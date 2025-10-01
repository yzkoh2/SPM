from flask import Blueprint, request, jsonify
from .service import ProjectService
from .models import db

project_bp = Blueprint('projects', __name__)

@project_bp.route('/projects', methods=['POST'])
def create_project():
    """
    Create a new project
    Expected JSON body:
    {
        "name": "Project Name",
        "description": "Project description",
        "deadline": "2025-12-31T23:59:59",  // Optional, ISO format
        "user_id": 123  // The creator/owner's user ID
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        name = data.get('name')
        user_id = data.get('user_id')
        
        if not name:
            return jsonify({"error": "Project name is required"}), 400
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        # Create project using service
        project = ProjectService.create_project(
            name=name,
            description=data.get('description'),
            deadline=data.get('deadline'),
            owner_id=user_id
        )
        
        return jsonify({
            "message": "Project created successfully",
            "project": project.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create project: {str(e)}"}), 500


@project_bp.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """
    Update project details
    Expected JSON body:
    {
        "name": "Updated Project Name",  // Optional
        "description": "Updated description",  // Optional
        "deadline": "2025-12-31T23:59:59",  // Optional
        "user_id": 123  // Required for authorization check
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        # Update project using service
        project = ProjectService.update_project(
            project_id=project_id,
            user_id=user_id,
            name=data.get('name'),
            description=data.get('description'),
            deadline=data.get('deadline')
        )
        
        return jsonify({
            "message": "Project updated successfully",
            "project": project.to_dict()
        }), 200
        
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update project: {str(e)}"}), 500


@project_bp.route('/projects/user/<int:user_id>', methods=['GET'])
def get_user_projects(user_id):
    """
    Get all projects a user is involved in (as owner or collaborator)
    Query parameters:
    - role: Filter by role (optional) e.g., ?role=owner or ?role=collaborator
    """
    try:
        role_filter = request.args.get('role')  # Optional: 'owner', 'collaborator', or None for all
        
        projects = ProjectService.get_user_projects(user_id, role_filter)
        
        return jsonify({
            "user_id": user_id,
            "total_projects": len(projects),
            "projects": projects
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch projects: {str(e)}"}), 500


@project_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """
    Get a specific project by ID
    """
    try:
        project = ProjectService.get_project_by_id(project_id)
        
        return jsonify({
            "project": project.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to fetch project: {str(e)}"}), 500


@project_bp.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """
    Delete a project (only owner can delete)
    Expected JSON body:
    {
        "user_id": 123  // Required for authorization check
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        ProjectService.delete_project(project_id, user_id)
        
        return jsonify({
            "message": "Project deleted successfully"
        }), 200
        
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete project: {str(e)}"}), 500