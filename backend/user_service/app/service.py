# app/services.py
from .models import db, User

def get_user_by_id(user_id):
    """Fetches a single user by their ID."""
    user = User.query.get(user_id)
    return user

def create_user(data):
    """Creates a new user."""
    new_user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'staff')
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user