from .models import db, Project, Task, Attachment, TaskStatusEnum, project_collaborators, task_collaborators, Comment, comment_mentions
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

        recurrence_end_date = None
        if task_data.get('recurrence_end_date'):
            try:
                if isinstance(task_data['recurrence_end_date'], str) and task_data['recurrence_end_date'].strip():
                    # Handle datetime-local format from HTML input
                    recurrence_end_date_str = task_data['recurrence_end_date']
                    if 'T' in recurrence_end_date_str:
                        recurrence_end_date = datetime.fromisoformat(recurrence_end_date_str)
                    else:
                        recurrence_end_date = datetime.strptime(recurrence_end_date_str, '%Y-%m-%d %H:%M:%S')
                elif isinstance(task_data['recurrence_end_date'], datetime):
                    recurrence_end_date = task_data['recurrence_end_date']
            except ValueError as e:
                print(f"Error parsing recurrence_end_date: {e}")
                recurrence_end_date = None

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
            parent_task_id=task_data.get('parent_task_id'),
            priority=task_data.get('priority'),
            is_recurring=task_data.get('is_recurring', False),
            recurrence_interval=task_data.get('recurrence_interval'),
            recurrence_days=task_data.get('recurrence_days'),
            recurrence_end_date=recurrence_end_date
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

def delete_task(task_id, user_id):
    """Delete a task by ID"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return False, "Task not found"

        if len(task.subtasks) != 0:
            return False, "Cannot delete a task that has subtasks. Please delete or reassign subtasks first."
    
        is_owner = (task.owner_id == user_id)

        if not is_owner:
            return False, "Forbidden: You do not have permission to delete this task."

        print(f"Deleting task: {task.title}")
        db.session.delete(task)
        db.session.commit()
        return True, "Task deleted successfully"
        
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
            task_id=task_id,
            parent_comment_id=data.get('parent_comment_id')
        )
        
        db.session.add(new_comment)
        db.session.flush()

        mention_ids = data.get('mention_ids', [])
        if mention_ids:
            mention_entries = [
                {'comment_id': new_comment.id, 'user_id': user_id}
                for user_id in set(mention_ids)
            ]
            db.session.execute(comment_mentions.insert(), mention_entries)

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

# Not Settled

# Add these functions to your existing task_service/app/service.py file

# ==================== PROJECT FUNCTIONS ====================

def create_project(project_data):
    """Create a new project"""
    try:
        print(f"Creating project with data: {project_data}")
        
        # Parse deadline if provided
        deadline = None
        if project_data.get('deadline'):
            try:
                if isinstance(project_data['deadline'], str) and project_data['deadline'].strip():
                    deadline_str = project_data['deadline']
                    if 'T' in deadline_str:
                        deadline = datetime.fromisoformat(deadline_str)
                    else:
                        deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
                elif isinstance(project_data['deadline'], datetime):
                    deadline = project_data['deadline']
            except ValueError as e:
                print(f"Error parsing deadline: {e}")
                deadline = None
        
        # Create project
        new_project = Project(
            title=project_data['title'],
            description=project_data.get('description'),
            deadline=deadline,
            owner_id=project_data['owner_id']
        )
        
        db.session.add(new_project)
        db.session.commit()
        
        return new_project.to_json()
    except Exception as e:
        print(f"Error creating project: {e}")
        db.session.rollback()
        raise


def get_project_by_id(project_id, user_id):
    """Get a project by ID with authorization check"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return None, "Project not found"
        
        # Check if user has access (owner or collaborator)
        collaborator_ids = project.collaborator_ids()
        if user_id != project.owner_id and user_id not in collaborator_ids:
            return None, "Forbidden: You don't have access to this project"
        
        return project, None
    except Exception as e:
        print(f"Error getting project: {e}")
        raise


