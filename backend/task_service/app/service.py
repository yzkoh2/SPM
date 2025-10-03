from .models import db, Project, Task, Attachment, TaskStatusEnum, project_collaborators, task_collaborators
from sqlalchemy import or_
from sqlalchemy.orm import aliased
from datetime import datetime

def get_all_tasks(user_id):
    if not user_id:
        return []

    # Alias for subtasks
    SubTask = aliased(Task)

    # Step 1: find parent_task_ids where user is a collaborator on a subtask
    subtask_collab_query = db.session.query(SubTask.parent_task_id)\
        .join(task_collaborators, task_collaborators.c.task_id == SubTask.id)\
        .filter(task_collaborators.c.user_id == user_id)\
        .filter(SubTask.parent_task_id.isnot(None))\
        .distinct()

    # Step 2: main query for parent tasks
    tasks_query = db.session.query(Task)\
        .filter(Task.parent_task_id.is_(None))\
        .filter(
            or_(
                Task.owner_id == user_id,  # owner
                db.session.query(task_collaborators)
                  .filter(task_collaborators.c.task_id == Task.id)
                  .filter(task_collaborators.c.user_id == user_id)
                  .exists(),  # direct collaborator
                Task.id.in_(subtask_collab_query)  # collaborator on subtasks
            )
        ).distinct()

    return tasks_query.all()

def create_task(task_data):
    """Create a new task"""
    try:
        print(f"Creating task with data: {task_data}")
        
        # Parse deadline if provided
        deadline = None
        if task_data.get('deadline'):
            try:
                if isinstance(task_data['deadline'], str) and task_data['deadline'].strip():
                    # Handle datetime-local format from HTML input
                    deadline_str = task_data['deadline']
                    if 'T' in deadline_str:
                        deadline = datetime.fromisoformat(deadline_str)
                    else:
                        deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
                elif isinstance(task_data['deadline'], datetime):
                    deadline = task_data['deadline']
            except ValueError as e:
                print(f"Error parsing deadline: {e}")
                deadline = None
        
        # Create new task
        new_task = Task(
            title=task_data['title'],
            description=task_data.get('description'),
            deadline=deadline,
            status=task_data.get('status', 'Unassigned'),
            owner_id=task_data['owner_id']
        )
        
        # Add to database
        db.session.add(new_task)
        db.session.commit()
        
        print(f"Task created with ID: {new_task.id}")
        
        # Return the created task
        return {
            "id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "deadline": str(new_task.deadline) if new_task.deadline else None,
            "status": new_task.status,
            "owner_id": new_task.owner_id,
            "subtask_count": 0,
            "comment_count": 0,
            "attachment_count": 0
        }
        
    except Exception as e:
        print(f"Error in create_task: {e}")
        db.session.rollback()
        raise e

def update_task(task_id, task_data):
    """Update an existing task"""
    try:
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return None
        
        # Update fields if provided
        if 'title' in task_data:
            task.title = task_data['title']
        if 'description' in task_data:
            task.description = task_data['description']
        if 'status' in task_data:
            task.status = task_data['status']
        if 'deadline' in task_data:
            if task_data['deadline']:
                try:
                    if isinstance(task_data['deadline'], str):
                        task.deadline = datetime.fromisoformat(task_data['deadline'])
                    else:
                        task.deadline = task_data['deadline']
                except ValueError:
                    task.deadline = None
            else:
                task.deadline = None
        
        db.session.commit()
        
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "deadline": str(task.deadline) if task.deadline else None,
            "status": task.status,
            "owner_id": task.owner_id,
            "subtask_count": len(task.subtasks),
            "comment_count": len(task.comments),
            "attachment_count": len(task.attachments)
        }
        
    except Exception as e:
        print(f"Error in update_task: {e}")
        db.session.rollback()
        raise e

def delete_task(task_id):
    """Delete a task by ID"""
    try:
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return False
            
        print(f"Deleting task: {task.title}")
        db.session.delete(task)
        db.session.commit()
        return True
        
    except Exception as e:
        print(f"Error in delete_task: {e}")
        db.session.rollback()
        raise e

def get_task_details(task_id):
    """Fetch a task with its subtasks, comments, and attachments"""
    try:
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
        
    except Exception as e:
        print(f"Error in get_task_details: {e}")
        raise e

def get_task_subtasks(task_id):
    """Fetch all subtasks for a specific task"""
    try:
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return None
        
        return [{
            "id": subtask.id,
            "title": subtask.title,
            "status": subtask.status,
            "task_id": subtask.task_id
        } for subtask in task.subtasks]
        
    except Exception as e:
        print(f"Error in get_task_subtasks: {e}")
        raise e

def create_subtask(task_id, subtask_data):
    """Create a new subtask for a task"""
    try:
        # Check if parent task exists
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return None
        
        # Create new subtask
        new_subtask = Subtask(
            title=subtask_data['title'],
            status=subtask_data.get('status', 'Unassigned'),
            task_id=task_id
        )
        
        db.session.add(new_subtask)
        db.session.commit()
        
        return {
            "id": new_subtask.id,
            "title": new_subtask.title,
            "status": new_subtask.status,
            "task_id": new_subtask.task_id
        }
        
    except Exception as e:
        print(f"Error in create_subtask: {e}")
        db.session.rollback()
        raise e

def get_subtask_details(task_id, subtask_id):
    """Fetch a specific subtask"""
    try:
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
        
    except Exception as e:
        print(f"Error in get_subtask_details: {e}")
        raise e