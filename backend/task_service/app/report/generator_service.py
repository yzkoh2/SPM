import os
import requests
from flask import current_app
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML  # <-- We won't use CSS, but WeasyPrint is still needed
from datetime import datetime
from .. import models
from .. import service
from sqlalchemy import or_

# --- Configuration ---
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = Environment(loader=FileSystemLoader(template_dir))

# --- User Helper Functions (THE CORRECTED VERSION) ---
def _fetch_user_details(user_id):
    """
    Fetches user details by making a real API call to the user_service.
    """
    try:
        user_service_url = current_app.config.get('USER_SERVICE_URL', 'http://spm_user_service:6000')
        response = requests.get(f"{user_service_url}/user/{user_id}", timeout=5)
        
        if response.status_code == 200:
            user_data = response.json()
            return {
                "id": user_data.get("id"),
                "name": user_data.get("name", f"User {user_id}")
            }
        else:
            print(f"Error fetching user {user_id}: {response.status_code}")
            return {"id": user_id, "name": f"User {user_id} (Not Found)"}
            
    except requests.exceptions.RequestException as e:
        print(f"API call failed for user {user_id}: {e}")
        return {"id": user_id, "name": f"User {user_id} (Service Down?)"}
    except Exception as e:
        print(f"Error fetching details for user {user_id}: {e}")
        return {"id": user_id, "name": f"User {user_id} (Error)"}

