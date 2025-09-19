from .models import db, Task

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
