from .models import db, Project, Task, Attachment, TaskStatusEnum, project_collaborators, task_collaborators, Comment, comment_mentions
from sqlalchemy import or_
from sqlalchemy.orm import aliased
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from .rabbitmq_publisher import publish_status_update 
from werkzeug.utils import secure_filename
from flask import current_app
import uuid

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
    #Create a new task
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
        
        #Add to database
        db.session.add(new_task)
        db.session.flush()
        
        collaborators_to_add = set(task_data.get('collaborators_to_add', []))
        collaborators_to_add.add(new_task.owner_id)

        _add_collaborators_to_parents(new_task, collaborators_to_add)

        db.session.commit()
        
    except Exception as e:
        print(f"Error in create_task: {e}")
        db.session.rollback()
        raise e

def update_task(task_id, user_id, task_data):
    #Update an existing task
    try:
        task = Task.query.get(task_id)
        if not task:
            return None, "Task not found"
        
        # Check if tasks belongs to user
        is_owner = (task.owner_id == user_id)
        is_collaborator = user_id in task.collaborator_ids()

        if not is_owner:
            if not is_collaborator:
                return None, "Forbidden: You do not have permission to edit this task."
            if any(field != 'status' for field in task_data):
                return None, "Forbidden: Collaborators can only update the task's status."
        
        # Track status change
        old_status = None
        status_changed = False

        # Check if task is part of a project, then later update the updated_at timestamp
        project_to_update = None
        if task.project_id:
            project_to_update = Project.query.get(task.project_id)

        # Find the parent task (if this is a subtask)
        parent_task_to_update = None
        if task.parent_task_id:
            parent_task_to_update = Task.query.get(task.parent_task_id)
        
        current_time = db.func.now()

        for field, data in task_data.items():
            if field in ['id', 'owner_id', 'collaborators_to_add', 'collaborators_to_remove']:
                continue

            if field == 'deadline' and data:
                task.deadline = datetime.fromisoformat(data)
                _cascade_parent_deadline_to_subtasks(task, task.deadline)
            elif field == 'recurring_end_date' and data:
                task.recurrence_end_date = datetime.fromisoformat(data)
            elif field == 'status':
                try:
                    # Parse the new status value
                    new_status_enum = TaskStatusEnum(data)
                    
                    # Validate subtasks before completing
                    if new_status_enum == TaskStatusEnum.COMPLETED:
                        if not _are_all_subtasks_completed(task):
                            return None, "Cannot mark task as completed while it has incomplete subtasks."
                    
                    # Track status change for RabbitMQ
                    if task.status != new_status_enum:
                        old_status = task.status.value
                        status_changed = True
                    
                    # Update the status
                    task.status = new_status_enum
                    
                except ValueError:
                    return None, "Invalid status value"
            elif hasattr(task, field):
                setattr(task, field, data)

        if is_owner:
            # First, determine the final set of collaborators to be added.
            # Use a set to automatically handle duplicates.
            collaborators_to_add = set(task_data.get('collaborators_to_add', []))

            # If the owner is being changed, update the task and add the new owner
            # to our set of users to be added as collaborators.
            new_owner_id = task_data.get('owner_id')
            if new_owner_id and int(new_owner_id) != task.owner_id:
                task.owner_id = int(new_owner_id)
                collaborators_to_add.add(task.owner_id)

            # Add all new collaborators from the consolidated set
            if collaborators_to_add:
                _add_collaborators_to_parents(task, collaborators_to_add)

            # Remove collaborators from the task and all its subtasks
            collaborators_to_remove = task_data.get('collaborators_to_remove')
            if collaborators_to_remove:
                _remove_collaborators_from_subtasks(task, set(collaborators_to_remove))

        #RECURRENCE LOGIC
        if 'status' in task_data and task.status == TaskStatusEnum.COMPLETED:
            if task.is_recurring:
                _create_next_recurring_task(task)

        if project_to_update:
            project_to_update.updated_at = current_time
            db.session.add(project_to_update)
        
        if parent_task_to_update:
            parent_task_to_update.updated_at = current_time
            db.session.add(parent_task_to_update)

        db.session.commit()

        # Publish to RabbitMQ if status changed
        if status_changed:
            try:
                from .rabbitmq_publisher import publish_status_update
                
                publish_status_update(
                    task_id=task.id,
                    old_status=old_status,
                    new_status=task.status.value,
                    changed_by_id=user_id
                )
            except Exception as e:
                print(f"⚠️ Failed to publish to RabbitMQ: {e}")

        return task.to_json(), "Task updated successfully"
    
    except Exception as e:
        print(f"Error in update_task: {e}")
        db.session.rollback()
        raise e

