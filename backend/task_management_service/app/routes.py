from flask import Blueprint, jsonify, request
from . import service

task_bp = Blueprint("task_bp", __name__)

@task_bp.route("/", methods=["GET"])
def get_all_tasks():
    """Get all tasks, optionally filtered by owner_id for dashboard"""
    owner_id = request.args.get('owner_id', type=int)
    status = request.args.get('status')
    
    tasks = service.get_all_tasks(owner_id=owner_id, status=status)
    return jsonify(tasks), 200

@task_bp.route("/<int:task_id>", methods=["GET"])
def get_task_details(task_id):
    """Get detailed view of a specific task - for individual task page"""
    task_details = service.get_task_details(task_id)
    if not task_details:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task_details), 200