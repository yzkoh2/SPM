from flask import Blueprint, jsonify
from . import service

task_bp = Blueprint("task_bp", __name__)

@task_bp.route("/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task_details = service.get_task_details(task_id)
    if not task_details:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task_details), 200
