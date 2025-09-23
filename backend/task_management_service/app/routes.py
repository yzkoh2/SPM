from flask import Blueprint, jsonify, request
from . import service

task_bp = Blueprint("task_bp", name)

@task_bp.route("/", methods=["GET"])
def get_all_tasks():
    """Get all tasks, optionally filtered by owner_id"""
    owner_id = request.args.get('owner_id', type=int)
    status = request.args.get('status')
    
    tasks = service.get_all_tasks(owner_id=owner_id, status=status)
    return jsonify(tasks), 200

# for testing will be removed or placed here for future needs
# Get a specific task by ID
@task_bp.route("/<int:task_id>", methods=["GET"])
def get_task(task_id):
    """Get a specific task with its subtasks, comments, and attachments"""
    task_details = service.get_task_details(task_id)
    if not task_details:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task_details), 200