def get_project_dashboard(project_id, user_id, status_filter=None, sort_by='deadline', 
                          collaborator_filter=None, owner_filter=None):
    """
    Get project dashboard with tasks, collaborators, and filtering/sorting
    
    Args:
        project_id: ID of the project
        user_id: ID of the requesting user
        status_filter: Filter tasks by status (comma-separated string)
        sort_by: Sort tasks by field (deadline, title, status)
        collaborator_filter: If 'me', show only tasks where user is a collaborator
        owner_filter: If 'me', show only tasks where user is the owner
    """
    try:
        # Get project with authorization
        project, error = get_project_by_id(project_id, user_id)
        if error:
            return None, error
        
        # Start with all tasks in this project (excluding subtasks)
        tasks_query = Task.query.filter(
            Task.project_id == project_id,
            Task.parent_task_id.is_(None)
        )
        
        # Apply status filter
        if status_filter:
            status_list = [s.strip() for s in status_filter.split(',')]
            # Convert status strings to enum values
            status_enums = []
            for status_str in status_list:
                try:
                    status_enums.append(TaskStatusEnum(status_str))
                except ValueError:
                    print(f"Invalid status: {status_str}")
            
            if status_enums:
                tasks_query = tasks_query.filter(Task.status.in_(status_enums))
        
        # Apply collaborator filter
        if collaborator_filter == 'me':
            # Only show tasks where the user is a collaborator
            tasks_query = tasks_query.join(
                task_collaborators,
                task_collaborators.c.task_id == Task.id
            ).filter(task_collaborators.c.user_id == user_id)
        
        # Apply owner filter
        if owner_filter == 'me':
            tasks_query = tasks_query.filter(Task.owner_id == user_id)
        
        # Apply sorting
        if sort_by == 'deadline':
            # Sort by deadline, with null values last
            tasks_query = tasks_query.order_by(Task.deadline.asc().nullslast())
        elif sort_by == 'title':
            tasks_query = tasks_query.order_by(Task.title.asc())
        elif sort_by == 'status':
            tasks_query = tasks_query.order_by(Task.status.asc())
        elif sort_by == 'priority':
            tasks_query = tasks_query.order_by(Task.priority.desc().nullslast())
        
        tasks = tasks_query.all()
        
        # Get project collaborators
        collaborator_ids = project.collaborator_ids()
        
        # Build response
        dashboard_data = {
            'project': project.to_json(),
            'tasks': [task.to_json() for task in tasks],
            'collaborators': collaborator_ids,
            'task_count': len(tasks)
        }
        
        return dashboard_data, None
        
    except Exception as e:
        print(f"Error getting project dashboard: {e}")
        raise


def get_user_projects(user_id, role_filter=None):
    """
    Get all projects for a user (as owner or collaborator)
    
    Args:
        user_id: ID of the user
        role_filter: 'owner', 'collaborator', or None for all
    """
    try:
        projects_data = []
        
        if role_filter == 'owner':
            # Get only projects owned by user
            owned_projects = Project.query.filter_by(owner_id=user_id).all()
            for project in owned_projects:
                project_dict = project.to_json()
                project_dict['user_role'] = 'owner'
                
                # Add task count
                task_count = Task.query.filter(
                    Task.project_id == project.id,
                    Task.parent_task_id.is_(None)
                ).count()
                project_dict['task_count'] = task_count
                
                projects_data.append(project_dict)
        
        elif role_filter == 'collaborator':
            # Get only projects where user is a collaborator
            result = db.session.execute(
                project_collaborators.select().where(
                    project_collaborators.c.user_id == user_id
                )
            )
            collab_project_ids = [row.project_id for row in result]
            
            for project_id in collab_project_ids:
                project = Project.query.get(project_id)
                if project:
                    project_dict = project.to_json()
                    project_dict['user_role'] = 'collaborator'
                    
                    # Add task count
                    task_count = Task.query.filter(
                        Task.project_id == project.id,
                        Task.parent_task_id.is_(None)
                    ).count()
                    project_dict['task_count'] = task_count
                    
                    projects_data.append(project_dict)
        
        else:
            # Get all projects (owned + collaborating)
            # First, get owned projects
            owned_projects = Project.query.filter_by(owner_id=user_id).all()
            for project in owned_projects:
                project_dict = project.to_json()
                project_dict['user_role'] = 'owner'
                
                # Add task count
                task_count = Task.query.filter(
                    Task.project_id == project.id,
                    Task.parent_task_id.is_(None)
                ).count()
                project_dict['task_count'] = task_count
                
                projects_data.append(project_dict)
            
            # Then, get projects where user is a collaborator
            result = db.session.execute(
                project_collaborators.select().where(
                    project_collaborators.c.user_id == user_id
                )
            )
            collab_project_ids = [row.project_id for row in result]
            
            for project_id in collab_project_ids:
                # Skip if already added as owner
                if any(p['id'] == project_id for p in projects_data):
                    continue
                
                project = Project.query.get(project_id)
                if project:
                    project_dict = project.to_json()
                    project_dict['user_role'] = 'collaborator'
                    
                    # Add task count
                    task_count = Task.query.filter(
                        Task.project_id == project.id,
                        Task.parent_task_id.is_(None)
                    ).count()
                    project_dict['task_count'] = task_count
                    
                    projects_data.append(project_dict)
        
        return projects_data
        
    except Exception as e:
        print(f"Error getting user projects: {e}")
        raise


