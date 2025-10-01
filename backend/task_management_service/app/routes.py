from flask import Blueprint, jsonify, request
from . import service

task_bp = Blueprint("task_bp", __name__)

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
        
        #Validate required fields
        if not data or not data.get('title'):
            return jsonify({"error": "Title is required"}), 400
            
        if not data.get('owner_id'):
            return jsonify({"error": "Owner ID is required"}), 400

        #create the task using service    
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
        
        updated_task = service.update_task(task_id, data)
        if not updated_task:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(updated_task), 200
    except Exception as e:
        print(f"Error in update_task: {e}")
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

@task_bp.route("/tasks/<int:task_id>/comments", methods=["POST"])
def add_comment(task_id):
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
        print(f"Error in add_comment: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/comments", methods=["GET"])
def get_comments(task_id):
    #Get all comments for a task
    try:
        comments = service.get_task_comments(task_id)
        if comments is None:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(comments), 200
    except Exception as e:
        print(f"Error in get_comments: {e}")
        return jsonify({"error": str(e)}), 500

# Health check endpoint
@task_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "task_management"}), 200

