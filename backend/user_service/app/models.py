# app/models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import enum

db = SQLAlchemy()

class RoleEnum(enum.Enum):
    """Enumeration for user roles to ensure consistency."""
    STAFF = 'Staff'
    MANAGER = 'Manager'
    DIRECTOR = 'Director'
    HR = 'HR'
    SM = 'SM'

class User(db.Model):
    """User in a system."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.Enum(RoleEnum), nullable=False, default=RoleEnum.STAFF)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)

    # Relationships
    team = db.relationship('Team', back_populates='members')

    def set_password(self, password):
        """Creates a hashed password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies a password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.name} ({self.email})>'

    # Methods
    
    def to_json(self):
        return {
            # 'username': self.username,
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'role': self.role.value,
            'team_id': self.team_id  
        }

class Team(db.Model):
    """Team in a company."""
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    # Relationships
    department = db.relationship('Department', back_populates='teams')
    members = db.relationship('User', back_populates='team')

    def __repr__(self):
        return f'<Team {self.name}>'
    
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'department_id': self.department_id
        }

class Department(db.Model):
    """Department in a company."""
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    # Relationships
    teams = db.relationship('Team', back_populates='department', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Department {self.name}>'

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name
        }