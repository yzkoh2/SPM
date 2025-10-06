from .models import db, Project, Task, Attachment, TaskStatusEnum, project_collaborators, task_collaborators, Comment
from sqlalchemy import or_
from sqlalchemy.orm import aliased
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Settled
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
        
        status = TaskStatusEnum.UNASSIGNED
        if task_data.get('status'):
            try:
                # Directly find the enum member by its value (e.g., 'Under Review')
                status = TaskStatusEnum(task_data['status'])
            except ValueError:
                status = TaskStatusEnum.UNASSIGNED
        # Create new task
        new_task = Task(
            title=task_data['title'],
            description=task_data.get('description'),
            deadline=deadline,
            status=status,
            owner_id=task_data['owner_id'],
            project_id=task_data.get('project_id'),
            parent_task_id=task_data.get('parent_task_id')
        )
        
        # Add to database
        db.session.add(new_task)
        db.session.commit()
        
        print(f"Task created with ID: {new_task.id}")
        
        # Return the created task
        return new_task.to_json()
        
    except Exception as e:
        print(f"Error in create_task: {e}")
        db.session.rollback()
        raise e

def update_task(task_id, user_id, task_data):
    """Update an existing task"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return None, "Task not found"
        
        # Check if taks belongs to user
        is_owner = (task.owner_id == user_id)
        is_collaborator = user_id in task.collaborator_ids()

        if not is_owner:
            if not is_collaborator:
                return None, "Forbidden: You do not have permission to edit this task."
            for field in task_data:
                if field != 'status':
                    return None, "Forbidden: Collaborators can only update the status of the task."
        
        for field, data in task_data.items():
            if field == 'deadline' and data:
                task.deadline = datetime.fromisoformat(data)
            elif field == 'recurring_end_date' and data:
                task.recurrence_end_date = datetime.fromisoformat(data)
            elif field == 'status':
                try:
                    # Directly find the enum member by its value (e.g., 'Under Review')
                    task.status = TaskStatusEnum(task_data['status'])
                except ValueError:
                    return None, "Invalid status value"
            else:
                setattr(task, field, data)
        
        db.session.flush()

        # --- RECURRENCE LOGIC (remains the same) ---
        if 'status' in task_data and task.status == TaskStatusEnum.COMPLETED:
            if task.is_recurring:
                _create_next_recurring_task(task)

        db.session.commit()
        return task.to_json(), "Task updated successfully"
        
    except Exception as e:
        print(f"Error in update_task: {e}")
        db.session.rollback()
        raise e

def _create_next_recurring_task(completed_task):
    """
    Creates the next instance of a recurring task.
    """
    if completed_task.recurrence_end_date and datetime.utcnow() >= completed_task.recurrence_end_date:
        return

    next_deadline = _calculate_next_due_date(
        completed_task.deadline, 
        completed_task.recurrence_interval, 
        completed_task.recurrence_days
    )

    new_task = Task(
        title=completed_task.title,
        description=completed_task.description,
        deadline=next_deadline,
        status=TaskStatusEnum.UNASSIGNED,
        owner_id=completed_task.owner_id,
        project_id=completed_task.project_id,
        parent_task_id=completed_task.parent_task_id,
        priority=completed_task.priority,
        is_recurring=True,
        recurrence_interval=completed_task.recurrence_interval,
        recurrence_days=completed_task.recurrence_days,
        recurrence_end_date=completed_task.recurrence_end_date
    )

    # --- FIX: Add and flush the new task to get its ID ---
    db.session.add(new_task)
    db.session.flush() # This assigns an ID to new_task without committing

    # --- Now this block will work correctly ---
    collaborator_ids_to_copy = completed_task.collaborator_ids()
    if collaborator_ids_to_copy: # Check if there are any collaborators
        # You can build a list of dictionaries for a bulk insert
        new_collaborators = [
            {'task_id': new_task.id, 'user_id': user_id}
            for user_id in collaborator_ids_to_copy
        ]
        db.session.execute(task_collaborators.insert(), new_collaborators)

    # --- Subtask copying logic remains the same ---
    for subtask_to_copy in completed_task.subtasks:
        # (Consider implementing the relative deadline logic here)
        new_subtask_deadline = subtask_to_copy.deadline # Or calculate a new one

        new_subtask = Task(
            title=subtask_to_copy.title,
            description=subtask_to_copy.description,
            deadline=new_subtask_deadline,
            status=TaskStatusEnum.UNASSIGNED,
            owner_id=subtask_to_copy.owner_id,
            project_id=subtask_to_copy.project_id,
            priority=subtask_to_copy.priority,
            parent_task=new_task
        )
        
        db.session.add(new_subtask)
        db.session.flush() # Flush to get the subtask's ID

        subtask_collaborator_ids = subtask_to_copy.collaborator_ids()
        if subtask_collaborator_ids:
            new_sub_collaborators = [
                {'task_id': new_subtask.id, 'user_id': user_id}
                for user_id in subtask_collaborator_ids
            ]
            db.session.execute(task_collaborators.insert(), new_sub_collaborators)
    
    # Mark the old task as no longer the active recurring one
    completed_task.is_recurring = False

def _calculate_next_due_date(current_deadline, interval, custom_days):
    """Calculates the next due date based on the recurrence interval."""
    if not current_deadline:
        return None # Cannot calculate next date without a starting point

    if interval == 'daily':
        return current_deadline + timedelta(days=1)
    elif interval == 'weekly':
        return current_deadline + timedelta(weeks=1)
    elif interval == 'monthly':
        return current_deadline + relativedelta(months=1)
    elif interval == 'custom' and custom_days:
        return current_deadline + timedelta(days=custom_days)
    
    return None

def delete_task(task_id):
    """Delete a task by ID"""
    try:
        task = Task.query.get(task_id)
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

        return task.to_json()
        
    except Exception as e:
        print(f"Error in get_task_details: {e}")
        raise e

# Not Settled
def add_comment(task_id, data):
    """Add a comment to a task"""
    try:
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return None, "Task not found"
        
        author_id = data.get('author_id')
        collab_ids = task.collaborator_ids()
        if task.owner_id != author_id and author_id not in collab_ids:
            return None, "Forbidden: You do not have permission to comment on this task."

        new_comment = Comment(
            body=data['body'],
            author_id=data['author_id'],
            task_id=task_id
        )
        
        db.session.add(new_comment)
        db.session.commit()
        
        return new_comment.to_json(), "Comment added successfully"
        
    except Exception as e:
        print(f"Error in add_comments: {e}")
        db.session.rollback()
        raise e

def delete_comment(comment_id):
    """Delete a comment by ID"""
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return False
            
        print(f"Deleting comment ID: {comment.id}")
        db.session.delete(comment)
        db.session.commit()
        return True
        
    except Exception as e:
        print(f"Error in delete_comment: {e}")
        db.session.rollback()
        raise e

def get_task_collaborators(task_id):
    """Get all collaborators for a task"""
    try:
        # Query the junction table directly using raw SQL
        result = db.session.execute(
            task_collaborators.select().where(task_collaborators.c.task_id == task_id)
        )
        
        # Return list of user_ids with minimal structure
        return [{'user_id': row.user_id} for row in result]
        
    except Exception as e:
        print(f"Error in get_task_collaborators: {e}")
        raise e

def add_task_collaborator(task_id, collaborator_id, user_id):
    """Add a collaborator to a task"""
    task = Task.query.get(task_id)
    if not task:
        raise Exception("Task not found")
    is_owner = (task.owner_id == user_id)
    if not is_owner:
        raise Exception("Forbidden: You do not have permission to edit this task.")
    parent_task_id = task.parent_task_id
    if parent_task_id:
        result = db.session.execute(
            task_collaborators.select().with_only_columns([task_collaborators.c.user_id])
            .where(task_collaborators.c.task_id == parent_task_id)
        )
        parent_collab_ids = [row.user_id for row in result]
        
        if collaborator_id not in parent_collab_ids:
            raise Exception("Collaborator must already be a collaborator of parent task.")
    try:
        db.session.execute(
            task_collaborators.insert().values(
                task_id=task_id,
                user_id=collaborator_id  
            )
        )
        db.session.commit()
        return {"message": "Collaborator added successfully"}
    except Exception as e:
        db.session.rollback()
        print(f"Error in add_task_collaborator: {e}")
        raise e

def remove_task_collaborator(task_id, collaborator_id, user_id):
    """Remove a collaborator from a task"""
    task = Task.query.get(task_id)
    if not task:
        raise Exception("Task not found")
    is_owner = (task.owner_id == user_id)
    if not is_owner:
        raise Exception("Forbidden: You do not have permission to edit this task.")
    task_ids = [task_id]
    children = Task.query.filter_by(parent_task_id=task_id).all()
    if children:
        task_ids.extend([child.id for child in children])
    try:
        db.session.execute(
            task_collaborators.delete().where(
                task_collaborators.c.task_id.in_(task_ids) &
                (task_collaborators.c.user_id == collaborator_id)
            )
        )
        db.session.commit()
        return {"message": "Collaborator removed successfully"}
    except Exception as e:
        db.session.rollback()
        print(f"Error in remove_task_collaborator: {e}")
        raise e

def get_task_subtasks(task_id):
    """Fetch all subtasks for a specific task"""
    try:
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return None
        
        return [subtask.to_json() for subtask in task.subtasks]
        
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