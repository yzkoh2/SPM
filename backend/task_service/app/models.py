from flask_sqlalchemy import SQLAlchemy
import enum
from datetime import datetime

db = SQLAlchemy()

# --- ENUMS ---

class TaskStatusEnum(enum.Enum):
    """Enumeration for task statuses to ensure consistency."""
    UNASSIGNED = 'Unassigned'
    ONGOING = 'Ongoing'
    UNDER_REVIEW = 'Under Review'
    COMPLETED = 'Completed'


# --- Junction Tables (store only IDs) ---

project_collaborators = db.Table(
    'project_collaborators',
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('user_id', db.Integer, primary_key=True)  # just store user IDs
)

task_collaborators = db.Table(
    'task_collaborators',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('user_id', db.Integer, primary_key=True)  # just store user IDs
)

comment_mentions = db.Table(
    'comment_mentions',
    db.Column('comment_id', db.Integer, db.ForeignKey('comments.id'), primary_key=True),
    db.Column('user_id', db.Integer, primary_key=True)  # just store user IDs
)

# --- MAIN MODELS ---

class Project(db.Model):
    """Represents a project, which is a container for tasks."""
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    owner_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relationship to tasks in this project
    tasks = db.relationship('Task', back_populates='project', cascade="all, delete-orphan")

    # Helper method to get collaborator IDs
    def collaborator_ids(self):
        result = db.session.execute(
            project_collaborators.select().where(project_collaborators.c.project_id == self.id)
        )
        return [row.user_id for row in result]

    def get_task(self):
        result = db.session.execute(
            db.select(Task).where(Task.project_id == self.id)
        )
        return [row.Task for row in result]

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'owner_id': self.owner_id,
            'collaborator_ids': self.collaborator_ids(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'tasks': [task.to_json() for task in self.tasks]
        }

class TaskActivityLog(db.Model):
    """
    Records a log of all changes to task details (title, status, priority, etc.)
    """
    __tablename__ = 'task_activity_log'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now(), index=True)
    field_changed = db.Column(db.String(50), nullable=False)
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)

    # Relationships
    task = db.relationship('Task', back_populates='activity_logs')

    def __repr__(self):
        return f'<TaskActivityLog {self.id}: {self.field_changed} on Task {self.task_id}>'

class Task(db.Model):
    """
    Represents a single task or subtask.
    Subtasks are modeled with a self-referencing foreign key.
    """
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum(TaskStatusEnum), nullable=False, default=TaskStatusEnum.UNASSIGNED)
    owner_id = db.Column(db.Integer, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    parent_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    priority = db.Column(db.Integer, nullable=True)  

    # Task Recurrance
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_interval = db.Column(db.String(50), nullable=True) 
    recurrence_days = db.Column(db.Integer, nullable=True) #
    recurrence_end_date = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relationships
    activity_logs = db.relationship('TaskActivityLog', back_populates='task', lazy='dynamic', cascade="all, delete-orphan")
    project = db.relationship('Project', back_populates='tasks')
    subtasks = db.relationship(
        'Task', backref=db.backref('parent_task', remote_side=[id]), cascade="all, delete-orphan"
    )
    attachments = db.relationship('Attachment', backref='task', cascade="all, delete-orphan")
    comments = db.relationship('Comment', backref='task', cascade="all, delete-orphan")

    # Helper method to get collaborator IDs
    def collaborator_ids(self):
        result = db.session.execute(
            task_collaborators.select().where(task_collaborators.c.task_id == self.id)
        )
        return [row.user_id for row in result]

    def to_json(self):
        # Filter comments to only include top-level (no parent_comment_id)
        top_level_comments = [c for c in self.comments if c.parent_comment_id is None]
        
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'owner_id': self.owner_id,
            'project_id': self.project_id,
            'parent_task_id': self.parent_task_id,
            'priority': self.priority,
            'is_recurring': self.is_recurring,
            'recurrence_interval': self.recurrence_interval,
            'recurrence_days': self.recurrence_days,
            'recurrence_end_date': self.recurrence_end_date.isoformat() if self.recurrence_end_date else None,
            'collaborator_ids': self.collaborator_ids(),
            'subtasks': [subtask.to_json() for subtask in self.subtasks],
            'subtask_count': len(self.subtasks),
            'comments': [comment.to_json() for comment in top_level_comments],  # Only top-level
            'comment_count': len(self.comments),  # Still count all comments
            'attachments': [attachment.to_json() for attachment in self.attachments],
            'attachment_count': len(self.attachments),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class Attachment(db.Model):
    """Represents a file attachment linked to a task."""
    __tablename__ = 'attachments'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)

    def to_json(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'url': self.url,
        }

class Comment(db.Model):
    """Represents a comment made on a task."""
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)

    replies = db.relationship(
        "Comment",
        back_populates="parent",
        cascade="all, delete-orphan" # Ensures replies are deleted with the parent
    )

    # This creates a 'parent' attribute, linking a reply back to its parent comment.
    parent = db.relationship(
        "Comment",
        back_populates="replies",
        remote_side=[id]
    )

    def get_mentions(self):
        result = db.session.execute(
            comment_mentions.select().where(comment_mentions.c.comment_id == self.id)
        )
        return [row.user_id for row in result]

    def to_json(self):
        """Serialize the object to a dictionary."""
        return {
            'id': self.id,
            'body': self.body,
            'author_id': self.author_id,
            'task_id': self.task_id,
            'created_at': self.created_at.isoformat(),
            'parent_comment_id': self.parent_comment_id,
            'replies': [reply.to_json() for reply in self.replies],
            'reply_count': len(self.replies),
            'mentions': self.get_mentions()
        }
    
class ReportHistory(db.Model):
    """Represents a file attachment linked to a task."""
    __tablename__ = 'report_history'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    target_user_id = db.Column(db.Integer, nullable=True)
    report_type = db.Column(db.String(100), nullable=False)
    project_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_json(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'url': self.url,
            'user_id': self.user_id,
            'target_user_id': self.target_user_id,
            'report_type': self.report_type,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat(),
        }