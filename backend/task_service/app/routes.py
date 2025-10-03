from flask import Blueprint, jsonify, request
from . import service

task_bp = Blueprint("task_bp", __name__)

# Settled
@task_bp.route("/tasks", methods=["GET"])
def get_all_tasks():
    """Get all tasks, optionally filtered by owner_id"""
    try:
        owner_id = request.args.get('owner_id', type=int)
        status = request.args.get('status')
        
        print(f"Getting tasks with owner_id={owner_id}, status={status}")
        
        tasks = service.get_all_tasks(owner_id)

        if tasks is None:
            return jsonify({"error": "Owner ID is required"}), 400

        tasks_json = [task.to_json() for task in tasks]

        return jsonify(tasks_json), 200
    except Exception as e:
        print(f"Error in get_all_tasks: {e}")
        return jsonify({"error": str(e)}), 500

# Not Settled
@task_bp.route("/tasks", methods=["POST"])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        print(f"Creating task with data: {data}")
        
        # Validate required fields
        if not data or not data.get('title'):
            return jsonify({"error": "Title is required"}), 400
            
        if not data.get('owner_id'):
            return jsonify({"error": "Owner ID is required"}), 400
            
        # Create the task using your service
        new_task = service.create_task(data)
        print(f"Created task: {new_task}")
        return jsonify(new_task), 201
        
    except Exception as e:
        print(f"Error in create_task: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    """Get a specific task with its subtasks, comments, and attachments"""
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
    """Update a task"""
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

@task_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete a task"""
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
    """Get all subtasks for a specific task"""
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
    """Create a new subtask for a task"""
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
    """Get a specific subtask"""
    try:
        print(f"Getting subtask {subtask_id} for task {task_id}")
        
        subtask = service.get_subtask_details(task_id, subtask_id)
        if not subtask:
            return jsonify({"error": "Subtask not found"}), 404
        return jsonify(subtask), 200
    except Exception as e:
        print(f"Error in get_subtask: {e}")
        return jsonify({"error": str(e)}), 500

# Health check endpoint
@task_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "task_management"}), 200