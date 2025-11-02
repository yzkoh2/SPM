# app/services.py
from .models import db, User, Team, RoleEnum, Department
from flask import current_app
import jwt
import datetime


# Verification Methods (JWT and Login)
def login_user(data):
    """
    Finds a user by email and verifies their password.
    In a real app, you would hash and compare passwords here.
    """
    user = get_user_by_email(data.get('email'))
    password = data.get('password')
    if user and user.check_password(password):
        return generate_token(user.id), user.id, user.name, user.role.value, user.username
    return None, None, None, None, None

def generate_token(user_id):
    """Generates a JWT Token signed with the app's SECRET_KEY."""
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1), # Token expires in 1 day
            'iat': datetime.datetime.utcnow(), # Issued at time
            'sub': str(user_id) # Subject (the user's ID)
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256")
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token
    except Exception as e:
        return str(e)
#############################################################################################################


# GET Methods
def get_user_by_id(user_id):
    """Fetches a single user by their ID."""
    return User.query.get(user_id)

def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def get_all_users():
    """Get all users from the database"""
    return User.query.all()

def get_all_teams():
    """Get all teams from the database"""
    return Team.query.all()

def get_all_users_in_team(team_id):
    """Get all users in a specific team"""
    return User.query.filter_by(team_id=team_id).all()

def get_all_dept():
    """Get all departments from the database"""
    return Department.query.all()

def get_all_users_in_dept(dept_id):
    """Get all users in a specific department"""
    return User.query.join(Team).filter(Team.department_id == dept_id).all()
#############################################################################################################


# POST Methods
def create_user(data):
    """Creates a new user."""

    if get_user_by_email(data['email']):
        return None, "Email already in use."
    if get_user_by_username(data['username']):
        return None, "Username already taken."
    
    team = Team.query.get(data.get('team_id'))
    if not team:
        return None, f"Team with id {data['team_id']} not found."

    role_str = data.get('role')
    if role_str:
        try:
            role = RoleEnum(role_str.capitalize())
        except ValueError:
            return None, f"Invalid role: {role_str}. Must be one of {[role.value for role in RoleEnum]}."
    else:
        role = RoleEnum.STAFF  # fallback to default

    new_user = User(
        username=data['username'],
        name=data['name'],
        email=data['email'],
        role=role,
        team_id=data['team_id']
    )

    new_user.set_password(data['password'])

    db.session.add(new_user)
    db.session.commit()

    return new_user, None
#############################################################################################################