# --- Main Report Generation Function ---
def generate_project_pdf_report(project_id: int, user_id: int, start_date: datetime = None, end_date: datetime = None):
    """
    Generates a PDF report for a specific project.
    """
    print(f"Generating report for Project ID: {project_id}, requested by User ID: {user_id}")
    if start_date and end_date:
        print(f"Filtering report from {start_date} to {end_date}")

    # --- 1. Fetch Project and Authorize ---
    try:
        project, error = service.get_project_by_id(project_id, user_id)
        if error:
            print(f"Authorization error or project not found: {error}")
            return None
        if not project:
             print(f"Project with ID {project_id} not found.")
             return None
        
        if isinstance(project, dict):
            project_model = models.Project.query.get(project_id)
            if not project_model: return None
            project_title = project.get('title', 'Unknown Project')
            project_owner_id = project.get('owner_id')
            project_collaborator_ids = project.get('collaborator_ids', [])
        else:
            project_model = project
            project_title = project_model.title
            project_owner_id = project_model.owner_id
            project_collaborator_ids = project_model.collaborator_ids()

    except Exception as e:
        print(f"Error fetching project {project_id}: {e}")
        return None

    # --- 2. Fetch Tasks for the Project ---
    try:
        # Start with the base query for the project's parent tasks
        query = models.Task.query.filter(
            models.Task.project_id == project_id,
            models.Task.parent_task_id.is_(None)
        )

        # --- MODIFIED: Apply date filter if provided ---
        if start_date and end_date:
            # We filter for tasks that were EITHER created OR completed in this window.
            # Assumes your Task model has 'created_at' and 'completed_at' fields.
            query = query.filter(
                or_(
                    (models.Task.updated_at >= start_date) & (models.Task.updated_at <= end_date),
                    (models.Task.completed_at >= start_date) & (models.Task.completed_at <= end_date)
                )
            )
        
        # Execute the query
        tasks_in_project = query.order_by(models.Task.deadline.asc().nullslast()).all()
        print(f"Found {len(tasks_in_project)} parent tasks for project {project_id} in the date range.")
    
    except Exception as e:
        print(f"Error fetching tasks for project {project_id}: {e}")
        tasks_in_project = []

    # --- 3. Process Data for Template ---
    now = datetime.utcnow()
    status_counts = {status.value: 0 for status in models.TaskStatusEnum}
    overdue_tasks = []
    tasks_data = []
    user_cache = {} 

    for task in tasks_in_project:
        status_value = task.status.value
        status_counts[status_value] += 1

        # Overdue logic should check against 'now', regardless of filter
        if task.deadline and task.deadline.replace(tzinfo=None) < now.replace(tzinfo=None) and task.status != models.TaskStatusEnum.COMPLETED:
            overdue_tasks.append(task)

        if task.owner_id not in user_cache:
            user_cache[task.owner_id] = _fetch_user_details(task.owner_id)
        owner_name = user_cache[task.owner_id]['name']

        collaborators_on_task = []
        for collab_id in task.collaborator_ids():
             if collab_id not in user_cache:
                 user_cache[collab_id] = _fetch_user_details(collab_id)
             if collab_id != task.owner_id:
                 collaborators_on_task.append(user_cache[collab_id]['name'])
        
        # --- MODIFICATION: REMOVED 'duration' ---
        # This field is no longer relevant as we are filtering, not calculating.
        # Your template should only have 6 columns.
        tasks_data.append({
            'title': task.title,
            'status': status_value,
            'deadline': task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else 'N/A',
            'owner_name': owner_name,
            'collaborator_names': ", ".join(collaborators_on_task) or "None",
            'priority': task.priority,
            'is_overdue': task in overdue_tasks
            # 'duration' field removed
        })

    if project_owner_id not in user_cache:
        user_cache[project_owner_id] = _fetch_user_details(project_owner_id)
    project_owner_name = user_cache[project_owner_id]['name']

    project_collaborator_names = []
    for collab_id in project_collaborator_ids:
        if collab_id not in user_cache:
            user_cache[collab_id] = _fetch_user_details(collab_id)
        if collab_id != project_owner_id:
             project_collaborator_names.append(user_cache[collab_id]['name'])

    # --- MODLIFICATION: Set 'report_period' based on filter dates ---
    report_period_str = "All Time"
    if start_date and end_date:
        report_period_str = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

    context = {
        "report_title": f"Project Report: {project_title}",
        "project_name": project_title,
        "report_period": report_period_str,   # <-- MODIFIED
        "generation_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "project_owner": project_owner_name,
        "project_collaborators": ", ".join(project_collaborator_names) or "None",
        "tasks": tasks_data,
        "status_counts": status_counts,
        "total_tasks": len(tasks_in_project),
        "overdue_count": len(overdue_tasks),
    }

    # --- 4. Render HTML Template ---
    try:
        template = jinja_env.get_template('project_report_template.html')
        html_string = template.render(context)
    except Exception as e:
        print(f"Error rendering HTML template: {e}")
        return f"<html><body><h1>Template Error</h1><p>{e}</p></body></html>".encode('utf-8')

    # --- 5. Generate PDF ---
    try:
        pdf_bytes = HTML(string=html_string).write_pdf()
        print(f"Successfully generated PDF ({len(pdf_bytes)} bytes) for project {project_id}.")
        return pdf_bytes

    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None
# ==================================================================
# NOTE: The function below was identical to the one above.
# I have applied the same template fixes to it.
# ==================================================================

