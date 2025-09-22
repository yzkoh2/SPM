from flask import Blueprint, jsonify, request
from . import service

task_bp = Blueprint("task_bp", __name__)

@task_bp.route("/", methods=["GET"])
def get_all_tasks():
    """Get all tasks, optionally filtered by owner_id"""
    owner_id = request.args.get('owner_id', type=int)
    status = request.args.get('status')
    
    tasks = service.get_all_tasks(owner_id=owner_id, status=status)
    return jsonify(tasks), 200

# Get a specific task by ID
@task_bp.route("/<int:task_id>", methods=["GET"])
def get_task(task_id):
    """Get a specific task with its subtasks, comments, and attachments"""
    task_details = service.get_task_details(task_id)
    if not task_details:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task_details), 200

# Get all subtasks for a specific task
@task_bp.route("/<int:task_id>/subtasks", methods=["GET"])
def get_task_subtasks(task_id):
    """Get all subtasks for a specific task"""
    subtasks = service.get_task_subtasks(task_id)
    if subtasks is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(subtasks), 200

# Get a specific subtask
@task_bp.route("/<int:task_id>/subtasks/<int:subtask_id>", methods=["GET"])
def get_subtask(task_id, subtask_id):
    """Get a specific subtask"""
    subtask = service.get_subtask_details(task_id, subtask_id)
    if not subtask:
        return jsonify({"error": "Subtask not found"}), 404
    return jsonify(subtask), 200
