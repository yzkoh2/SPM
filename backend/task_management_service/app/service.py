from .models import db, Task, Subtask, Comment, Attachment, TaskCollaborator, SubtaskCollaborator
from datetime import datetime

def get_all_tasks(owner_id=None, status=None):
    #Retrieve all tasks with optional filters
    try:
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
        
    except Exception as e:
        print(f"Error in get_all_tasks: {e}")
        raise e

def get_task_details(task_id):
    #Get detailed task information
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
            "subtasks": [{
                "id": s.id,
                "title": s.title,
                "status": s.status,
                "assignee_id": s.assignee_id
            } for s in task.subtasks],
            "comments": [{
                "id": c.id,
                "body": c.body,
                "author_id": c.author_id
            } for c in task.comments],
            "attachments": [{
                "id": a.id,
                "filename": a.filename,
                "url": a.url
            } for a in task.attachments],
            "collaborators": [{
                "user_id": collab.user_id,
                "role": collab.role,
                "added_at": str(collab.added_at) if collab.added_at else None
            } for collab in task.collaborators]
        }
        
    except Exception as e:
        print(f"Error in get_task_details: {e}")
        raise e

def create_task(task_data):
    #Create a new task
    try:
        new_task = Task(
            title=task_data['title'],
            description=task_data.get('description'),
            deadline=task_data.get('deadline'),
            status=task_data.get('status', 'Unassigned'),
            owner_id=task_data['owner_id']
        )
        
        db.session.add(new_task)
        db.session.commit()
        
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
    #Update an existing task
    try:
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return None
        
        print(f"Updating task {task_id} with data: {task_data}")
        
        # Update fields if provided
        if 'title' in task_data:
            task.title = task_data['title']
        if 'description' in task_data:
            task.description = task_data['description']
        if 'owner_id' in task_data:
            task.owner_id = task_data['owner_id']
        if 'deadline' in task_data:
            if task_data['deadline']:
                try:
                    if isinstance(task_data['deadline'], str):
                        deadline_str = task_data['deadline']
                        if 'T' in deadline_str:
                            task.deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                        else:
                            task.deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
                    else:
                        task.deadline = task_data['deadline']
                except ValueError as e:
                    print(f"Error parsing deadline: {e}")
                    task.deadline = None
            else:
                task.deadline = None
        
        db.session.commit()
        
        print(f"Task {task_id} updated successfully")
        
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "deadline": str(task.deadline) if task.deadline else None,
            "status": task.status,
            "owner_id": task.owner_id,
            "subtask_count": len(task.subtasks),
            "comment_count": len(task.comments),
            "attachment_count": len(task.attachments),
            "collaborators": [{
                "user_id": collab.user_id,
                "role": collab.role
            } for collab in task.collaborators]
        }
        
    except Exception as e:
        print(f"Error in update_task: {e}")
        db.session.rollback()
        raise e

def delete_task(task_id):
    #Delete a task
    try:
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return False
        
        db.session.delete(task)
        db.session.commit()
        return True
        
    except Exception as e:
        print(f"Error in delete_task: {e}")
        db.session.rollback()
        raise e

# ============= SUBTASK OPERATIONS =============

def get_task_subtasks(task_id):
    #Get all subtasks for a task
    try:
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return None
        
        return [{
            "id": subtask.id,
            "title": subtask.title,
            "description": subtask.description,
            "deadline": str(subtask.deadline) if subtask.deadline else None,
            "status": subtask.status,
            "assignee_id": subtask.assignee_id,
            "task_id": subtask.task_id
        } for subtask in task.subtasks]
        
    except Exception as e:
        print(f"Error in get_task_subtasks: {e}")
        raise e