def update_project(project_id, user_id, project_data):
    """Update a project (only owner can update)"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return None, "Project not found"
        
        # Check if user is the owner
        if project.owner_id != user_id:
            return None, "Forbidden: Only the project owner can update the project"
        
        # Update fields
        if 'title' in project_data:
            project.title = project_data['title']
        
        if 'description' in project_data:
            project.description = project_data['description']
        
        if 'deadline' in project_data:
            deadline = None
            if project_data['deadline']:
                try:
                    if isinstance(project_data['deadline'], str):
                        deadline_str = project_data['deadline']
                        if 'T' in deadline_str:
                            deadline = datetime.fromisoformat(deadline_str)
                        else:
                            deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
                    elif isinstance(project_data['deadline'], datetime):
                        deadline = project_data['deadline']
                except ValueError as e:
                    print(f"Error parsing deadline: {e}")
            project.deadline = deadline
        
        db.session.commit()
        return project.to_json(), None
        
    except Exception as e:
        print(f"Error updating project: {e}")
        db.session.rollback()
        raise


def delete_project(project_id, user_id):
    """Delete a project (only owner can delete)"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return False, "Project not found"
        
        # Check if user is the owner
        if project.owner_id != user_id:
            return False, "Forbidden: Only the project owner can delete the project"
        
        db.session.delete(project)
        db.session.commit()
        return True, None
        
    except Exception as e:
        print(f"Error deleting project: {e}")
        db.session.rollback()
        raise


def add_project_collaborator(project_id, user_id, collaborator_user_id):
    """Add a collaborator to a project (only owner can add)"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return None, "Project not found"
        
        # Check if user is the owner
        if project.owner_id != user_id:
            return None, "Forbidden: Only the project owner can add collaborators"
        
        # Check if already a collaborator
        existing = db.session.execute(
            project_collaborators.select().where(
                project_collaborators.c.project_id == project_id,
                project_collaborators.c.user_id == collaborator_user_id
            )
        ).first()
        
        if existing:
            return None, "User is already a collaborator on this project"
        
        # Add collaborator
        db.session.execute(
            project_collaborators.insert().values(
                project_id=project_id,
                user_id=collaborator_user_id
            )
        )
        db.session.commit()
        
        return {"message": "Collaborator added successfully"}, None
        
    except Exception as e:
        print(f"Error adding collaborator: {e}")
        db.session.rollback()
        raise


def remove_project_collaborator(project_id, user_id, collaborator_user_id):
    """Remove a collaborator from a project (only owner can remove)"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return None, "Project not found"
        
        # Check if user is the owner
        if project.owner_id != user_id:
            return None, "Forbidden: Only the project owner can remove collaborators"
        
        # Remove collaborator
        db.session.execute(
            project_collaborators.delete().where(
                project_collaborators.c.project_id == project_id,
                project_collaborators.c.user_id == collaborator_user_id
            )
        )
        db.session.commit()
        
        return {"message": "Collaborator removed successfully"}, None
        
    except Exception as e:
        print(f"Error removing collaborator: {e}")
        db.session.rollback()
        raise

# Add these functions to backend/task_service/app/service.py

# ==================== EDIT PROJECT & MANAGE TASKS FUNCTIONS ====================

def remove_collaborator_from_project_tasks(project_id, user_id):
    """
    Remove a user from all tasks and subtasks in a project when they are removed as collaborator
    """
    try:
        # Get all tasks in the project (including subtasks)
        tasks = Task.query.filter(Task.project_id == project_id).all()
        
        for task in tasks:
            # Remove from task_collaborators if present
            db.session.execute(
                task_collaborators.delete().where(
                    task_collaborators.c.task_id == task.id,
                    task_collaborators.c.user_id == user_id
                )
            )
        
        db.session.commit()
        return True
        
    except Exception as e:
        print(f"Error removing collaborator from project tasks: {e}")
        db.session.rollback()
        raise


