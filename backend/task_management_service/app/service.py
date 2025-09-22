from .models import db, Task, Subtask, Comment, Attachment
from datetime import datetime

def get_all_tasks(owner_id=None, status=None):
    """Fetch all tasks with optional filtering"""
    query = Task.query
    
    if owner_id:
        query = query.filter_by(owner_id=owner_id)
    
    if status:
        query = query.filter_by(status=status)
    
    tasks = query.all()
    
    return [{
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "deadline": str(task.deadline) if task.deadline else None,
        "status": task.status,
        "owner_id": task.owner_id,
        "subtask_count": len(task.subtasks),
        "comment_count": len(task.comments),
        "attachment_count": len(task.attachments)
    } for task in tasks]

def get_task_details(task_id):
    """Fetch a task with its subtasks, comments, and attachments"""
    task = Task.query.filter_by(id=task_id).first()
    if not task:
        return None

    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "deadline": str(task.deadline) if task.deadline else None,
        "status": task.status,
        "owner_id": task.owner_id,
        "subtasks": [{"id": s.id, "title": s.title, "status": s.status} for s in task.subtasks],
        "comments": [{"id": c.id, "body": c.body, "author_id": c.author_id} for c in task.comments],
        "attachments": [{"id": a.id, "filename": a.filename, "url": a.url} for a in task.attachments]
    }

def get_task_subtasks(task_id):
    """Fetch all subtasks for a specific task"""
    task = Task.query.filter_by(id=task_id).first()
    if not task:
        return None
    
    return [{
        "id": subtask.id,
        "title": subtask.title,
        "status": subtask.status,
        "task_id": subtask.task_id
    } for subtask in task.subtasks]

def get_subtask_details(task_id, subtask_id):
    """Fetch a specific subtask"""
    subtask = Subtask.query.filter_by(id=subtask_id, task_id=task_id).first()
    if not subtask:
        return None
    
    return {
        "id": subtask.id,
        "title": subtask.title,
        "status": subtask.status,
        "task_id": subtask.task_id,
        "parent_task": {
            "id": subtask.parent_task.id,
            "title": subtask.parent_task.title,
            "status": subtask.parent_task.status
        }
    }