def create_subtask(task_id, subtask_data):
    #Create a new subtask
    try:
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return None
        
        new_subtask = Subtask(
            title=subtask_data['title'],
            description=subtask_data.get('description'),
            deadline=subtask_data.get('deadline'),
            status=subtask_data.get('status', 'Unassigned'),
            assignee_id=subtask_data.get('assignee_id'),
            task_id=task_id
        )
        
        db.session.add(new_subtask)
        db.session.commit()
        
        return {
            "id": new_subtask.id,
            "title": new_subtask.title,
            "description": new_subtask.description,
            "deadline": str(new_subtask.deadline) if new_subtask.deadline else None,
            "status": new_subtask.status,
            "assignee_id": new_subtask.assignee_id,
            "task_id": new_subtask.task_id
        }
        
    except Exception as e:
        print(f"Error in create_subtask: {e}")
        db.session.rollback()
        raise e

def get_subtask_details(task_id, subtask_id):
    #Get detailed subtask information
    try:
        subtask = Subtask.query.filter_by(id=subtask_id, task_id=task_id).first()
        if not subtask:
            return None
        
        return {
            "id": subtask.id,
            "title": subtask.title,
            "description": subtask.description,
            "deadline": str(subtask.deadline) if subtask.deadline else None,
            "status": subtask.status,
            "assignee_id": subtask.assignee_id,
            "task_id": subtask.task_id,
            "parent_task": {
                "id": subtask.parent_task.id,
                "title": subtask.parent_task.title,
                "status": subtask.parent_task.status,
                "owner_id": subtask.parent_task.owner_id
            },
            "collaborators": [{
                "user_id": collab.user_id,
                "role": collab.role,
                "added_at": str(collab.added_at) if collab.added_at else None
            } for collab in subtask.collaborators]
        }
        
    except Exception as e:
        print(f"Error in get_subtask_details: {e}")
        raise e

def update_subtask(task_id, subtask_id, subtask_data):
    #Update an existing subtask
    try:
        subtask = Subtask.query.filter_by(id=subtask_id, task_id=task_id).first()
        if not subtask:
            return None
        
        print(f"Updating subtask {subtask_id} with data: {subtask_data}")
        
        # Update fields if provided
        if 'title' in subtask_data:
            subtask.title = subtask_data['title']
        if 'description' in subtask_data:
            subtask.description = subtask_data['description']
        if 'assignee_id' in subtask_data:
            subtask.assignee_id = subtask_data['assignee_id']
        if 'deadline' in subtask_data:
            if subtask_data['deadline']:
                try:
                    if isinstance(subtask_data['deadline'], str):
                        deadline_str = subtask_data['deadline']
                        if 'T' in deadline_str:
                            subtask.deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                        else:
                            subtask.deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
                    else:
                        subtask.deadline = subtask_data['deadline']
                except ValueError as e:
                    print(f"Error parsing deadline: {e}")
                    subtask.deadline = None
            else:
                subtask.deadline = None
        
        db.session.commit()
        
        print(f"Subtask {subtask_id} updated successfully")
        
        return {
            "id": subtask.id,
            "title": subtask.title,
            "description": subtask.description,
            "deadline": str(subtask.deadline) if subtask.deadline else None,
            "status": subtask.status,
            "assignee_id": subtask.assignee_id,
            "task_id": subtask.task_id,
            "collaborators": [{
                "user_id": collab.user_id,
                "role": collab.role
            } for collab in subtask.collaborators]
        }
        
    except Exception as e:
        print(f"Error in update_subtask: {e}")
        db.session.rollback()
        raise e

def update_subtask_status(task_id, subtask_id, new_status):
    #Update only the subtask status
    try:
        subtask = Subtask.query.filter_by(id=subtask_id, task_id=task_id).first()
        if not subtask:
            return None
        
        subtask.status = new_status
        db.session.commit()
        
        return {
            "id": subtask.id,
            "title": subtask.title,
            "description": subtask.description,
            "deadline": str(subtask.deadline) if subtask.deadline else None,
            "status": subtask.status,
            "assignee_id": subtask.assignee_id,
            "task_id": subtask.task_id
        }
        
    except Exception as e:
        print(f"Error in update_subtask_status: {e}")
        db.session.rollback()
        raise e

