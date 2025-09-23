from .models import db, Task, Subtask, Comment, Attachment
from datetime import datetime
import requests
import os

def get_all_tasks(owner_id=None, status=None):
    """Fetch all tasks with optional filtering - primarily for dashboard view"""
    query = Task.query
    
    # If owner_id is provided, filter tasks for that specific user
    if owner_id:
        query = query.filter_by(owner_id=owner_id)
    
    if status:
        query = query.filter_by(status=status)
    
    tasks = query.all()
    
    return [{
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "deadline": task.deadline.isoformat() if task.deadline else None,
        "status": task.status,
        "owner_id": task.owner_id,
        "subtask_count": len(task.subtasks),
        "comment_count": len(task.comments),
        "attachment_count": len(task.attachments)
    } for task in tasks]

def get_task_details(task_id):
    """Fetch complete task details for individual task page"""
    task = Task.query.filter_by(id=task_id).first()
    if not task:
        return None

    # Get owner details from user service
    owner_details = get_user_details(task.owner_id)
    
    # Get collaborator details for comments
    comment_authors = set(comment.author_id for comment in task.comments)
    collaborators = []
    for author_id in comment_authors:
        user_details = get_user_details(author_id)
        if user_details and user_details not in collaborators:
            collaborators.append(user_details)

    # Always include the task owner in collaborators if not already there
    if owner_details and owner_details not in collaborators:
        collaborators.append(owner_details)

    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "deadline": task.deadline.isoformat() if task.deadline else None,
        "status": task.status,
        "owner_id": task.owner_id,
        "owner_details": owner_details,
        "collaborators": collaborators,
        "subtasks": [{
            "id": s.id, 
            "title": s.title, 
            "status": s.status,
            "created_at": s.created_at.isoformat() if hasattr(s, 'created_at') and s.created_at else None
        } for s in task.subtasks],
        "comments": [{
            "id": c.id, 
            "body": c.body, 
            "author_id": c.author_id,
            "author_details": get_user_details(c.author_id),
            "created_at": c.created_at.isoformat() if hasattr(c, 'created_at') and c.created_at else None
        } for c in task.comments],
        "attachments": [{
            "id": a.id, 
            "filename": a.filename, 
            "url": a.url,
            "size": getattr(a, 'size', None),
            "uploaded_at": a.uploaded_at.isoformat() if hasattr(a, 'uploaded_at') and a.uploaded_at else None
        } for a in task.attachments]
    }

def get_user_details(user_id):
    """Fetch user details from user service via Kong gateway"""
    try:
        # Try to use Kong gateway first, fall back to direct service URL if needed
        kong_url = os.getenv('KONG_URL', 'http://kong:8000')
        
        # For development, you might need to use localhost instead
        if 'localhost' in kong_url or '127.0.0.1' in kong_url:
            kong_url = 'http://localhost:8000'
        
        response = requests.get(f"{kong_url}/user/{user_id}", timeout=5)
        
        if response.status_code == 200:
            user_data = response.json()
            return {
                "id": user_id,
                "username": user_data.get("username", "Unknown"),
                "email": user_data.get("email", "Unknown"),
                "role": user_data.get("role", "Unknown")
            }
        else:
            print(f"Failed to fetch user {user_id}: HTTP {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching user details for user {user_id}: {e}")
    except Exception as e:
        print(f"Error fetching user details for user {user_id}: {e}")
    
    # Return default values if API call fails
    return {
        "id": user_id, 
        "username": f"User_{user_id}",
        "email": "Unknown", 
        "role": "Unknown"
    }