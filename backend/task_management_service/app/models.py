from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Task(db.Model):
    """Task model with ownership transfer logic and subtask support"""
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), 
                      db.CheckConstraint("status IN ('unassigned', 'ongoing', 'under_review', 'completed')"),
                      default='unassigned')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=False)  # Original creator (never changes)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, nullable=True)   # Last person to update
    owner_id = db.Column(db.Integer, nullable=False)    # Current owner (changes on reassignment)
    assigned_to = db.Column(db.Integer, nullable=True)  # Current assignee (can be null)

    # Relationships
    subtasks = db.relationship("Subtask", backref="parent_task", lazy=True, cascade="all, delete-orphan", order_by="Subtask.order_index")
    comments = db.relationship("Comment", backref="task", lazy=True, cascade="all, delete-orphan", 
                              primaryjoin="Task.id == Comment.task_id")
    attachments = db.relationship("Attachment", backref="task", lazy=True, cascade="all, delete-orphan",
                                 primaryjoin="Task.id == Attachment.task_id")
    collaborators = db.relationship("TaskCollaborator", backref="task", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Task {self.id}: {self.title}>'

    def is_unassigned(self):
        """Check if task is unassigned"""
        return self.assigned_to is None

    def is_owned_by(self, user_id):
        """Check if task is owned by specific user"""
        return self.owner_id == user_id

    def is_assigned_to(self, user_id):
        """Check if task is assigned to specific user"""
        return self.assigned_to == user_id

    def get_completion_percentage(self):
        """Calculate completion percentage based on subtasks"""
        if not self.subtasks:
            return 0
        
        completed_subtasks = sum(1 for subtask in self.subtasks if subtask.status == 'completed')
        return round((completed_subtasks / len(self.subtasks)) * 100, 1)

    def get_subtask_status_summary(self):
        """Get summary of subtask statuses"""
        if not self.subtasks:
            return {}
        
        status_count = {}
        for subtask in self.subtasks:
            status_count[subtask.status] = status_count.get(subtask.status, 0) + 1
        
        return status_count

    def assign_to_user(self, user_id, updated_by_user_id=None):
        """
        Assign task to a user and transfer ownership
        
        Args:
            user_id (int): User to assign task to
            updated_by_user_id (int): User making the assignment
        """
        self.assigned_to = user_id
        self.owner_id = user_id  # Ownership transfers on assignment
        if updated_by_user_id:
            self.updated_by = updated_by_user_id
        
        # Update status if currently unassigned
        if self.status == 'unassigned':
            self.status = 'ongoing'

    def unassign_task(self, updated_by_user_id=None):
        """
        Unassign task (remove assignee but keep owner)
        
        Args:
            updated_by_user_id (int): User making the change
        """
        self.assigned_to = None
        if updated_by_user_id:
            self.updated_by = updated_by_user_id
        
        # Update status if appropriate
        if self.status == 'ongoing':
            self.status = 'unassigned'

    def to_dict(self):
        """Convert task to dictionary for API responses"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "updated_by": self.updated_by,
            "owner_id": self.owner_id,
            "assigned_to": self.assigned_to,
            "is_unassigned": self.is_unassigned(),
            "subtask_count": len(self.subtasks),
            "comment_count": len(self.comments),
            "attachment_count": len(self.attachments),
            "collaborator_count": len(self.collaborators),
            "completion_percentage": self.get_completion_percentage(),
            "subtask_status_summary": self.get_subtask_status_summary()
        }

    def to_detailed_dict(self):
        """Convert task to detailed dictionary including related entities"""
        base_dict = self.to_dict()
        base_dict.update({
            "subtasks": [subtask.to_dict() for subtask in self.subtasks],
            "comments": [comment.to_dict() for comment in self.comments],
            "attachments": [attachment.to_dict() for attachment in self.attachments],
            "collaborators": [collaborator.to_dict() for collaborator in self.collaborators]
        })
        return base_dict


class Subtask(db.Model):
    """Subtask model representing individual task components"""
    __tablename__ = "subtasks"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20),
                      db.CheckConstraint("status IN ('unassigned', 'ongoing', 'under_review', 'completed')"),
                      default='unassigned')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=False)  # User ID from user service
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, nullable=True)   # User ID from user service
    assigned_to = db.Column(db.Integer, nullable=True)  # User ID from user service
    order_index = db.Column(db.Integer, default=0)     # For ordering subtasks

    # Relationships
    comments = db.relationship("Comment", backref="subtask", lazy=True, cascade="all, delete-orphan",
                              primaryjoin="Subtask.id == Comment.subtask_id")
    attachments = db.relationship("Attachment", backref="subtask", lazy=True, cascade="all, delete-orphan",
                                 primaryjoin="Subtask.id == Attachment.subtask_id")

    def __repr__(self):
        return f'<Subtask {self.id}: {self.title} (Task {self.task_id})>'

    def is_assigned_to(self, user_id):
        """Check if subtask is assigned to specific user"""
        return self.assigned_to == user_id

    def is_completed(self):
        """Check if subtask is completed"""
        return self.status == 'completed'

    def assign_to_user(self, user_id, updated_by_user_id=None):
        """
        Assign subtask to a user
        
        Args:
            user_id (int): User to assign subtask to
            updated_by_user_id (int): User making the assignment
        """
        self.assigned_to = user_id
        if updated_by_user_id:
            self.updated_by = updated_by_user_id
        
        # Update status if currently unassigned
        if self.status == 'unassigned':
            self.status = 'ongoing'

    def mark_completed(self, updated_by_user_id=None):
        """
        Mark subtask as completed
        
        Args:
            updated_by_user_id (int): User marking as complete
        """
        self.status = 'completed'
        if updated_by_user_id:
            self.updated_by = updated_by_user_id

    def to_dict(self):
        """Convert subtask to dictionary for API responses"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "updated_by": self.updated_by,
            "assigned_to": self.assigned_to,
            "order_index": self.order_index,
            "is_completed": self.is_completed(),
            "comment_count": len(self.comments),
            "attachment_count": len(self.attachments)
        }

    def to_detailed_dict(self):
        """Convert subtask to detailed dictionary including related entities"""
        base_dict = self.to_dict()
        base_dict.update({
            "comments": [comment.to_dict() for comment in self.comments],
            "attachments": [attachment.to_dict() for attachment in self.attachments]
        })
        return base_dict


