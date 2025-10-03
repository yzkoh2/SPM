from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()

class TaskStatusEnum(enum.Enum):
    """Enumeration for task statuses to ensure consistency."""
    UNASSIGNED = 'Unassigned'
    ONGOING = 'Ongoing'
    UNDER_REVIEW = 'Under Review'
    COMPLETED = 'Completed'

# --- Junction Tables for Many-to-Many Relationships ---

# Associates users with projects they are collaborating on.
project_collaborators = db.Table('project_collaborators',
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    # Note: user_id is just an integer. The actual user data lives in the User Service.
    db.Column('user_id', db.Integer, primary_key=True)
)

# Associates users with tasks they are collaborating on.
task_collaborators = db.Table('task_collaborators',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('user_id', db.Integer, primary_key=True)
)

# --- Main Models ---

class Project(db.Model):
    """Represents a project, which is a container for tasks."""
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    owner_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationship to tasks contained within this project
    tasks = db.relationship('Task', back_populates='project', cascade="all, delete-orphan")
    
    # Many-to-many relationship linking project IDs to user IDs
    collaborators = db.relationship('User', secondary=project_collaborators)

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'owner_id': self.owner_id,
            'collaborator_ids': [user.id for user in self.collaborators],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Attachment(db.Model):
    """Represents a file attachment linked to a task."""
    __tablename__ = 'attachments'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)

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

    # Relationships
    project = db.relationship('Project', back_populates='tasks')
    subtasks = db.relationship('Task', backref=db.backref('parent_task', remote_side=[id]), cascade="all, delete-orphan")
    collaborators = db.relationship('User', secondary=task_collaborators)
    attachments = db.relationship('Attachment', backref='task', cascade="all, delete-orphan")

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'owner_id': self.owner_id,
            'project_id': self.project_id,
            'parent_task_id': self.parent_task_id,
            'collaborator_ids': [user.id for user in self.collaborators],
        }

class User(db.Model):
    """
    Placeholder model for SQLAlchemy relationships.
    This does NOT create a 'users' table in the Task Service database.
    It's a necessary construct for the ORM to understand the many-to-many
    relationships defined in Project and Task models.
    """
    __tablename__ = 'users_placeholder'
    id = db.Column(db.Integer, primary_key=True)