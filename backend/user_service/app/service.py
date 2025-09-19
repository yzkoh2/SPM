# app/services.py
from .models import db, User
from flask import current_app
import jwt
import datetime

def get_user_by_id(user_id):
    """Fetches a single user by their ID."""
    return User.query.get(user_id)
    

def get_user_by_email(email):
    return User.query.get(email)


def create_user(data):
    """Creates a new user."""
    new_user = User(
        username=data['username'],
        password=data['password'],
        email=data['email'],
        role=data.get('role', 'staff')
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user

def login_user(data):
    """
    Finds a user by email and verifies their password.
    In a real app, you would hash and compare passwords here.
    """
    user = User.query.filter_by(email=data['email']).first()
    if user and user.password == data['password']:
        return user
    return None

def generate_token(user_id):
    """Generates a JWT Token signed with the app's SECRET_KEY."""
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1), # Token expires in 1 day
            'iat': datetime.datetime.utcnow(), # Issued at time
            'sub': user_id # Subject (the user's ID)
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return str(e)