def _create_next_recurring_task(completed_task):
    #Creates the next instance of a recurring task.
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
    #Calculates the next due date based on the recurrence interval.
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

def _add_collaborators_to_parents(task, collaborator_ids):
    """
    Helper function to add a set of collaborators to a task and cascade up to all its parents.
    """
    if not collaborator_ids:
        return

    updated_project_ids = set()

    current_task_node = task
    while current_task_node:
        result = db.session.execute(
            db.select(task_collaborators.c.user_id).where(
                task_collaborators.c.task_id == current_task_node.id
            )
        )
        existing_collab_ids = {row.user_id for row in result}
        
        new_for_this_task = collaborator_ids - existing_collab_ids
        
        if new_for_this_task:
            db.session.execute(task_collaborators.insert(), [
                {'task_id': current_task_node.id, 'user_id': collab_id} for collab_id in new_for_this_task
            ])
        
        project_id = current_task_node.project_id

        if project_id and project_id not in updated_project_ids:
            result = db.session.execute(
                db.select(project_collaborators.c.user_id).where(
                    project_collaborators.c.project_id == project_id
                )
            )
            existing_project_collab_ids = {row.user_id for row in result}
            new_for_this_project = collaborator_ids - existing_project_collab_ids

            if new_for_this_project:
                db.session.execute(project_collaborators.insert(), [
                    {'project_id': project_id, 'user_id': collab_id} for collab_id in new_for_this_project
                ])
            updated_project_ids.add(project_id)
        if current_task_node.parent_task_id:
            current_task_node = Task.query.get(current_task_node.parent_task_id)
        else:
            current_task_node = None

def _remove_collaborators_from_subtasks(task, collaborator_ids):
    """
    Helper function to remove a set of collaborators from a task and cascade down to all its subtasks.
    """
    if not collaborator_ids:
        return

    task_ids_to_update = _get_all_subtask_ids(task.id)
    select_owners_query = db.select(Task.owner_id).where(Task.id.in_(task_ids_to_update)).distinct()
    owner_ids_result = db.session.execute(select_owners_query)
    protected_owner_ids = {owner_id for (owner_id,) in owner_ids_result}

    # 3. Filter the list of collaborators to remove, excluding protected owners
    safe_list_to_remove = [
        user_id for user_id in collaborator_ids if user_id not in protected_owner_ids
    ]

    # 4. If there are any collaborators left to remove, execute the delete operation
    if safe_list_to_remove:
        db.session.execute(
            task_collaborators.delete().where(
                task_collaborators.c.task_id.in_(task_ids_to_update) &
                task_collaborators.c.user_id.in_(safe_list_to_remove)
            )
        )

def _are_all_subtasks_completed(task):
    """Check if status of all subtasks of a task are completed"""
    if not task.subtasks:
        return True
    for subtask in task.subtasks:
        if subtask.status != TaskStatusEnum.COMPLETED:
            return False
    return True

def _cascade_parent_deadline_to_subtasks(task, new_deadline):
    """Recursively update subtasks' deadlines if they exceed the new parent deadline"""
    for subtask in task.subtasks:
        if subtask.deadline and new_deadline and subtask.deadline > new_deadline:
            subtask.deadline = new_deadline
        _cascade_parent_deadline_to_subtasks(subtask, new_deadline)

def delete_task(task_id, user_id):
    #Delete a task by ID
    try:
        task = Task.query.get(task_id)
        if not task:
            return False, "Task not found"

        if not all(subtask.status == TaskStatusEnum.COMPLETED for subtask in task.subtasks):
            return False, "Cannot delete task. All subtasks must be completed first."
    
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
    #Fetch a task with its subtasks, comments, and attachments
    try:
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return None

        return task.to_json()
        
    except Exception as e:
        print(f"Error in get_task_details: {e}")
        raise e

