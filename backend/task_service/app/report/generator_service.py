# In: backend/task_service/app/report/generator_service.py

import os
import requests  # <-- ADD THIS IMPORT
from flask import current_app  # <-- ADD THIS IMPORT
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from datetime import datetime
from .. import models
from .. import service

# --- Configuration ---
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = Environment(loader=FileSystemLoader(template_dir))

# --- User Helper Functions (THE CORRECTED VERSION) ---
def _fetch_user_details(user_id):
    """
    Fetches user details by making a real API call to the user_service.
    """
    try:
        # Get the User Service URL from the Flask config
        # We set a default, but it's better to set this in config.py
        user_service_url = current_app.config.get('USER_SERVICE_URL', 'http://spm_user_service:6000')
        
        # Make the API call
        response = requests.get(f"{user_service_url}/user/{user_id}", timeout=5)
        
        # Check if the request was successful
        if response.status_code == 200:
            user_data = response.json()
            # Return the data in the format the report expects
            return {
                "id": user_data.get("id"),
                "name": user_data.get("name", f"User {user_id}")
            }
        else:
            # User not found or service error
            print(f"Error fetching user {user_id}: {response.status_code}")
            return {"id": user_id, "name": f"User {user_id} (Not Found)"}
            
    except requests.exceptions.RequestException as e:
        # Handle connection errors, timeouts, etc.
        print(f"API call failed for user {user_id}: {e}")
        return {"id": user_id, "name": f"User {user_id} (Service Down?)"}
    except Exception as e:
        print(f"Error fetching details for user {user_id}: {e}")
        return {"id": user_id, "name": f"User {user_id} (Error)"}

# --- Main Report Generation Function ---
def generate_project_pdf_report(project_id: int, user_id: int):
    """
    Generates a PDF report for a specific project.
    ... (rest of the function stays exactly the same) ...
    """
    print(f"Generating report for Project ID: {project_id}, requested by User ID: {user_id}")

    # --- 1. Fetch Project and Authorize ---
    try:
        # This part remains the same
        project, error = service.get_project_by_id(project_id, user_id)
        if error:
            print(f"Authorization error or project not found: {error}")
            return None
        if not project:
             print(f"Project with ID {project_id} not found.")
             return None
        
        # This logic remains the same
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
        # This part remains the same
        tasks_in_project = models.Task.query.filter(
            models.Task.project_id == project_id,
            models.Task.parent_task_id.is_(None)
        ).order_by(models.Task.deadline.asc().nullslast()).all()
        print(f"Found {len(tasks_in_project)} parent tasks for project {project_id}.")
    except Exception as e:
        print(f"Error fetching tasks for project {project_id}: {e}")
        tasks_in_project = []

    # --- 3. Process Data for Template ---
    # This entire section (looping through tasks, caching users, etc.)
    # remains exactly the same. It will now call your *new*
    # _fetch_user_details function.
    
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

        tasks_data.append({
            'title': task.title,
            'status': status_value,
            'deadline': task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else 'N/A',
            'owner_name': owner_name,
            'collaborator_names': ", ".join(collaborators_on_task) or "None",
            'priority': task.priority or 'N/A',
            'is_overdue': task in overdue_tasks
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

    context = {
        "report_title": f"Project Report: {project_title}",
        "generation_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "project_owner": project_owner_name,
        "project_collaborators": ", ".join(project_collaborator_names) or "None",
        "tasks": tasks_data,
        "status_counts": status_counts,
        "total_tasks": len(tasks_in_project),
        "overdue_count": len(overdue_tasks),
    }

    # --- 4. Render HTML Template ---
    # This part remains the same
    try:
        template = jinja_env.get_template('project_report_template.html')
        html_string = template.render(context)
    except Exception as e:
        print(f"Error rendering HTML template: {e}")
        return f"<html><body><h1>Template Error</h1><p>{e}</p></body></html>".encode('utf-8')

    # --- 5. Generate PDF ---
    # This part remains the same
    try:
        css_string = """
            body { font-family: sans-serif; font-size: 12px; }
            h1, h2 { color: #333; border-bottom: 1px solid #eee; padding-bottom: 5px;}
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #ccc; padding: 6px; text-align: left; }
            th { background-color: #f2f2f2; font-weight: bold; }
            .overdue { color: red; font-weight: bold; }
        """
        
        pdf_bytes = HTML(string=html_string).write_pdf(stylesheets=[CSS(string=css_string)])
        print(f"Successfully generated PDF ({len(pdf_bytes)} bytes) for project {project_id}.")
        return pdf_bytes

    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None

def generate_individual_pdf_report(project_id: int, user_id: int):
    """
    Generates a PDF report for a specific project.
    ... (rest of the function stays exactly the same) ...
    """
    print(f"Generating report for Project ID: {project_id}, requested by User ID: {user_id}")

    # --- 1. Fetch Project and Authorize ---
    try:
        # This part remains the same
        project, error = service.get_project_by_id(project_id, user_id)
        if error:
            print(f"Authorization error or project not found: {error}")
            return None
        if not project:
             print(f"Project with ID {project_id} not found.")
             return None
        
        # This logic remains the same
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
        # This part remains the same
        tasks_in_project = models.Task.query.filter(
            models.Task.project_id == project_id,
            models.Task.parent_task_id.is_(None)
        ).order_by(models.Task.deadline.asc().nullslast()).all()
        print(f"Found {len(tasks_in_project)} parent tasks for project {project_id}.")
    except Exception as e:
        print(f"Error fetching tasks for project {project_id}: {e}")
        tasks_in_project = []

    # --- 3. Process Data for Template ---
    # This entire section (looping through tasks, caching users, etc.)
    # remains exactly the same. It will now call your *new*
    # _fetch_user_details function.
    
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

        tasks_data.append({
            'title': task.title,
            'status': status_value,
            'deadline': task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else 'N/A',
            'owner_name': owner_name,
            'collaborator_names': ", ".join(collaborators_on_task) or "None",
            'priority': task.priority or 'N/A',
            'is_overdue': task in overdue_tasks
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

    context = {
        "report_title": f"Project Report: {project_title}",
        "generation_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "project_owner": project_owner_name,
        "project_collaborators": ", ".join(project_collaborator_names) or "None",
        "tasks": tasks_data,
        "status_counts": status_counts,
        "total_tasks": len(tasks_in_project),
        "overdue_count": len(overdue_tasks),
    }

    # --- 4. Render HTML Template ---
    # This part remains the same
    try:
        template = jinja_env.get_template('project_report_template.html')
        html_string = template.render(context)
    except Exception as e:
        print(f"Error rendering HTML template: {e}")
        return f"<html><body><h1>Template Error</h1><p>{e}</p></body></html>".encode('utf-8')

    # --- 5. Generate PDF ---
    # This part remains the same
    try:
        css_string = """
            body { font-family: sans-serif; font-size: 12px; }
            h1, h2 { color: #333; border-bottom: 1px solid #eee; padding-bottom: 5px;}
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #ccc; padding: 6px; text-align: left; }
            th { background-color: #f2f2f2; font-weight: bold; }
            .overdue { color: red; font-weight: bold; }
        """
        
        pdf_bytes = HTML(string=html_string).write_pdf(stylesheets=[CSS(string=css_string)])
        print(f"Successfully generated PDF ({len(pdf_bytes)} bytes) for project {project_id}.")
        return pdf_bytes

    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None