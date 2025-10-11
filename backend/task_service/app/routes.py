from flask import Blueprint, jsonify, request
from . import service

task_bp = Blueprint("task_bp", __name__)

# Settled
# Health check endpoint
@task_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "task_management"}), 200

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

@task_bp.route("/tasks", methods=["POST"])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        print(f"Creating task with data: {data}")
        
        # Validate required fields
        if not data or not data.get('title'):
            return jsonify({"error": "Missing field: Title"}), 400
            
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

        user_id = data.pop('user_id', None)
        
        updated_task, message = service.update_task(task_id, user_id, data)
        if updated_task is None:
            if "not found" in message:
                return jsonify({"error": message}), 404
            elif "Forbidden" in message:
                return jsonify({"error": message}), 403
            else:
                return jsonify({"error": message}), 400 
        return jsonify(updated_task), 200
    
    except Exception as e:
        print(f"Error in update_task: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete a task"""
    try:
        print(f"Deleting task with id={task_id}")
        data = request.get_json()
        user_id = data.get('user_id') if data else None
        success, message = service.delete_task(task_id, user_id)
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 404
    except Exception as e:
        print(f"Error in delete_task: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/comments", methods=["POST"])
def add_comment(task_id):
    """Add a comment to a task"""
    try:
        data = request.get_json()
        print(f"Adding comment to task {task_id} with data: {data}")
        
        if not data or not data.get('body') or not data.get('author_id'):
            return jsonify({"error": "Comment body and author_id are required"}), 400
            
        new_comment = service.add_comment(task_id, data)
        if not new_comment:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(new_comment), 201
    except Exception as e:
        print(f"Error in add_comment: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/deletecomment/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    """Delete a comment"""
    try:
        print(f"Deleting comment with id={comment_id}")
        
        success = service.delete_comment(comment_id)
        if success:
            return jsonify({"message": "Comment deleted successfully"}), 200
        else:
            return jsonify({"error": "Comment not found"}), 404
    except Exception as e:
        print(f"Error in delete_comment: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/collaborators", methods=["GET"])
def get_task_subtask_collaborators(task_id):
    #Get all collaborators for a task/subtask
    try:
        collaborators = service.get_task_collaborators(task_id)
        return jsonify(collaborators), 200
    except Exception as e:
        print(f"Error in get_task_collaborators: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route('/tasks/<int:task_id>/collaborators', methods=['POST'])
def add_collaborator_route(task_id):
    data = request.get_json()
    collaborator_ids = data.get('collaborator_ids')
    requested_by = data.get('requested_by')

    if not collaborator_ids or not requested_by:
        return jsonify({"error": "Missing collaborator_ids"}), 400

    try:
        service.add_task_collaborators(task_id, collaborator_ids, requested_by)
        return jsonify({"message": "Collaborator added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@task_bp.route('/tasks/<int:task_id>/collaborators', methods=['DELETE'])
def remove_collaborator_route(task_id):
    data = request.get_json()
    collaborator_ids = data.get('collaborator_id')
    requested_by = data.get('requested_by')

    if not collaborator_ids or not requested_by:
        return jsonify({"error": "Missing collaborator_id"}), 400

    try:
        service.remove_task_collaborator(task_id, collaborator_ids, requested_by)
        return jsonify({"message": "Collaborator removed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/attachments", methods=["POST"])
def add_attachment_route(task_id):
    """Handles file upload to S3 and adds attachment to a task"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = request.form.get('filename')

    try:
        new_attachment = service.add_attachment(task_id, file, filename)
        if not new_attachment:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(new_attachment), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/attachments/<int:attachment_id>", methods=["GET"])
def get_attachment_route(task_id, attachment_id):
    """Get a specific attachment for a task"""
    try:
        attachment, message = service.get_attachment_url(task_id, attachment_id)
        if not attachment:
            return jsonify({"error": message}), 404
        return jsonify(attachment), 200
    except Exception as e:
        print(f"Error in get_attachment: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>/attachments/<int:attachment_id>", methods=["DELETE"])
def delete_attachment_route(task_id, attachment_id):
    """Delete an attachment from a task"""
    try:
        success, message = service.delete_attachment_url(task_id, attachment_id)
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 404
    except Exception as e:
        print(f"Error in delete_attachment: {e}")
        return jsonify({"error": str(e)}), 500
# Not Settled
# ==================== PROJECT ROUTES ====================

@task_bp.route("/projects", methods=["POST"])
def create_project():
    """Create a new project"""
    try:
        data = request.get_json()
        print(f"Creating project with data: {data}")
        
        # Validate required fields
        if not data or not data.get('title'):
            return jsonify({"error": "Title is required"}), 400
            
        if not data.get('owner_id'):
            return jsonify({"error": "Owner ID is required"}), 400
            
        new_project = service.create_project(data)
        return jsonify(new_project), 201
        
    except Exception as e:
        print(f"Error in create_project: {e}")
        return jsonify({"error": str(e)}), 500


@task_bp.route("/projects/<int:project_id>", methods=["GET"])
def get_project(project_id):
    """Get a specific project"""
    try:
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        project, error = service.get_project_by_id(project_id, user_id)
        
        if error:
            if "not found" in error:
                return jsonify({"error": error}), 404
            else:
                return jsonify({"error": error}), 403
        
        return jsonify(project.to_json()), 200
        
    except Exception as e:
        print(f"Error in get_project: {e}")
        return jsonify({"error": str(e)}), 500


@task_bp.route("/projects/<int:project_id>/dashboard", methods=["GET"])
def get_project_dashboard(project_id):
    """
    Get project dashboard with tasks, collaborators, and filtering/sorting
    
    Query parameters:
    - user_id (required): ID of the requesting user
    - status: Filter tasks by status (comma-separated, e.g., "Ongoing,Under Review")
    - sort_by: Sort tasks by field (deadline, title, status, priority). Default: deadline
    - collaborator: If 'me', show only tasks where user is a collaborator
    - owner: If 'me', show only tasks where user is the owner
    
    Example: /projects/1/dashboard?user_id=2&status=Ongoing,Under Review&sort_by=deadline&owner=me
    """
    try:
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        # Get filter and sort parameters
        status_filter = request.args.get('status')
        sort_by = request.args.get('sort_by', 'deadline')
        collaborator_filter = request.args.get('collaborator')
        owner_filter = request.args.get('owner')
        
        dashboard_data, error = service.get_project_dashboard(
            project_id=project_id,
            user_id=user_id,
            status_filter=status_filter,
            sort_by=sort_by,
            collaborator_filter=collaborator_filter,
            owner_filter=owner_filter
        )
        
        if error:
            if "not found" in error:
                return jsonify({"error": error}), 404
            else:
                return jsonify({"error": error}), 403
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        print(f"Error in get_project_dashboard: {e}")
        return jsonify({"error": str(e)}), 500


@task_bp.route("/projects/user/<int:user_id>", methods=["GET"])
def get_user_projects(user_id):
    """
    Get all projects for a user
    
    Query parameters:
    - role: Filter by role ('owner', 'collaborator', or omit for all)
    
    Example: /projects/user/2?role=owner
    """
    try:
        role_filter = request.args.get('role')
        
        projects = service.get_user_projects(user_id, role_filter)
        return jsonify(projects), 200
        
    except Exception as e:
        print(f"Error in get_user_projects: {e}")
        return jsonify({"error": str(e)}), 500


@task_bp.route("/projects/<int:project_id>", methods=["PUT"])
def update_project(project_id):
    """Update a project (only owner can update)"""
    try:
        data = request.get_json()
        print(f"Updating project {project_id} with data: {data}")
        
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        updated_project, error = service.update_project(project_id, user_id, data)
        
        if error:
            if "not found" in error:
                return jsonify({"error": error}), 404
            else:
                return jsonify({"error": error}), 403
        
        return jsonify(updated_project), 200
        
    except Exception as e:
        print(f"Error in update_project: {e}")
        return jsonify({"error": str(e)}), 500


@task_bp.route("/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    """Delete a project (only owner can delete)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        success, error = service.delete_project(project_id, user_id)
        
        if error:
            if "not found" in error:
                return jsonify({"error": error}), 404
            else:
                return jsonify({"error": error}), 403
        
        return jsonify({"message": "Project deleted successfully"}), 200
        
    except Exception as e:
        print(f"Error in delete_project: {e}")
        return jsonify({"error": str(e)}), 500


@task_bp.route("/projects/<int:project_id>/collaborators", methods=["POST"])
def add_project_collaborator(project_id):
    """Add a collaborator to a project"""
    try:
        data = request.get_json()
        print(f"Adding collaborator to project {project_id} with data: {data}")
        
        user_id = data.get('user_id')  # The user making the request (must be owner)
        collaborator_user_id = data.get('collaborator_user_id')  # The user to add
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        if not collaborator_user_id:
            return jsonify({"error": "Collaborator user ID is required"}), 400
        
        result, error = service.add_project_collaborator(
            project_id, user_id, collaborator_user_id
        )
        
        if error:
            if "not found" in error:
                return jsonify({"error": error}), 404
            elif "already" in error:
                return jsonify({"error": error}), 409
            else:
                return jsonify({"error": error}), 403
        
        return jsonify(result), 201
        
    except Exception as e:
        print(f"Error in add_project_collaborator: {e}")
        return jsonify({"error": str(e)}), 500


@task_bp.route("/projects/<int:project_id>/collaborators/<int:collaborator_user_id>", methods=["DELETE"])
def remove_project_collaborator(project_id, collaborator_user_id):
    """Remove a collaborator from a project"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')  # The user making the request (must be owner)
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        result, error = service.remove_project_collaborator(
            project_id, user_id, collaborator_user_id
        )
        
        if error:
            if "not found" in error:
                return jsonify({"error": error}), 404
            else:
                return jsonify({"error": error}), 403
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error in remove_project_collaborator: {e}")
        return jsonify({"error": str(e)}), 500
    
# ==================== PROJECT TASK MANAGEMENT ROUTES ====================
@task_bp.route("/projects/<int:project_id>/tasks", methods=["GET"])
def get_project_tasks(project_id):
    """
    Get all tasks for a project
    """
    try:
        tasks, error = service.get_project_tasks(project_id)
        if error:
            if "not found" in error:
                return jsonify({"error": error}), 404
            else:
                return jsonify({"error": error}), 403
        
        tasks_json = [task.to_json() for task in tasks]
        return jsonify(tasks_json), 200
        
    except Exception as e:
        print(f"Error in get_project_tasks: {e}")
        return jsonify({"error": str(e)}), 500

@task_bp.route("/projects/<int:project_id>/tasks", methods=["POST"])
def create_task_in_project(project_id):
    """
    Create a new task directly within a project
    User must be project owner or collaborator
    """
    try:
        data = request.get_json()
        print(f"Creating task in project {project_id} with data: {data}")
        
        user_id = data.get('user_id') or data.get('owner_id')
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        if not data.get('title'):
            return jsonify({"error": "Task title is required"}), 400
        
        new_task, error = service.create_task_in_project(data, project_id, user_id)
        
        if error:
            if "not found" in error:
                return jsonify({"error": error}), 404
            else:
                return jsonify({"error": error}), 403
        
        return jsonify(new_task), 201
        
    except Exception as e:
        print(f"Error in create_task_in_project: {e}")
        return jsonify({"error": str(e)}), 500


@task_bp.route("/tasks/<int:task_id>/add-to-project", methods=["POST"])
def add_existing_task_to_project(task_id):
    """
    Add an existing standalone task to a project
    User must be the task owner
    
    Body: { "project_id": 1, "user_id": 2 }
    """
    try:
        data = request.get_json()
        print(f"Adding task {task_id} to project with data: {data}")
        
        user_id = data.get('user_id')
        project_id = data.get('project_id')
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        if not project_id:
            return jsonify({"error": "Project ID is required"}), 400
        
        updated_task, error = service.add_existing_task_to_project(task_id, project_id, user_id)
        
        if error:
            if "not found" in error:
                return jsonify({"error": error}), 404
            elif "already assigned" in error:
                return jsonify({"error": error}), 409
            else:
                return jsonify({"error": error}), 403
        
        return jsonify(updated_task), 200
        
    except Exception as e:
        print(f"Error in add_existing_task_to_project: {e}")
        return jsonify({"error": str(e)}), 500


@task_bp.route("/tasks/<int:task_id>/remove-from-project", methods=["POST"])
def remove_task_from_project(task_id):
    """
    Unassign a task from its project
    User must be the task owner
    
    Body: { "user_id": 2 }
    """
    try:
        data = request.get_json()
        print(f"Removing task {task_id} from project")
        
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        updated_task, error = service.remove_task_from_project(task_id, user_id)
        
        if error:
            if "not found" in error:
                return jsonify({"error": error}), 404
            elif "not assigned" in error:
                return jsonify({"error": error}), 400
            else:
                return jsonify({"error": error}), 403
        
        return jsonify(updated_task), 200
        
    except Exception as e:
        print(f"Error in remove_task_from_project: {e}")
        return jsonify({"error": str(e)}), 500


@task_bp.route("/tasks/standalone", methods=["GET"])
def get_standalone_tasks():
    """
    Get all standalone tasks (not assigned to any project) for a user
    Query parameter: user_id
    """
    try:
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        tasks = service.get_standalone_tasks_for_user(user_id)
        return jsonify(tasks), 200
        
    except Exception as e:
        print(f"Error in get_standalone_tasks: {e}")
        return jsonify({"error": str(e)}), 500