def add_comment(task_id, data):
    #Add a new comment to a task, trigger mention notification if necessary
    try:
        #Create new comment
        new_comment = Comment(
            body=data['body'],
            author_id=data['author_id'],
            task_id=task_id,
            parent_comment_id=data.get('parent_comment_id')
        )
        
        db.session.add(new_comment)
        db.session.flush()

        #Process mentions (if any)
        mention_ids = data.get('mention_ids', [])
        if mention_ids:
            #Save mention relationships to database
            mention_entries = [
                {'comment_id': new_comment.id, 'user_id': user_id}
                for user_id in set(mention_ids)
            ]
            db.session.execute(comment_mentions.insert(), mention_entries)
            
            #Publish mention alerts to RabbitMQ
            from .rabbitmq_publisher import publish_mention_alert
            
            print(f"📝 Processing {len(set(mention_ids))} mention(s) for comment {new_comment.id}")
            
            for mentioned_user_id in set(mention_ids):
                #Skip self-mentions
                if mentioned_user_id == data['author_id']:
                    print(f"⏭️  Skipping self-mention for user {mentioned_user_id}")
                    continue
                
                try:
                    publish_mention_alert(
                        task_id=task_id,
                        comment_id=new_comment.id,
                        mentioned_user_id=mentioned_user_id,
                        author_id=data['author_id'],
                        comment_body=data['body']
                    )
                except Exception as publish_error:
                    print(f"⚠️  Failed to publish mention alert: {publish_error}")

        db.session.commit()
        
        return new_comment.to_json(), "Comment added successfully"
        
    except Exception as e:
        print(f"Error in add_comments: {e}")
        db.session.rollback()
        raise e

def delete_comment(comment_id):
    #Delete a comment by ID
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
    #Get all collaborators for a task
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

def add_task_collaborators(task_id, collaborator_ids, user_id):
    """Add a list of collaborators to a task and all its parent tasks."""
    if not isinstance(collaborator_ids, list) or not collaborator_ids:
        raise ValueError("collaborator_ids must be a non-empty list.")

    task = Task.query.get(task_id)
    if not task:
        raise Exception("Task not found")

    if task.owner_id != user_id:
        raise Exception("Forbidden: You do not have permission to edit this task.")

    try:
        # Use a set to avoid duplicate collaborator IDs
        collaborators_to_add = set(collaborator_ids)
        
        # Start with the current task and move up to its parents
        current_task = task
        while current_task:
            # Get existing collaborators for the current task
            result = db.session.execute(
                task_collaborators.select().with_only_columns([task_collaborators.c.user_id])
                .where(task_collaborators.c.task_id == current_task.id)
            )
            existing_collaborators = {row.user_id for row in result}
            
            # Determine which collaborators are new for this task
            new_collaborators_for_task = collaborators_to_add - existing_collaborators
            
            if new_collaborators_for_task:
                new_collaborator_entries = [
                    {'task_id': current_task.id, 'user_id': collab_id}
                    for collab_id in new_collaborators_for_task
                ]
                db.session.execute(task_collaborators.insert(), new_collaborator_entries)
            
            # Move to the parent task
            if current_task.parent_task_id:
                current_task = Task.query.get(current_task.parent_task_id)
            else:
                current_task = None

        db.session.commit()
        return {"message": "Collaborators added successfully to the task and its parents"}
    except Exception as e:
        db.session.rollback()
        print(f"Error in add_task_collaborators: {e}")
        raise e

def remove_task_collaborator(task_id, collaborator_ids, user_id):
    """Remove a list of collaborators from a task and all its subtasks."""
    if not isinstance(collaborator_ids, list) or not collaborator_ids:
        raise ValueError("collaborator_ids must be a non-empty list.")

    task = Task.query.get(task_id)
    if not task:
        raise Exception("Task not found")

    is_owner = (task.owner_id == user_id)
    if not is_owner:
        raise Exception("Forbidden: You do not have permission to edit this task.")

    # A recursive function to get all subtask IDs
    def get_all_subtask_ids(t_id):
        ids = {t_id}
        children = Task.query.filter_by(parent_task_id=t_id).all()
        for child in children:
            ids.update(get_all_subtask_ids(child.id))
        return ids

    task_ids_to_update = get_all_subtask_ids(task_id)

    try:
        db.session.execute(
            task_collaborators.delete().where(
                task_collaborators.c.task_id.in_(task_ids_to_update) &
                (task_collaborators.c.user_id.in_(collaborator_ids))
            )
        )
        db.session.commit()
        return {"message": "Collaborators removed successfully from the task and its subtasks"}
    except Exception as e:
        db.session.rollback()
        print(f"Error in remove_task_collaborator: {e}")
        raise e

def _get_all_subtask_ids(task_id):
    ids = {task_id}
    children = Task.query.filter_by(parent_task_id=task_id).all()
    for child in children:
        ids.update(_get_all_subtask_ids(child.id))
    return ids

