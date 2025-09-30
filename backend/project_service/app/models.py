from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association tables
project_tasks = db.Table(
    "project_tasks",
    db.Column("project_id", db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    db.Column("task_id", db.Integer, primary_key=True)  # external Task ID
)

project_collaborators = db.Table(
    "project_collaborators",
    db.Column("project_id", db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    db.Column("user_id", db.Integer, primary_key=True),  # external User ID
    db.Column("role", db.String(50))
)

class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, nullable=False)     # user ID from User DB
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    # These are lightweight; you can still join with other services via APIs
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

# Optional models for richer ORM access (they wrap the link tables)
class ProjectTaskLink(db.Model):
    __tablename__ = "project_tasks"

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    task_id = db.Column(db.Integer, primary_key=True)  # external Task ID

    project = db.relationship("Project", back_populates="tasks")

class ProjectCollaboratorLink(db.Model):
    __tablename__ = "project_collaborators"

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)   # external User ID
    role = db.Column(db.String(50))

    project = db.relationship("Project", back_populates="collaborators")
