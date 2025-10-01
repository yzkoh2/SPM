from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, nullable=False)  # user ID from User DB
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    tasks = db.relationship(
        "ProjectTaskLink",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    collaborators = db.relationship(
        "ProjectCollaboratorLink",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        """Convert project to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ProjectTaskLink(db.Model):
    __tablename__ = "project_tasks"

    project_id = db.Column(
        db.Integer, 
        db.ForeignKey("projects.id", ondelete="CASCADE"), 
        primary_key=True
    )
    task_id = db.Column(db.Integer, primary_key=True)  # external Task ID

    project = db.relationship("Project", back_populates="tasks")

    def to_dict(self):
        """Convert task link to dictionary"""
        return {
            'project_id': self.project_id,
            'task_id': self.task_id
        }


class ProjectCollaboratorLink(db.Model):
    __tablename__ = "project_collaborators"

    project_id = db.Column(
        db.Integer, 
        db.ForeignKey("projects.id", ondelete="CASCADE"), 
        primary_key=True
    )
    user_id = db.Column(db.Integer, primary_key=True)  # external User ID
    role = db.Column(db.String(50))

    project = db.relationship("Project", back_populates="collaborators")

    def to_dict(self):
        """Convert collaborator link to dictionary"""
        return {
            'project_id': self.project_id,
            'user_id': self.user_id,
            'role': self.role
        }