class TaskCollaborator(db.Model):
    """Junction table for task collaborators (many-to-many relationship)"""
    __tablename__ = "task_collaborators"

    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)  # User ID from user service
    role = db.Column(db.String(50), default='collaborator')
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    added_by = db.Column(db.Integer, nullable=True)    # User ID from user service

    def __repr__(self):
        return f'<TaskCollaborator task_id={self.task_id}, user_id={self.user_id}>'

    def to_dict(self):
        """Convert collaborator to dictionary for API responses"""
        return {
            "task_id": self.task_id,
            "user_id": self.user_id,
            "role": self.role,
            "added_at": self.added_at.isoformat() if self.added_at else None,
            "added_by": self.added_by
        }


class Comment(db.Model):
    """Comment model supporting both tasks and subtasks"""
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=True)      # Can be null if on subtask
    subtask_id = db.Column(db.Integer, db.ForeignKey("subtasks.id"), nullable=True)  # Can be null if on task
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=False)  # User ID from user service
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, nullable=True)   # User ID from user service

    def __repr__(self):
        if self.task_id:
            return f'<Comment {self.id} for Task {self.task_id}>'
        else:
            return f'<Comment {self.id} for Subtask {self.subtask_id}>'

    def get_parent_type(self):
        """Get whether this comment is on a task or subtask"""
        return 'task' if self.task_id else 'subtask'

    def get_parent_id(self):
        """Get the ID of the parent (task or subtask)"""
        return self.task_id if self.task_id else self.subtask_id

    def to_dict(self):
        """Convert comment to dictionary for API responses"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "subtask_id": self.subtask_id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "updated_by": self.updated_by,
            "parent_type": self.get_parent_type(),
            "parent_id": self.get_parent_id()
        }


class Attachment(db.Model):
    """Attachment model supporting both tasks and subtasks"""
    __tablename__ = "attachments"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=True)      # Can be null if on subtask
    subtask_id = db.Column(db.Integer, db.ForeignKey("subtasks.id"), nullable=True)  # Can be null if on task
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    mime_type = db.Column(db.String(100), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, nullable=False)  # User ID from user service

    def __repr__(self):
        if self.task_id:
            return f'<Attachment {self.id}: {self.file_name} (Task {self.task_id})>'
        else:
            return f'<Attachment {self.id}: {self.file_name} (Subtask {self.subtask_id})>'

    def get_parent_type(self):
        """Get whether this attachment is on a task or subtask"""
        return 'task' if self.task_id else 'subtask'

    def get_parent_id(self):
        """Get the ID of the parent (task or subtask)"""
        return self.task_id if self.task_id else self.subtask_id

    def to_dict(self):
        """Convert attachment to dictionary for API responses"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "subtask_id": self.subtask_id,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "uploaded_by": self.uploaded_by,
            "parent_type": self.get_parent_type(),
            "parent_id": self.get_parent_id()
        }