def generate_individual_pdf_report(project_id: int, user_id: int):
    """
    Generates a PDF report for a specific project.
    ... (rest of the function stays exactly the same) ...
    """
    print(f"Generating report for Project ID: {project_id}, requested by User ID: {user_id}")

    # --- 1. Fetch Project and Authorize ---
    try:
        project, error = service.get_project_by_id(project_id, user_id)
        if error:
            print(f"Authorization error or project not found: {error}")
            return None
        if not project:
             print(f"Project with ID {project_id} not found.")
             return None
        
        if isinstance(project, dict):
            project_model = models.Project.query.get(project_id)
            if not project_model: return None
            project_title = project.get('title', 'Unknown Project')
            project_owner_id = project.get('owner_id')
            project_collaborator_ids = project.get('collaborator_ids', [])
        else:
            project_model = project
            project_title = project_model.title
            project_owner_id = project_model.owner_id
            project_collaborator_ids = project_model.collaborator_ids()

    except Exception as e:
        print(f"Error fetching project {project_id}: {e}")
        return None

    # --- 2. Fetch Tasks for the Project ---
    try:
        tasks_in_project = models.Task.query.filter(
            models.Task.project_id == project_id,
            models.Task.parent_task_id.is_(None)
        ).order_by(models.Task.deadline.asc().nullslast()).all()
        print(f"Found {len(tasks_in_project)} parent tasks for project {project_id}.")
    except Exception as e:
        print(f"Error fetching tasks for project {project_id}: {e}")
        tasks_in_project = []

    # --- 3. Process Data for Template ---
    now = datetime.utcnow()
    status_counts = {status.value: 0 for status in models.TaskStatusEnum}
    overdue_tasks = []
    tasks_data = []
    user_cache = {} 

    for task in tasks_in_project:
        status_value = task.status.value
        status_counts[status_value] += 1

        if task.deadline and task.deadline.replace(tzinfo=None) < now.replace(tzinfo=None) and task.status != models.TaskStatusEnum.COMPLETED:
            overdue_tasks.append(task)

        if task.owner_id not in user_cache:
            user_cache[task.owner_id] = _fetch_user_details(task.owner_id)
        owner_name = user_cache[task.owner_id]['name']

        collaborators_on_task = []
        for collab_id in task.collaborator_ids():
             if collab_id not in user_cache:
                 user_cache[collab_id] = _fetch_user_details(collab_id)
             if collab_id != task.owner_id:
                 collaborators_on_task.append(user_cache[collab_id]['name'])

        # --- MODIFICATION: ADDED 'duration' ---
        task_duration = "N/A" # TODO: Add real duration logic

        tasks_data.append({
            'title': task.title,
            'status': status_value,
            'deadline': task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else 'N/A',
            'owner_name': owner_name,
            'collaborator_names': ", ".join(collaborators_on_task) or "None",
            'priority': task.priority, # Pass the number
            'is_overdue': task in overdue_tasks,
            'duration': task_duration # <-- ADDED
        })

    if project_owner_id not in user_cache:
        user_cache[project_owner_id] = _fetch_user_details(project_owner_id)
    project_owner_name = user_cache[project_owner_id]['name']

    project_collaborator_names = []
    for collab_id in project_collaborator_ids:
        if collab_id not in user_cache:
            user_cache[collab_id] = _fetch_user_details(collab_id)
        if collab_id != project_owner_id:
             project_collaborator_names.append(user_cache[collab_id]['name'])

    # --- MODIFICATION: ADDED 'project_name' and 'report_period' ---
    context = {
        "report_title": f"Project Report: {project_title}",
        "project_name": project_title, # <-- ADDED
        "report_period": "All Time",   # <-- ADDED
        "generation_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "project_owner": project_owner_name,
        "project_collaborators": ", ".join(project_collaborator_names) or "None",
        "tasks": tasks_data,
        "status_counts": status_counts,
        "total_tasks": len(tasks_in_project),
        "overdue_count": len(overdue_tasks),
    }

    # --- 4. Render HTML Template ---
    try:
        # NOTE: This is still pointing to 'project_report_template.html'.
        # If this function is for an INDIVIDUAL report, you should 
        # create and use 'individual_report_template.html' here.
        template = jinja_env.get_template('project_report_template.html')
        html_string = template.render(context)
    except Exception as e:
        print(f"Error rendering HTML template: {e}")
        return f"<html><body><h1>Template Error</h1><p>{e}</p></body></html>".encode('utf-8')

    # --- 5. Generate PDF ---
    try:
        # --- MODIFICATION: REMOVED OLD CSS ---
        pdf_bytes = HTML(string=html_string).write_pdf() # <-- MODIFIED
        
        print(f"Successfully generated PDF ({len(pdf_bytes)} bytes) for project {project_id}.")
        return pdf_bytes

    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None