def add_existing_task_to_project(task_id, project_id, user_id):
    """
    Add an existing standalone task to a project
    User must be the task owner
    """
    try:
        # Get the task
        task = Task.query.get(task_id)
        
        if not task:
            return None, "Task not found"
        
        # Check if user is the task owner
        if task.owner_id != user_id:
            return None, "Forbidden: Only the task owner can add it to a project"
        
        # Check if task already belongs to a project
        if task.project_id is not None:
            return None, "Task is already assigned to a project"
        
        # Check if user has access to the project (owner or collaborator)
        project = Project.query.get(project_id)
        if not project:
            return None, "Project not found"
        
        collaborator_ids = project.collaborator_ids()
        if user_id != project.owner_id and user_id not in collaborator_ids:
            return None, "Forbidden: You don't have access to this project"
        
        # Assign task to project
        task.project_id = project_id
        db.session.commit()
        
        return task.to_json(), None
        
    except Exception as e:
        print(f"Error adding task to project: {e}")
        db.session.rollback()
        raise


def remove_task_from_project(task_id, user_id):
    """
    Unassign a task from its project
    User must be the task owner
    """
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return None, "Task not found"
        
        # Check if user is the task owner
        if task.owner_id != user_id:
            return None, "Forbidden: Only the task owner can remove it from a project"
        
        # Check if task belongs to a project
        if task.project_id is None:
            return None, "Task is not assigned to any project"
        
        # Remove from project
        task.project_id = None
        db.session.commit()
        
        return task.to_json(), None
        
    except Exception as e:
        print(f"Error removing task from project: {e}")
        db.session.rollback()
        raise


def create_task_in_project(task_data, project_id, user_id):
    """
    Create a new task directly within a project
    User must be project owner or collaborator
    """
    try:
        # Check if user has access to the project
        project = Project.query.get(project_id)
        if not project:
            return None, "Project not found"
        
        collaborator_ids = project.collaborator_ids()
        if user_id != project.owner_id and user_id not in collaborator_ids:
            return None, "Forbidden: You must be a project owner or collaborator to create tasks"
        
        # Add project_id to task data
        task_data['project_id'] = project_id
        
        # Create the task using existing function
        new_task = create_task(task_data)
        
        return new_task, None
        
    except Exception as e:
        print(f"Error creating task in project: {e}")
        db.session.rollback()
        raise


def get_standalone_tasks_for_user(user_id):
    """
    Get all tasks owned by user that are not assigned to any project (standalone tasks)
    """
    try:
        tasks = Task.query.filter(
            Task.owner_id == user_id,
            Task.project_id.is_(None),
            Task.parent_task_id.is_(None)  # Only parent tasks
        ).order_by(Task.id.desc()).all()
        
        return [task.to_json() for task in tasks]
        
    except Exception as e:
        print(f"Error getting standalone tasks: {e}")
        raise


# Update the existing remove_project_collaborator function to cascade removal
def remove_project_collaborator(project_id, user_id, collaborator_user_id):
    """
    Remove a collaborator from a project (only owner can remove)
    Also removes them from all project tasks and subtasks
    """
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return None, "Project not found"
        
        # Check if user is the owner
        if project.owner_id != user_id:
            return None, "Forbidden: Only the project owner can remove collaborators"
        
        # Cannot remove the owner
        if collaborator_user_id == project.owner_id:
            return None, "Cannot remove the project owner from collaborators"
        
        # Remove from project tasks first (CASCADE)
        remove_collaborator_from_project_tasks(project_id, collaborator_user_id)
        
        # Remove from project collaborators
        db.session.execute(
            project_collaborators.delete().where(
                project_collaborators.c.project_id == project_id,
                project_collaborators.c.user_id == collaborator_user_id
            )
        )
        db.session.commit()
        
        return {"message": "Collaborator removed successfully from project and all tasks"}, None
        
    except Exception as e:
        print(f"Error removing collaborator: {e}")
        db.session.rollback()
        raise