# ============= COLLABORATOR OPERATIONS =============

# Legacy function names for backwards compatibility
def add_collaborator(task_id, collaborator_id):
    #Add a collaborator to a task (legacy name)
    return add_task_collaborator(task_id, collaborator_id)

def remove_collaborator(task_id, collaborator_id):
    #Remove a collaborator from a task (legacy name)
    return remove_task_collaborator(task_id, collaborator_id)

def add_task_collaborator(task_id, collaborator_id):
    #Add a collaborator to a task
    try:
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return False
        
        # Check if already a collaborator
        existing = TaskCollaborator.query.filter_by(
            task_id=task_id,
            user_id=collaborator_id
        ).first()
        
        if existing:
            return True  # Already a collaborator
        
        # Add new collaborator
        new_collaborator = TaskCollaborator(
            task_id=task_id,
            user_id=collaborator_id,
            role='collaborator'
        )
        
        db.session.add(new_collaborator)
        db.session.commit()
        
        print(f"Added collaborator {collaborator_id} to task {task_id}")
        return True
        
    except Exception as e:
        print(f"Error in add_task_collaborator: {e}")
        db.session.rollback()
        raise e

def remove_task_collaborator(task_id, collaborator_id):
    #Remove a collaborator from a task
    try:
        collaborator = TaskCollaborator.query.filter_by(
            task_id=task_id,
            user_id=collaborator_id
        ).first()
        
        if not collaborator:
            return False
        
        db.session.delete(collaborator)
        db.session.commit()
        
        print(f"Removed collaborator {collaborator_id} from task {task_id}")
        return True
        
    except Exception as e:
        print(f"Error in remove_task_collaborator: {e}")
        db.session.rollback()
        raise e

def get_task_collaborators(task_id):
    #Get all collaborators for a task
    try:
        collaborators = TaskCollaborator.query.filter_by(task_id=task_id).all()
        
        return [{
            "user_id": collab.user_id,
            "role": collab.role,
            "added_at": str(collab.added_at) if collab.added_at else None
        } for collab in collaborators]
        
    except Exception as e:
        print(f"Error in get_task_collaborators: {e}")
        raise e

def add_subtask_collaborator(subtask_id, collaborator_id):
    #Add a collaborator to a subtask
    try:
        subtask = Subtask.query.filter_by(id=subtask_id).first()
        if not subtask:
            return False
        
        # Check if already a collaborator
        existing = SubtaskCollaborator.query.filter_by(
            subtask_id=subtask_id,
            user_id=collaborator_id
        ).first()
        
        if existing:
            return True  # Already a collaborator
        
        # Add new collaborator
        new_collaborator = SubtaskCollaborator(
            subtask_id=subtask_id,
            user_id=collaborator_id,
            role='collaborator'
        )
        
        db.session.add(new_collaborator)
        db.session.commit()
        
        print(f"Added collaborator {collaborator_id} to subtask {subtask_id}")
        return True
        
    except Exception as e:
        print(f"Error in add_subtask_collaborator: {e}")
        db.session.rollback()
        raise e

def remove_subtask_collaborator(subtask_id, collaborator_id):
    #Remove a collaborator from a subtask
    try:
        collaborator = SubtaskCollaborator.query.filter_by(
            subtask_id=subtask_id,
            user_id=collaborator_id
        ).first()
        
        if not collaborator:
            return False
        
        db.session.delete(collaborator)
        db.session.commit()
        
        print(f"Removed collaborator {collaborator_id} from subtask {subtask_id}")
        return True
        
    except Exception as e:
        print(f"Error in remove_subtask_collaborator: {e}")
        db.session.rollback()
        raise e

