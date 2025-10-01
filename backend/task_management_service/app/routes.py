from flask import Blueprint, jsonify, request
from . import service

task_bp = Blueprint("task_bp", __name__)

# ============= TASK ROUTES =============

@task_bp.route("/tasks", methods=["GET"])
def get_all_tasks():
    #Get all tasks, optionally filtered by owner_id
    try:
        owner_id = request.args.get('owner_id', type=int)
        status = request.args.get('status')
        
        print(f"Getting tasks with owner_id={owner_id}, status={status}")
        
        tasks = service.get_all_tasks(owner_id=owner_id, status=status)
        return jsonify(tasks), 200
    except Exception as e:
        print(f"Error in get_all_tasks: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks", methods=["POST"])
def create_task():
    #Create a new task
    try:
        data = request.get_json()
        print(f"Creating task with data: {data}")
        
        if not data or not data.get('title'):
            return jsonify({"error": "Title is required"}), 400
            
        if not data.get('owner_id'):
            return jsonify({"error": "Owner ID is required"}), 400

        new_task = service.create_task(data)
        print(f"Created task: {new_task}")
        return jsonify(new_task), 201
        
    except Exception as e:
        print(f"Error in create_task: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    #Get a specific task with its subtasks, comments, and attachments
    try:
        print(f"Getting task with id={task_id}")
        
        task_details = service.get_task_details(task_id)
        if not task_details:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(task_details), 200
    except Exception as e:
        print(f"Error in get_task: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    #Update a task
    try:
        data = request.get_json()
        print(f"Updating task {task_id} with data: {data}")
        
        # Get the requesting user's ID from the request
        requesting_user_id = data.get('requesting_user_id')
        
        if not requesting_user_id:
            return jsonify({"error": "requesting_user_id is required"}), 400
        
        # Check if task exists and get current task data
        current_task = service.get_task_details(task_id)
        if not current_task:
            return jsonify({"error": "Task not found"}), 404
            
        # Check if user is the owner of the task
        if current_task['owner_id'] != requesting_user_id:
            return jsonify({"error": "Only task owner can edit the task"}), 403
            
        # Check if task is completed (cannot edit completed tasks)
        if current_task['status'] == 'Completed':
            return jsonify({"error": "Cannot edit completed tasks"}), 403
        
        # Remove requesting_user_id from data before update
        update_data = {k: v for k, v in data.items() if k != 'requesting_user_id'}
        
        updated_task = service.update_task(task_id, update_data)
        if not updated_task:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(updated_task), 200
    except Exception as e:
        print(f"Error in update_task: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    #Delete a task
    try:
        print(f"Deleting task with id={task_id}")
        
        success = service.delete_task(task_id)
        if success:
            return jsonify({"message": "Task deleted successfully"}), 200
        else:
            return jsonify({"error": "Task not found"}), 404
    except Exception as e:
        print(f"Error in delete_task: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/status", methods=["PATCH"])
def update_task_status(task_id):
    #Update task status with validation
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        new_status = data.get('status')
        comment = data.get('comment')
        
        print(f"Status update request: task_id={task_id}, user_id={user_id}, status={new_status}")
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        if not new_status:
            return jsonify({"error": "Status is required"}), 400
        
        # Validate status value
        valid_statuses = ['Unassigned', 'Ongoing', 'Under Review', 'Completed']
        if new_status not in valid_statuses:
            return jsonify({"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400
        
        # Check if user is owner or collaborator
        if not service.is_task_collaborator(task_id, user_id):
            return jsonify({"error": "You must be the owner or collaborator to update this task"}), 403
        
        # If marking as completed, verify all subtasks are completed
        if new_status == 'Completed':
            all_completed, incomplete_count = service.check_all_subtasks_completed(task_id)
            if not all_completed:
                return jsonify({
                    "error": f"Cannot mark task as completed. {incomplete_count} subtask(s) still incomplete",
                    "incomplete_subtasks": incomplete_count
                }), 400
        
        # Update the task status
        updated_task = service.update_task_status(task_id, new_status)
        
        # Add comment if provided
        if comment and comment.strip():
            service.add_task_comment(task_id, user_id, comment)
        
        return jsonify({
            "success": True,
            "task": updated_task,
            "message": f"Task status updated to {new_status}"
        }), 200
        
    except Exception as e:
        print(f"Error in update_task_status: {e}")
        return jsonify({"error": str(e)}), 500

# ============= TASK COLLABORATOR ROUTES =============

@task_bp.route("/tasks/<int:task_id>/collaborators", methods=["GET"])
def get_task_collaborators(task_id):
    #Get all collaborators for a task
    try:
        collaborators = service.get_task_collaborators(task_id)
        return jsonify(collaborators), 200
    except Exception as e:
        print(f"Error in get_task_collaborators: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/collaborators", methods=["POST"])
def add_task_collaborator(task_id):
    #Add a collaborator to a task
    try:
        data = request.get_json()
        print(f"Adding collaborator to task {task_id}")
        
        requesting_user_id = data.get('requesting_user_id')
        new_collaborator_id = data.get('collaborator_id')
        
        if not requesting_user_id or not new_collaborator_id:
            return jsonify({"error": "requesting_user_id and collaborator_id are required"}), 400
        
        # Check if user is the owner of the task
        current_task = service.get_task_details(task_id)
        if not current_task:
            return jsonify({"error": "Task not found"}), 404
            
        if current_task['owner_id'] != requesting_user_id:
            return jsonify({"error": "Only task owner can add collaborators"}), 403
        
        result = service.add_task_collaborator(task_id, new_collaborator_id)
        if result:
            return jsonify({"message": "Collaborator added successfully"}), 200
        else:
            return jsonify({"error": "Failed to add collaborator"}), 400
    except Exception as e:
        print(f"Error in add_task_collaborator: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/collaborators/<int:collaborator_id>", methods=["DELETE"])
def remove_task_collaborator(task_id, collaborator_id):
    #Remove a collaborator from a task
    try:
        requesting_user_id = request.args.get('requesting_user_id', type=int)
        
        if not requesting_user_id:
            return jsonify({"error": "requesting_user_id is required"}), 400
        
        # Check if user is the owner of the task
        current_task = service.get_task_details(task_id)
        if not current_task:
            return jsonify({"error": "Task not found"}), 404
            
        if current_task['owner_id'] != requesting_user_id:
            return jsonify({"error": "Only task owner can remove collaborators"}), 403
        
        result = service.remove_task_collaborator(task_id, collaborator_id)
        if result:
            return jsonify({"message": "Collaborator removed successfully"}), 200
        else:
            return jsonify({"error": "Failed to remove collaborator"}), 400
    except Exception as e:
        print(f"Error in remove_task_collaborator: {e}")
        return jsonify({"error": str(e)}), 500

# ============= TASK TRANSFER OWNERSHIP ROUTE =============

@task_bp.route("/tasks/<int:task_id>/transfer", methods=["POST"])
def transfer_task_ownership(task_id):
    #Transfer task ownership to another user
    try:
        data = request.get_json()
        print(f"Transferring task {task_id} ownership")
        
        requesting_user_id = data.get('requesting_user_id')
        requesting_user_role = data.get('requesting_user_role')
        requesting_user_department = data.get('requesting_user_department')
        
        new_owner_id = data.get('new_owner_id')
        new_owner_role = data.get('new_owner_role')
        new_owner_department = data.get('new_owner_department')
        
        if not all([requesting_user_id, requesting_user_role, requesting_user_department, 
                    new_owner_id, new_owner_role, new_owner_department]):
            return jsonify({"error": "All user and role information required"}), 400
        
        # Check if task exists
        current_task = service.get_task_details(task_id)
        if not current_task:
            return jsonify({"error": "Task not found"}), 404
        
        # Check if user is the owner of the task
        if current_task['owner_id'] != requesting_user_id:
            return jsonify({"error": "Only task owner can transfer ownership"}), 403
        
        # Check if task is completed
        if current_task['status'] == 'Completed':
            return jsonify({"error": "Cannot transfer completed tasks"}), 403
        
        # Check role hierarchy for transfer
        role_hierarchy = {'director': 3, 'manager': 2, 'staff': 1}
        
        # Only Manager/Director can transfer tasks
        if requesting_user_role not in ['manager', 'director']:
            return jsonify({"error": "Only Managers and Directors can transfer tasks"}), 403
        
        # Check if transferring to someone in the same department
        if requesting_user_department != new_owner_department:
            return jsonify({"error": "Can only transfer tasks within the same department"}), 403
        
        # Check role hierarchy rules
        requesting_role_level = role_hierarchy.get(requesting_user_role.lower(), 0)
        new_owner_role_level = role_hierarchy.get(new_owner_role.lower(), 0)
        
        # Director can transfer to Manager or Staff
        # Manager can transfer to Staff only (not to Director)
        if requesting_user_role.lower() == 'manager' and new_owner_role.lower() == 'director':
            return jsonify({"error": "Managers cannot transfer tasks to Directors"}), 403
        
        if new_owner_role_level >= requesting_role_level:
            return jsonify({"error": "Can only transfer tasks to users with lower or equal roles"}), 403
        
        # Update task ownership
        updated_data = {'owner_id': new_owner_id}
        updated_task = service.update_task(task_id, updated_data)
        
        if updated_task:
            return jsonify({
                "message": "Task ownership transferred successfully",
                "task": updated_task
            }), 200
        else:
            return jsonify({"error": "Failed to transfer task"}), 400
            
    except Exception as e:
        print(f"Error in transfer_task_ownership: {e}")
        return jsonify({"error": str(e)}), 500

# ============= SUBTASK ROUTES =============

@task_bp.route("/tasks/<int:task_id>/subtasks", methods=["GET"])
def get_task_subtasks(task_id):
    #Get all subtasks for a specific task
    try:
        print(f"Getting subtasks for task {task_id}")
        
        subtasks = service.get_task_subtasks(task_id)
        if subtasks is None:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(subtasks), 200
    except Exception as e:
        print(f"Error in get_task_subtasks: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/subtasks", methods=["POST"])
def create_subtask(task_id):
    #Create a new subtask for a task
    try:
        data = request.get_json()
        print(f"Creating subtask for task {task_id} with data: {data}")
        
        if not data or not data.get('title'):
            return jsonify({"error": "Subtask title is required"}), 400
            
        new_subtask = service.create_subtask(task_id, data)
        if not new_subtask:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(new_subtask), 201
    except Exception as e:
        print(f"Error in create_subtask: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/subtasks/<int:subtask_id>", methods=["GET"])
def get_subtask(task_id, subtask_id):
    #Get a specific subtask
    try:
        print(f"Getting subtask {subtask_id} for task {task_id}")
        
        subtask = service.get_subtask_details(task_id, subtask_id)
        if not subtask:
            return jsonify({"error": "Subtask not found"}), 404
        return jsonify(subtask), 200
    except Exception as e:
        print(f"Error in get_subtask: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/subtasks/<int:subtask_id>", methods=["PUT"])
def update_subtask(task_id, subtask_id):
    #Update a subtask
    try:
        data = request.get_json()
        print(f"Updating subtask {subtask_id} for task {task_id} with data: {data}")
        
        # Get the requesting user's ID from the request
        requesting_user_id = data.get('requesting_user_id')
        
        if not requesting_user_id:
            return jsonify({"error": "requesting_user_id is required"}), 400
        
        # Check if subtask exists and get current data
        current_subtask = service.get_subtask_details(task_id, subtask_id)
        if not current_subtask:
            return jsonify({"error": "Subtask not found"}), 404
            
        # Check if user is the owner of the parent task
        parent_task = service.get_task_details(task_id)
        if parent_task['owner_id'] != requesting_user_id:
            return jsonify({"error": "Only task owner can edit subtasks"}), 403
            
        # Check if subtask is completed
        if current_subtask['status'] == 'Completed':
            return jsonify({"error": "Cannot edit completed subtasks"}), 403
        
        # Remove requesting_user_id from data before update
        update_data = {k: v for k, v in data.items() if k != 'requesting_user_id'}
        
        updated_subtask = service.update_subtask(task_id, subtask_id, update_data)
        if not updated_subtask:
            return jsonify({"error": "Subtask not found"}), 404
        return jsonify(updated_subtask), 200
    except Exception as e:
        print(f"Error in update_subtask: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/subtasks/<int:subtask_id>/status", methods=["PATCH"])
def update_subtask_status(task_id, subtask_id):
    #Update subtask status with validation
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        new_status = data.get('status')
        comment = data.get('comment')
        
        print(f"Subtask status update: task_id={task_id}, subtask_id={subtask_id}, user_id={user_id}, status={new_status}")
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        if not new_status:
            return jsonify({"error": "Status is required"}), 400
        
        # Validate status value
        valid_statuses = ['Unassigned', 'Ongoing', 'Under Review', 'Completed', 'On Hold']
        if new_status not in valid_statuses:
            return jsonify({"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400
        
        # Check if user is owner or collaborator of parent task
        if not service.is_task_collaborator(task_id, user_id):
            return jsonify({"error": "You must be the owner or collaborator to update this subtask"}), 403
        
        # Update the subtask status
        updated_subtask = service.update_subtask_status(task_id, subtask_id, new_status)
        
        if not updated_subtask:
            return jsonify({"error": "Subtask not found"}), 404
        
        # Add comment if provided
        if comment and comment.strip():
            service.add_subtask_comment(task_id, subtask_id, user_id, comment)
        
        return jsonify({
            "success": True,
            "subtask": updated_subtask,
            "message": f"Subtask status updated to {new_status}"
        }), 200
        
    except Exception as e:
        print(f"Error in update_subtask_status: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/subtasks/<int:subtask_id>", methods=["DELETE"])
def delete_subtask(task_id, subtask_id):
    #Delete a subtask
    try:
        print(f"Deleting subtask {subtask_id} from task {task_id}")
        
        subtask = service.get_subtask_details(task_id, subtask_id)
        if not subtask:
            return jsonify({"error": "Subtask not found"}), 404
        
        # In a full implementation, you'd add this method to service.py
        from .models import Subtask, db
        subtask_to_delete = Subtask.query.filter_by(id=subtask_id, task_id=task_id).first()
        if subtask_to_delete:
            db.session.delete(subtask_to_delete)
            db.session.commit()
            return jsonify({"message": "Subtask deleted successfully"}), 200
        else:
            return jsonify({"error": "Subtask not found"}), 404
            
    except Exception as e:
        print(f"Error in delete_subtask: {e}")
        return jsonify({"error": str(e)}), 500

# ============= SUBTASK COLLABORATOR ROUTES =============

@task_bp.route("/tasks/<int:task_id>/subtasks/<int:subtask_id>/collaborators", methods=["GET"])
def get_subtask_collaborators(task_id, subtask_id):
    #Get all collaborators for a subtask
    try:
        collaborators = service.get_subtask_collaborators(subtask_id)
        return jsonify(collaborators), 200
    except Exception as e:
        print(f"Error in get_subtask_collaborators: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/subtasks/<int:subtask_id>/collaborators", methods=["POST"])
def add_subtask_collaborator(task_id, subtask_id):
    #Add a collaborator to a subtask
    try:
        data = request.get_json()
        print(f"Adding collaborator to subtask {subtask_id}")
        
        requesting_user_id = data.get('requesting_user_id')
        new_collaborator_id = data.get('collaborator_id')
        
        if not requesting_user_id or not new_collaborator_id:
            return jsonify({"error": "requesting_user_id and collaborator_id are required"}), 400
        
        # Check if user is the owner of the parent task
        parent_task = service.get_task_details(task_id)
        if not parent_task:
            return jsonify({"error": "Task not found"}), 404
            
        if parent_task['owner_id'] != requesting_user_id:
            return jsonify({"error": "Only task owner can add subtask collaborators"}), 403
        
        result = service.add_subtask_collaborator(subtask_id, new_collaborator_id)
        if result:
            return jsonify({"message": "Collaborator added successfully"}), 200
        else:
            return jsonify({"error": "Failed to add collaborator"}), 400
    except Exception as e:
        print(f"Error in add_subtask_collaborator: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/subtasks/<int:subtask_id>/collaborators/<int:collaborator_id>", methods=["DELETE"])
def remove_subtask_collaborator(task_id, subtask_id, collaborator_id):
    #Remove a collaborator from a subtask
    try:
        requesting_user_id = request.args.get('requesting_user_id', type=int)
        
        if not requesting_user_id:
            return jsonify({"error": "requesting_user_id is required"}), 400
        
        # Check if user is the owner of the parent task
        parent_task = service.get_task_details(task_id)
        if not parent_task:
            return jsonify({"error": "Task not found"}), 404
            
        if parent_task['owner_id'] != requesting_user_id:
            return jsonify({"error": "Only task owner can remove subtask collaborators"}), 403
        
        result = service.remove_subtask_collaborator(subtask_id, collaborator_id)
        if result:
            return jsonify({"message": "Collaborator removed successfully"}), 200
        else:
            return jsonify({"error": "Failed to remove collaborator"}), 400
    except Exception as e:
        print(f"Error in remove_subtask_collaborator: {e}")
        return jsonify({"error": str(e)}), 500

# ============= SUBTASK TRANSFER OWNERSHIP ROUTE =============

@task_bp.route("/tasks/<int:task_id>/subtasks/<int:subtask_id>/transfer", methods=["POST"])
def transfer_subtask_ownership(task_id, subtask_id):
    #Transfer subtask ownership (assignee) to another user
    try:
        data = request.get_json()
        print(f"Transferring subtask {subtask_id} ownership")
        
        requesting_user_id = data.get('requesting_user_id')
        requesting_user_role = data.get('requesting_user_role')
        requesting_user_department = data.get('requesting_user_department')
        
        new_assignee_id = data.get('new_assignee_id')
        new_assignee_role = data.get('new_assignee_role')
        new_assignee_department = data.get('new_assignee_department')
        
        if not all([requesting_user_id, requesting_user_role, requesting_user_department, 
                    new_assignee_id, new_assignee_role, new_assignee_department]):
            return jsonify({"error": "All user and role information required"}), 400
        
        # Check if subtask exists
        current_subtask = service.get_subtask_details(task_id, subtask_id)
        if not current_subtask:
            return jsonify({"error": "Subtask not found"}), 404
        
        # Check if user is the owner of the parent task
        parent_task = service.get_task_details(task_id)
        if parent_task['owner_id'] != requesting_user_id:
            return jsonify({"error": "Only task owner can transfer subtask ownership"}), 403
        
        # Check if subtask is completed
        if current_subtask['status'] == 'Completed':
            return jsonify({"error": "Cannot transfer completed subtasks"}), 403
        
        # Apply same role hierarchy rules
        role_hierarchy = {'director': 3, 'manager': 2, 'staff': 1}
        
        if requesting_user_role not in ['manager', 'director']:
            return jsonify({"error": "Only Managers and Directors can transfer subtasks"}), 403
        
        if requesting_user_department != new_assignee_department:
            return jsonify({"error": "Can only transfer subtasks within the same department"}), 403
        
        # Check role hierarchy rules
        requesting_role_level = role_hierarchy.get(requesting_user_role.lower(), 0)
        new_assignee_role_level = role_hierarchy.get(new_assignee_role.lower(), 0)
        
        # Director can transfer to Manager or Staff
        # Manager can transfer to Staff only (not to Director)
        if requesting_user_role.lower() == 'manager' and new_assignee_role.lower() == 'director':
            return jsonify({"error": "Managers cannot transfer subtasks to Directors"}), 403
        
        if new_assignee_role_level >= requesting_role_level:
            return jsonify({"error": "Can only transfer subtasks to users with lower or equal roles"}), 403
        
        # Update subtask assignee
        updated_data = {'assignee_id': new_assignee_id}
        updated_subtask = service.update_subtask(task_id, subtask_id, updated_data)
        
        if updated_subtask:
            return jsonify({
                "message": "Subtask ownership transferred successfully",
                "subtask": updated_subtask
            }), 200
        else:
            return jsonify({"error": "Failed to transfer subtask"}), 400
            
    except Exception as e:
        print(f"Error in transfer_subtask_ownership: {e}")
        return jsonify({"error": str(e)}), 500

# ============= COMMENT ROUTES =============

@task_bp.route("/tasks/<int:task_id>/comments", methods=["POST"])
def add_task_comment(task_id):
    #Add a comment to a task
    try:
        data = request.get_json()
        
        if not data or not data.get('body'):
            return jsonify({"error": "Comment body is required"}), 400
            
        if not data.get('author_id'):
            return jsonify({"error": "Author ID is required"}), 400
        
        comment = service.add_task_comment(
            task_id, 
            data['author_id'], 
            data['body']
        )
        
        if not comment:
            return jsonify({"error": "Task not found"}), 404
            
        return jsonify(comment), 201
    except Exception as e:
        print(f"Error in add_task_comment: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/comments", methods=["GET"])
def get_task_comments(task_id):
    #Get all comments for a task
    try:
        comments = service.get_task_comments(task_id)
        if comments is None:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(comments), 200
    except Exception as e:
        print(f"Error in get_task_comments: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/subtasks/<int:subtask_id>/comments", methods=["POST"])
def add_subtask_comment(task_id, subtask_id):
    #Add a comment to a subtask
    try:
        data = request.get_json()
        
        if not data or not data.get('body'):
            return jsonify({"error": "Comment body is required"}), 400
            
        if not data.get('author_id'):
            return jsonify({"error": "Author ID is required"}), 400
        
        comment = service.add_subtask_comment(
            task_id,
            subtask_id,
            data['author_id'], 
            data['body']
        )
        
        if not comment:
            return jsonify({"error": "Subtask not found"}), 404
            
        return jsonify(comment), 201
    except Exception as e:
        print(f"Error in add_subtask_comment: {e}")
        return jsonify({"error": str(e)}), 500

# ============= HEALTH CHECK =============

@task_bp.route("/health", methods=["GET"])
def health_check():
    #Health check endpoint
    return jsonify({"status": "healthy", "service": "task_management"}), 200