from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default="Unassigned") 
    owner_id = db.Column(db.Integer, nullable=False)  

    # Relationships
    subtasks = db.relationship("Subtask", backref="parent_task", lazy=True)
    comments = db.relationship("Comment", backref="task", lazy=True)
    attachments = db.relationship("Attachment", backref="task", lazy=True)

class Subtask(db.Model):
    __tablename__ = "subtasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)  
    deadline = db.Column(db.DateTime, nullable=True)  
    status = db.Column(db.String(50), default="Unassigned")
    assignee_id = db.Column(db.Integer, nullable=True) 
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)

class TaskCollaborator(db.Model):
    __tablename__ = "task_collaborators"
    
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    added_at = db.Column(db.DateTime, default=lambda: datetime.now())
    role = db.Column(db.String(50), default="collaborator")

class SubtaskCollaborator(db.Model):
    __tablename__ = "subtask_collaborators"
    
    subtask_id = db.Column(db.Integer, db.ForeignKey("subtasks.id"), primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    added_at = db.Column(db.DateTime, default=lambda: datetime.now())
    role = db.Column(db.String(50), default="collaborator")

class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, nullable=False)  
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)

class Attachment(db.Model):
    __tablename__ = "attachments"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