def get_subtask_collaborators(subtask_id):
    #Get all collaborators for a subtask
    try:
        collaborators = SubtaskCollaborator.query.filter_by(subtask_id=subtask_id).all()
        
        return [{
            "user_id": collab.user_id,
            "role": collab.role,
            "added_at": str(collab.added_at) if collab.added_at else None
        } for collab in collaborators]
        
    except Exception as e:
        print(f"Error in get_subtask_collaborators: {e}")
        raise e

# ============= UTILITY FUNCTIONS =============

def is_task_collaborator(task_id, user_id):
    #Check if user is owner or collaborator of task
    try:
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return False
        
        # User is owner
        if task.owner_id == user_id:
            return True
        
        # Check if user is collaborator
        collaborator = TaskCollaborator.query.filter_by(
            task_id=task_id, 
            user_id=user_id
        ).first()
        
        return collaborator is not None
        
    except Exception as e:
        print(f"Error in is_task_collaborator: {e}")
        return False

def is_subtask_collaborator(subtask_id, user_id):
    #Check if user is assignee or collaborator of subtask
    try:
        subtask = Subtask.query.filter_by(id=subtask_id).first()
        if not subtask:
            return False
        
        # User is assignee
        if subtask.assignee_id == user_id:
            return True
        
        # Check if user is collaborator
        collaborator = SubtaskCollaborator.query.filter_by(
            subtask_id=subtask_id, 
            user_id=user_id
        ).first()
        
        return collaborator is not None
        
    except Exception as e:
        print(f"Error in is_subtask_collaborator: {e}")
        return False

def check_all_subtasks_completed(task_id):
    #Check if all subtasks are completed
    try:
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return False, 0
        
        subtasks = task.subtasks
        if not subtasks or len(subtasks) == 0:
            return True, 0
        
        incomplete_subtasks = [s for s in subtasks if s.status != 'Completed']
        
        return len(incomplete_subtasks) == 0, len(incomplete_subtasks)
        
    except Exception as e:
        print(f"Error in check_all_subtasks_completed: {e}")
        return False, 0

# ============= COMMENT OPERATIONS =============

def add_task_comment(task_id, author_id, comment_body):
    #Add a comment to a task
    try:
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return None
        
        new_comment = Comment(
            body=comment_body,
            author_id=author_id,
            task_id=task_id
        )
        
        db.session.add(new_comment)
        db.session.commit()
        
        return {
            "id": new_comment.id,
            "body": new_comment.body,
            "author_id": new_comment.author_id,
            "task_id": new_comment.task_id
        }
        
    except Exception as e:
        print(f"Error in add_task_comment: {e}")
        db.session.rollback()
        raise e

def get_task_comments(task_id):
    #Get all comments for a task
    try:
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return None
        
        return [{
            "id": comment.id,
            "body": comment.body,
            "author_id": comment.author_id,
            "task_id": comment.task_id
        } for comment in task.comments]
        
    except Exception as e:
        print(f"Error in get_task_comments: {e}")
        raise e

def add_subtask_comment(task_id, subtask_id, author_id, comment_body):
    #Add a comment to a subtask
    try:
        subtask = Subtask.query.filter_by(id=subtask_id, task_id=task_id).first()
        if not subtask:
            return None
        
        comment_with_ref = f"[Subtask #{subtask_id}: {subtask.title}] {comment_body}"
        
        new_comment = Comment(
            body=comment_with_ref,
            author_id=author_id,
            task_id=task_id
        )
        
        db.session.add(new_comment)
        db.session.commit()
        
        return {
            "id": new_comment.id,
            "body": new_comment.body,
            "author_id": new_comment.author_id,
            "task_id": new_comment.task_id,
            "subtask_id": subtask_id
        }
        
    except Exception as e:
        print(f"Error in add_subtask_comment: {e}")
        db.session.rollback()
        raise e

def update_task_status(task_id, new_status):
    #Update only the task status
    try:
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return None
        
        task.status = new_status
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
        print(f"Error in update_task_status: {e}")
        db.session.rollback()
        raise e