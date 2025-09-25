from flask import Blueprint, jsonify, request
from .service import (TaskService, SubtaskService, CollaboratorService, 
                      CommentService, AttachmentService)

task_bp = Blueprint("task_bp", __name__)

# Task Routes
@task_bp.route("/tasks", methods=["GET"])
def get_all_tasks():
    """Get all tasks, with optional filtering"""
    try:
        created_by = request.args.get('created_by', type=int)
        owner_id = request.args.get('owner_id', type=int)
        assigned_to = request.args.get('assigned_to', type=int)
        status = request.args.get('status')
        include_unassigned = request.args.get('include_unassigned', 'false').lower() == 'true'
        limit = request.args.get('limit', type=int)
        
        print(f"Getting tasks with filters: created_by={created_by}, owner_id={owner_id}, "
              f"assigned_to={assigned_to}, status={status}, include_unassigned={include_unassigned}")
        
        tasks = TaskService.get_all_tasks(
            created_by=created_by,
            owner_id=owner_id,
            assigned_to=assigned_to, 
            status=status,
            include_unassigned=include_unassigned,
            limit=limit
        )
        return jsonify(tasks), 200
    except Exception as e:
        print(f"Error in get_all_tasks: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks", methods=["POST"])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        print(f"Creating task with data: {data}")
        
        # Validate required fields
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        if not data.get('title'):
            return jsonify({"error": "Title is required"}), 400
        if not data.get('created_by'):
            return jsonify({"error": "Created by user ID is required"}), 400
            
        # Create the task using service
        new_task = TaskService.create_task(data)
        print(f"Created task: {new_task}")
        return jsonify(new_task), 201
        
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error in create_task: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    """Get a specific task with its details"""
    try:
        print(f"Getting task with id={task_id}")
        
        task_details = TaskService.get_task_by_id(task_id)
        if not task_details:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(task_details), 200
    except Exception as e:
        print(f"Error in get_task: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """Update a task"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
            
        updated_by_user_id = data.get('updated_by')
        print(f"Updating task {task_id} with data: {data}")
        
        updated_task = TaskService.update_task(task_id, data, updated_by_user_id)
        if not updated_task:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(updated_task), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error in update_task: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete a task"""
    try:
        print(f"Deleting task with id={task_id}")
        
        success = TaskService.delete_task(task_id)
        if success:
            return jsonify({"message": "Task deleted successfully"}), 200
        else:
            return jsonify({"error": "Task not found"}), 404
    except Exception as e:
        print(f"Error in delete_task: {e}")
        return jsonify({"error": str(e)}), 500

# Task Assignment Routes
@task_bp.route("/tasks/<int:task_id>/assign", methods=["POST"])
def assign_task(task_id):
    """Assign a task to a user (transfers ownership)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        if not data.get('assigned_to'):
            return jsonify({"error": "Assigned to user ID is required"}), 400
            
        updated_by_user_id = data.get('updated_by')
        print(f"Assigning task {task_id} to user {data['assigned_to']}")
        
        updated_task = TaskService.assign_task(
            task_id=task_id,
            assigned_to_user_id=data['assigned_to'],
            updated_by_user_id=updated_by_user_id
        )
        if not updated_task:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(updated_task), 200
    except Exception as e:
        print(f"Error in assign_task: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/unassign", methods=["POST"])
def unassign_task(task_id):
    """Unassign a task (remove assignee but keep owner)"""
    try:
        data = request.get_json() or {}
        updated_by_user_id = data.get('updated_by')
        print(f"Unassigning task {task_id}")
        
        updated_task = TaskService.unassign_task(
            task_id=task_id,
            updated_by_user_id=updated_by_user_id
        )
        if not updated_task:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(updated_task), 200
    except Exception as e:
        print(f"Error in unassign_task: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/transfer-ownership", methods=["POST"])
def transfer_task_ownership(task_id):
    """Transfer task ownership without changing assignment"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        if not data.get('new_owner_id'):
            return jsonify({"error": "New owner ID is required"}), 400
            
        updated_by_user_id = data.get('updated_by')
        print(f"Transferring ownership of task {task_id} to user {data['new_owner_id']}")
        
        updated_task = TaskService.transfer_ownership(
            task_id=task_id,
            new_owner_id=data['new_owner_id'],
            updated_by_user_id=updated_by_user_id
        )
        if not updated_task:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(updated_task), 200
    except Exception as e:
        print(f"Error in transfer_task_ownership: {e}")
        return jsonify({"error": str(e)}), 500

# User Task Routes
@task_bp.route("/users/<int:user_id>/tasks", methods=["GET"])
def get_user_tasks(user_id):
    """Get all tasks related to a user"""
    try:
        include_owned = request.args.get('include_owned', 'true').lower() == 'true'
        include_assigned = request.args.get('include_assigned', 'true').lower() == 'true'
        include_created = request.args.get('include_created', 'false').lower() == 'true'
        include_unassigned = request.args.get('include_unassigned', 'false').lower() == 'true'
        
        print(f"Getting tasks for user {user_id}")
        
        user_tasks = TaskService.get_user_tasks(
            user_id=user_id,
            include_owned=include_owned,
            include_assigned=include_assigned,
            include_created=include_created,
            include_unassigned=include_unassigned
        )
        return jsonify(user_tasks), 200
    except Exception as e:
        print(f"Error in get_user_tasks: {e}")
        return jsonify({"error": str(e)}), 500

# Subtask Routes
@task_bp.route("/tasks/<int:task_id>/subtasks", methods=["GET"])
def get_task_subtasks(task_id):
    """Get all subtasks for a specific task"""
    try:
        assigned_to = request.args.get('assigned_to', type=int)
        status = request.args.get('status')
        
        print(f"Getting subtasks for task {task_id}")
        
        subtasks = SubtaskService.get_task_subtasks(
            task_id=task_id,
            assigned_to=assigned_to,
            status=status
        )
        return jsonify(subtasks), 200
    except Exception as e:
        print(f"Error in get_task_subtasks: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/subtasks", methods=["POST"])
def create_subtask(task_id):
    """Create a new subtask"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        if not data.get('title'):
            return jsonify({"error": "Title is required"}), 400
        if not data.get('created_by'):
            return jsonify({"error": "Created by user ID is required"}), 400
            
        # Add task_id to the data
        data['task_id'] = task_id
        
        print(f"Creating subtask for task {task_id}: {data}")
        
        new_subtask = SubtaskService.create_subtask(data)
        return jsonify(new_subtask), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error in create_subtask: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/subtasks/<int:subtask_id>", methods=["GET"])
def get_subtask(subtask_id):
    """Get a specific subtask with its details"""
    try:
        print(f"Getting subtask with id={subtask_id}")
        
        subtask_details = SubtaskService.get_subtask_by_id(subtask_id)
        if not subtask_details:
            return jsonify({"error": "Subtask not found"}), 404
        return jsonify(subtask_details), 200
    except Exception as e:
        print(f"Error in get_subtask: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/subtasks/<int:subtask_id>", methods=["PUT"])
def update_subtask(subtask_id):
    """Update a subtask"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
            
        updated_by_user_id = data.get('updated_by')
        print(f"Updating subtask {subtask_id} with data: {data}")
        
        updated_subtask = SubtaskService.update_subtask(subtask_id, data, updated_by_user_id)
        if not updated_subtask:
            return jsonify({"error": "Subtask not found"}), 404
        return jsonify(updated_subtask), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error in update_subtask: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/subtasks/<int:subtask_id>", methods=["DELETE"])
def delete_subtask(subtask_id):
    """Delete a subtask"""
    try:
        print(f"Deleting subtask with id={subtask_id}")
        
        success = SubtaskService.delete_subtask(subtask_id)
        if success:
            return jsonify({"message": "Subtask deleted successfully"}), 200
        else:
            return jsonify({"error": "Subtask not found"}), 404
    except Exception as e:
        print(f"Error in delete_subtask: {e}")
        return jsonify({"error": str(e)}), 500

# Subtask Assignment Routes
@task_bp.route("/subtasks/<int:subtask_id>/assign", methods=["POST"])
def assign_subtask(subtask_id):
    """Assign a subtask to a user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        if not data.get('assigned_to'):
            return jsonify({"error": "Assigned to user ID is required"}), 400
            
        updated_by_user_id = data.get('updated_by')
        print(f"Assigning subtask {subtask_id} to user {data['assigned_to']}")
        
        updated_subtask = SubtaskService.assign_subtask(
            subtask_id=subtask_id,
            assigned_to_user_id=data['assigned_to'],
            updated_by_user_id=updated_by_user_id
        )
        if not updated_subtask:
            return jsonify({"error": "Subtask not found"}), 404
        return jsonify(updated_subtask), 200
    except Exception as e:
        print(f"Error in assign_subtask: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/subtasks/<int:subtask_id>/complete", methods=["POST"])
def complete_subtask(subtask_id):
    """Mark a subtask as completed"""
    try:
        data = request.get_json() or {}
        updated_by_user_id = data.get('updated_by')
        print(f"Marking subtask {subtask_id} as completed")
        
        updated_subtask = SubtaskService.complete_subtask(
            subtask_id=subtask_id,
            updated_by_user_id=updated_by_user_id
        )
        if not updated_subtask:
            return jsonify({"error": "Subtask not found"}), 404
        return jsonify(updated_subtask), 200
    except Exception as e:
        print(f"Error in complete_subtask: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/subtasks/reorder", methods=["POST"])
def reorder_subtasks(task_id):
    """Reorder subtasks for a task"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        if not data.get('subtask_order'):
            return jsonify({"error": "Subtask order is required"}), 400
            
        print(f"Reordering subtasks for task {task_id}: {data['subtask_order']}")
        
        reordered_subtasks = SubtaskService.reorder_subtasks(
            task_id=task_id,
            subtask_order=data['subtask_order']
        )
        return jsonify(reordered_subtasks), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error in reorder_subtasks: {e}")
        return jsonify({"error": str(e)}), 500

# Collaborator Routes
@task_bp.route("/tasks/<int:task_id>/collaborators", methods=["GET"])
def get_task_collaborators(task_id):
    """Get all collaborators for a task"""
    try:
        print(f"Getting collaborators for task {task_id}")
        
        collaborators = CollaboratorService.get_task_collaborators(task_id)
        return jsonify(collaborators), 200
    except Exception as e:
        print(f"Error in get_task_collaborators: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/collaborators", methods=["POST"])
def add_collaborator(task_id):
    """Add a collaborator to a task"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        if not data.get('user_id'):
            return jsonify({"error": "User ID is required"}), 400
            
        print(f"Adding collaborator to task {task_id}: {data}")
        
        collaborator = CollaboratorService.add_collaborator(
            task_id=task_id,
            user_id=data['user_id'],
            role=data.get('role', 'collaborator'),
            added_by_user_id=data.get('added_by')
        )
        return jsonify(collaborator), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error in add_collaborator: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/collaborators/<int:user_id>", methods=["DELETE"])
def remove_collaborator(task_id, user_id):
    """Remove a collaborator from a task"""
    try:
        print(f"Removing collaborator {user_id} from task {task_id}")
        
        success = CollaboratorService.remove_collaborator(task_id, user_id)
        if success:
            return jsonify({"message": "Collaborator removed successfully"}), 200
        else:
            return jsonify({"error": "Collaborator not found"}), 404
    except Exception as e:
        print(f"Error in remove_collaborator: {e}")
        return jsonify({"error": str(e)}), 500

# Comment Routes (Tasks)
@task_bp.route("/tasks/<int:task_id>/comments", methods=["POST"])
def create_task_comment(task_id):
    """Create a new comment on a task"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        if not data.get('content'):
            return jsonify({"error": "Comment content is required"}), 400
        if not data.get('created_by'):
            return jsonify({"error": "Created by user ID is required"}), 400
            
        print(f"Creating comment for task {task_id}: {data}")
        
        comment = CommentService.create_task_comment(
            task_id=task_id,
            content=data['content'],
            created_by_user_id=data['created_by']
        )
        return jsonify(comment), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error in create_task_comment: {e}")
        return jsonify({"error": str(e)}), 500

# Comment Routes (Subtasks)
@task_bp.route("/subtasks/<int:subtask_id>/comments", methods=["POST"])
def create_subtask_comment(subtask_id):
    """Create a new comment on a subtask"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        if not data.get('content'):
            return jsonify({"error": "Comment content is required"}), 400
        if not data.get('created_by'):
            return jsonify({"error": "Created by user ID is required"}), 400
            
        print(f"Creating comment for subtask {subtask_id}: {data}")
        
        comment = CommentService.create_subtask_comment(
            subtask_id=subtask_id,
            content=data['content'],
            created_by_user_id=data['created_by']
        )
        return jsonify(comment), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error in create_subtask_comment: {e}")
        return jsonify({"error": str(e)}), 500

# Comment Routes (General)
@task_bp.route("/comments/<int:comment_id>", methods=["PUT"])
def update_comment(comment_id):
    """Update a comment"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        if not data.get('content'):
            return jsonify({"error": "Comment content is required"}), 400
        if not data.get('updated_by'):
            return jsonify({"error": "Updated by user ID is required"}), 400
            
        print(f"Updating comment {comment_id}: {data}")
        
        comment = CommentService.update_comment(
            comment_id=comment_id,
            content=data['content'],
            updated_by_user_id=data['updated_by']
        )
        if not comment:
            return jsonify({"error": "Comment not found"}), 404
        return jsonify(comment), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error in update_comment: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    """Delete a comment"""
    try:
        print(f"Deleting comment {comment_id}")
        
        success = CommentService.delete_comment(comment_id)
        if success:
            return jsonify({"message": "Comment deleted successfully"}), 200
        else:
            return jsonify({"error": "Comment not found"}), 404
    except Exception as e:
        print(f"Error in delete_comment: {e}")
        return jsonify({"error": str(e)}), 500

# Attachment Routes (Tasks)
@task_bp.route("/tasks/<int:task_id>/attachments", methods=["GET"])
def get_task_attachments(task_id):
    """Get all attachments for a task"""
    try:
        print(f"Getting attachments for task {task_id}")
        
        attachments = AttachmentService.get_task_attachments(task_id)
        return jsonify(attachments), 200
    except Exception as e:
        print(f"Error in get_task_attachments: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/attachments", methods=["POST"])
def create_task_attachment(task_id):
    """Create a new attachment for a task"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        if not data.get('file_name'):
            return jsonify({"error": "File name is required"}), 400
        if not data.get('file_path'):
            return jsonify({"error": "File path is required"}), 400
        if not data.get('uploaded_by'):
            return jsonify({"error": "Uploaded by user ID is required"}), 400
            
        print(f"Creating attachment for task {task_id}: {data}")
        
        attachment = AttachmentService.create_task_attachment(
            task_id=task_id,
            file_name=data['file_name'],
            file_path=data['file_path'],
            uploaded_by_user_id=data['uploaded_by'],
            file_size=data.get('file_size'),
            mime_type=data.get('mime_type')
        )
        return jsonify(attachment), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error in create_task_attachment: {e}")
        return jsonify({"error": str(e)}), 500

# Attachment Routes (Subtasks)
@task_bp.route("/subtasks/<int:subtask_id>/attachments", methods=["GET"])
def get_subtask_attachments(subtask_id):
    """Get all attachments for a subtask"""
    try:
        print(f"Getting attachments for subtask {subtask_id}")
        
        attachments = AttachmentService.get_subtask_attachments(subtask_id)
        return jsonify(attachments), 200
    except Exception as e:
        print(f"Error in get_subtask_attachments: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/subtasks/<int:subtask_id>/attachments", methods=["POST"])
def create_subtask_attachment(subtask_id):
    """Create a new attachment for a subtask"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        if not data.get('file_name'):
            return jsonify({"error": "File name is required"}), 400
        if not data.get('file_path'):
            return jsonify({"error": "File path is required"}), 400
        if not data.get('uploaded_by'):
            return jsonify({"error": "Uploaded by user ID is required"}), 400
            
        print(f"Creating attachment for subtask {subtask_id}: {data}")
        
        attachment = AttachmentService.create_subtask_attachment(
            subtask_id=subtask_id,
            file_name=data['file_name'],
            file_path=data['file_path'],
            uploaded_by_user_id=data['uploaded_by'],
            file_size=data.get('file_size'),
            mime_type=data.get('mime_type')
        )
        return jsonify(attachment), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error in create_subtask_attachment: {e}")
        return jsonify({"error": str(e)}), 500

# Attachment Routes (General)
@task_bp.route("/attachments/<int:attachment_id>", methods=["DELETE"])
def delete_attachment(attachment_id):
    """Delete an attachment"""
    try:
        print(f"Deleting attachment {attachment_id}")
        
        success = AttachmentService.delete_attachment(attachment_id)
        if success:
            return jsonify({"message": "Attachment deleted successfully"}), 200
        else:
            return jsonify({"error": "Attachment not found"}), 404
    except Exception as e:
        print(f"Error in delete_attachment: {e}")
        return jsonify({"error": str(e)}), 500

# Health check route
@task_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "task_management_with_subtasks"}), 200