def add_attachment(task_id, file, input_filename):
    """Add an attachment to a task"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return None

        # Secure the filename and use it as the S3 object key
        filename = secure_filename(file.filename)
        s3_object_key = f"{uuid.uuid4()}_{filename}" 
        
        # Upload the file object to S3
        current_app.s3_client.upload_fileobj(
            file,
            current_app.config['S3_BUCKET_NAME'],
            s3_object_key,
            ExtraArgs={'ContentType': file.content_type}
        )

        # In the DB, store the filename (S3 key), not a full URL
        new_attachment = Attachment(
            filename=input_filename,
            url=s3_object_key,  # Storing S3 object key in the 'url' field
            task_id=task_id
        )
        db.session.add(new_attachment)
        db.session.commit()
        return new_attachment.to_json()
    except Exception as e:
        db.session.rollback()
        raise e

def get_attachment_url(task_id, attachment_id):
    """Generate a pre-signed URL for an attachment"""
    try:
        attachment = Attachment.query.filter_by(
            id=attachment_id, task_id=task_id
        ).first()

        if not attachment:
            return None, "Attachment not found"

        presigned_url = current_app.s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': current_app.config['S3_BUCKET_NAME'],
                'Key': attachment.url
            },
            ExpiresIn=3600  # URL valid for 1 hour
        )

        return {
            "id": attachment.id,
            "filename": attachment.filename,
            "url": presigned_url,
        }, "Success"
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None, "Error generating URL"

def delete_attachment_url(task_id, attachment_id):
    """Delete an attachment from a task"""
    try:
        attachment = Attachment.query.filter_by(
            id=attachment_id, task_id=task_id
        ).first()

        if not attachment:
            return False, "Attachment not found"

        # Delete the file from S3
        current_app.s3_client.delete_object(
            Bucket=current_app.config['S3_BUCKET_NAME'],
            Key=attachment.url
        )

        # Delete the attachment record from the database
        db.session.delete(attachment)
        db.session.commit()
        return True, "Attachment deleted successfully"
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting attachment: {e}")
        return False, "Error deleting attachment"

# ==================== PROJECT FUNCTIONS ====================

def create_project(project_data):
    #Create a new project
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
        db.session.flush()

        collaborators_to_add = set(project_data.get('collaborator_ids', []))
        collaborators_to_add.add(new_project.owner_id)

        result = db.session.execute(
            db.select(project_collaborators.c.user_id).where(
                project_collaborators.c.project_id == new_project.id
            )
        )
        existing_collaborators = {row.user_id for row in result}
        new_collaborators_for_project = collaborators_to_add - existing_collaborators
        if new_collaborators_for_project:
            new_collaborator_entries = [
                {'project_id': new_project.id, 'user_id': collab_id}
                for collab_id in new_collaborators_for_project
            ]
            db.session.execute(project_collaborators.insert(), new_collaborator_entries)

        db.session.commit()
        
        return new_project.to_json()
    except Exception as e:
        print(f"Error creating project: {e}")
        db.session.rollback()
        raise

def get_project_by_id(project_id, user_id):
    #Get a project by ID with authorization check
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

# Done update
def update_project(project_id, user_id, project_data):
    """Update a project (title, description, deadline, owner, collaborators)"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return None, "Project not found"
        
        # Check if user is the owner
        if project.owner_id != user_id:
            return None, "Forbidden: Only the project owner can update the project"
        
        # --- Handle standard field updates ---
        for field, data in project_data.items():
            # Skip fields that are handled manually below
            if field in ['id', 'owner_id', 'collaborators_to_add', 'collaborators_to_remove']:
                continue

            if field == 'deadline':
                deadline = None
                if data:  # 'data' is the value of project_data['deadline']
                    try:
                        if isinstance(data, str):
                            deadline_str = data
                            if 'T' in deadline_str:
                                deadline = datetime.fromisoformat(deadline_str)
                            else:
                                try:
                                    deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
                                except ValueError:
                                     deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
                        elif isinstance(data, datetime):
                            deadline = data
                    except ValueError as e:
                        print(f"Error parsing deadline: {e}")
                
                project.deadline = deadline
                _cascade_project_deadline_to_tasks(project.id, deadline)
            
            elif hasattr(project, field):
                # This will update 'title' and 'description'
                setattr(project, field, data)

        # --- Handle Collaborator Changes ---
        collaborators_to_add = project_data.get('collaborators_to_add', [])
        if collaborators_to_add:
            for collab_id in collaborators_to_add:
                if int(collab_id) != project.owner_id:
                    try:
                        add_project_collaborator(project_id, user_id, int(collab_id))
                    except Exception as add_err:
                        print(f"Warning: Failed to add collaborator {collab_id}: {add_err}")

        collaborators_to_remove = project_data.get('collaborators_to_remove', [])
        if collaborators_to_remove:
            for collab_id in collaborators_to_remove:
                if int(collab_id) != user_id:
                    try:
                        remove_project_collaborator(project_id, user_id, int(collab_id))
                    except Exception as remove_err:
                        print(f"Warning: Failed to remove collaborator {collab_id}: {remove_err}")
        
        db.session.commit()
        # Return the updated project and a success message
        return project.to_json(), "Project updated successfully"
        
    except Exception as e:
        print(f"Error updating project: {e}")
        db.session.rollback()
        # On failure, return None and an error message
        return None, f"An internal error occurred: {str(e)}"

def _cascade_project_deadline_to_tasks(project_id, new_project_deadline):
    """
    Updates deadlines for all parent tasks in a project and recursively cascades
    to their subtasks by calling _cascade_parent_deadline_to_subtasks.
    """
    # Do nothing if the new project deadline is cleared (set to None)
    if not new_project_deadline:
        print("Project deadline cleared, not cascading.")
        return

    try:
        # Step 1: Get only the PARENT tasks in the project
        parent_tasks = Task.query.filter(
            Task.project_id == project_id,
            Task.parent_task_id.is_(None)
        ).all()

        if not parent_tasks:
            return  # No parent tasks in this project

        updated_parent_count = 0
        for task in parent_tasks:
            # Step 2: Update the parent task itself if its deadline is later
            if task.deadline and task.deadline > new_project_deadline:
                task.deadline = new_project_deadline
                updated_parent_count += 1
            
            # Step 3: Call the *existing* recursive helper for its subtasks
            # This will check all children, grandchildren, etc.
            _cascade_parent_deadline_to_subtasks(task, new_project_deadline)

        if updated_parent_count > 0:
            print(f"Cascaded new project deadline to {updated_parent_count} parent tasks (and their subtasks).")

    except Exception as e:
        # Log the error but don't block the main update
        print(f"Error cascading project deadline: {e}")

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

# ==================== EDIT PROJECT & GET/ MANAGE TASKS FUNCTIONS ====================
def get_project_tasks(project_id):
    """
    Get all tasks (excluding subtasks) for a project
    """
    try:        
        # Get all parent tasks in the project
        tasks = Task.query.filter(
            Task.project_id == project_id,
            Task.parent_task_id.is_(None)
        ).order_by(Task.id.desc()).all()
        
        return tasks, None
        
    except Exception as e:
        print(f"Error getting project tasks: {e}")
        raise

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
        
        # Check if user adding task is the task owner
        if task.owner_id != user_id:
            return None, "Forbidden: Only the task owner can add it to a project"
        
        # Check if task already belongs to a project
        if task.project_id is not None:
            return None, "Task is already assigned to a project"
        
        # Check if user has access to the project (owner or collaborator)
        project = Project.query.get(project_id)
        if not project:
            return None, "Project not found"
        
        project_collaborators = set(project.collaborator_ids())
        is_project_owner = (user_id == project.owner_id)
        is_project_member = (user_id in project_collaborators)

        if not is_project_owner and not is_project_member:
            return None, "Forbidden: You don't have access to this project"

        task_collaborators = set(task.collaborator_ids())
        missing_collaborators = [
            collab_id for collab_id in task_collaborators
            if collab_id not in project_collaborators
        ]

        if missing_collaborators:
            if not is_project_owner:
                # Reject adding the task if user is not project owner (given task has collaborators outside project collaborators)
                return None, "Forbidden: Task has collaborators not in the project"
            else:
                # Add missing collaborators to the project
                for collab_id in missing_collaborators:
                    try:
                        add_project_collaborator(project_id, project.owner_id, collab_id)
                    except Exception as add_err:
                        print(f"Warning: Failed to add collaborator {collab_id} to project {project_id}: {add_err}")

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
        
        # Check if task belongs to a project
        if task.project_id is None:
            return None, "Task is not assigned to any project"
        
        # Get Project
        project = Project.query.get(task.project_id)
        if not project:
            return None, "Project not found"
        
        is_task_owner = (task.owner_id == user_id)
        is_project_owner = (user_id == project.owner_id)

        if not is_task_owner and not is_project_owner:
            return None, "Forbidden: You don't have permission to remove this task from the project"

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

        for collab_id in task_data.get('collaborators_to_add', []):
            try:
                add_project_collaborator(project_id, project.owner_id, collab_id)
            except Exception as add_err:
                print(f"Warning: Failed to add collaborator {collab_id} to task {new_task.id}: {add_err}")
        
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