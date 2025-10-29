import os
import requests
import matplotlib
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from collections import defaultdict
from flask import current_app
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import datetime, timedelta
from .. import models
from .. import service as task_service
from sqlalchemy import or_, and_
import numpy as np # Import numpy for bar charts

# Set matplotlib backend to 'Agg' to avoid GUI issues in a server environment
matplotlib.use('Agg')

# --- Configuration ---
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = Environment(loader=FileSystemLoader(template_dir))

# --- Chart Generation Helpers ---

def _generate_pie_chart_base64(data_dict, title):
    """Generates a Base64-encoded pie chart from a dictionary."""
    filtered_data = {k: v for k, v in data_dict.items() if v > 0}
    if not filtered_data:
        return None

    labels = filtered_data.keys()
    values = filtered_data.values()

    try:
        fig, ax = plt.subplots(figsize=(5, 3.5))
        colors = plt.cm.Paired(range(len(values)))
        wedges, texts, autotexts = ax.pie(
            values, 
            autopct='%1.1f%%', 
            startangle=90,
            colors=colors,
            textprops={'fontsize': 8}
        )
        ax.axis('equal')
        plt.title(title, fontsize=12, pad=10)
        ax.legend(
            wedges, labels, title="Categories", 
            loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize='small'
        )
        
        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', transparent=True)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close(fig)
        return img_base64
    except Exception as e:
        print(f"Error generating pie chart '{title}': {e}")
        plt.close()
        return None

def _generate_hbar_chart_base64(data_dict, title):
    """Generates a Base64-encoded horizontal bar chart for priority (1-10)."""
    try:
        labels = [f"P{i}" for i in range(1, 11)]
        values = [data_dict.get(i, 0) for i in range(1, 11)]

        fig, ax = plt.subplots(figsize=(5, 3.5))
        y_pos = np.arange(len(labels))
        
        ax.barh(y_pos, values, align='center', color='#3498db')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=8)
        ax.invert_yaxis()
        ax.set_xlabel('Task Count', fontsize=9)
        plt.title(title, fontsize=12, pad=10)
        
        for i, v in enumerate(values):
            if v > 0:
                ax.text(v + 0.1, i, str(v), color='black', fontsize=8, va='center')
        
        plt.tight_layout()

        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', transparent=True)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close(fig)
        return img_base64
    except Exception as e:
        print(f"Error generating bar chart '{title}': {e}")
        plt.close()
        return None

# --- User Helper Function ---
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
                "name": user_data.get("name", f"User {user_id}"),
                "role": user_data.get("role", "Unknown")
            }
        else:
            print(f"Error fetching user {user_id}: {response.status_code}")
            return {"id": user_id, "name": f"User {user_id} (Not Found)", "role": "Unknown"}

    except requests.exceptions.RequestException as e:
        print(f"API call failed for user {user_id}: {e}")
        return {"id": user_id, "name": f"User {user_id} (Service Down?)", "role": "Unknown"}
    except Exception as e:
        print(f"Error fetching details for user {user_id}: {e}")
        return {"id": user_id, "name": f"User {user_id} (Error)", "role": "Unknown"}


# --- Main Report Generation Function ---
def generate_project_pdf_report(project_id: int, user_id: int, start_date: datetime = None, end_date: datetime = None):
    """
    Generates a PDF report for a specific project including activity logs,
    collaborator stats, and generated graphs.
    """
    print(f"Generating activity report for Project ID: {project_id}, requested by User ID: {user_id}")
    print(f"Time range: {start_date} to {end_date}")

    user_cache = {} 

    # --- 1. Fetch Project and Authorize ---
    try:
        project, error = task_service.get_project_by_id(project_id, user_id)
        if error:
            print(f"Authorization error or project not found: {error}")
            return None, f"Error: {error}"
        if not project:
            print(f"Project with ID {project_id} not found.")
            return None, "Project not found."

        if isinstance(project, dict):
             project_model = models.Project.query.get(project_id)
             if not project_model: return None, "Project model not found after initial fetch."
             project = project_model 
        
        project_title = project.title
        project_description = project.description
        project_deadline = project.deadline.strftime('%Y-%m-%d %H:%M') if project.deadline else 'N/A'
        project_owner_id = project.owner_id
        # Get the full list of collaborator IDs for the project
        project_collaborator_ids = project.collaborator_ids() 

    except Exception as e:
        print(f"Error fetching project {project_id}: {e}")
        return None, f"Could not fetch project details: {e}"

    # --- 2. Fetch Project Details (Owner & Collaborator Names) ---
    # Pre-fetch all collaborator details and store in cache
    if project_owner_id not in user_cache:
        user_cache[project_owner_id] = _fetch_user_details(project_owner_id)
    project_owner_name = user_cache[project_owner_id]['name']

    project_collaborator_names = []
    for collab_id in project_collaborator_ids:
        if collab_id not in user_cache:
            user_cache[collab_id] = _fetch_user_details(collab_id)
        if collab_id != project_owner_id:
             project_collaborator_names.append(user_cache[collab_id]['name'])

    project_details = {
        'title': project_title,
        'description': project_description,
        'deadline': project_deadline,
        'owner_name': project_owner_name,
        'collaborator_names': ", ".join(project_collaborator_names) or "None",
    }

    # --- 3. Fetch Relevant Tasks ---
    try:
        # This query is date-range dependent
        query = models.Task.query.filter(
            models.Task.project_id == project_id
        )
        if start_date and end_date:
            print(f"Applying date filter to tasks: {start_date} to {end_date}")
            query = query.filter(
                or_(
                    and_(models.Task.updated_at >= start_date, models.Task.updated_at <= end_date),
                    and_(models.Task.created_at >= start_date, models.Task.created_at <= end_date)
                )
            )
        else:
            print("No date filter provided. Fetching all tasks for project metrics.")

        relevant_tasks = query.order_by(models.Task.deadline.asc().nullslast()).all()
        print(f"Found {len(relevant_tasks)} relevant tasks for metrics.")
    
    except Exception as e:
        print(f"Error fetching relevant tasks for project {project_id}: {e}")
        return None, f"Could not fetch tasks: {e}"

    # --- 4. Calculate Section 1 Metrics & Collaborator Stats ---
    now_utc = datetime.utcnow() 
    status_distribution = {status.value: 0 for status in models.TaskStatusEnum}
    priority_distribution = {p: 0 for p in range(1, 11)} 
    overdue_tasks_list = []
    
    collaborator_stats = defaultdict(lambda: {
        'total_tasks': 0, 'main_tasks': 0, 'sub_tasks': 0,
        'in_progress': 0, 'under_review': 0, 'completed': 0
    })

    # --- THIS IS THE FIX ---
    # Pre-populate the dictionary with ALL project collaborators from Step 1.
    # This ensures everyone is in the list, even if they have 0 tasks.
    for collab_id in project_collaborator_ids:
        # By simply accessing the key, the defaultdict creates the
        # default (all zeros) entry if it doesn't exist.
        _ = collaborator_stats[collab_id]
    # --- END OF FIX ---

    # Now, loop through the date-filtered tasks and increment stats
    for task in relevant_tasks:
        # --- Standard Metrics ---
        status_distribution[task.status.value] += 1
        if task.priority and 1 <= task.priority <= 10:
            priority_distribution[task.priority] += 1

        # --- Overdue Logic ---
        if task.deadline and task.deadline.replace(tzinfo=None) < now_utc.replace(tzinfo=None) and task.status != models.TaskStatusEnum.COMPLETED:
            if task.owner_id not in user_cache:
                 user_cache[task.owner_id] = _fetch_user_details(task.owner_id)
            owner_name = user_cache[task.owner_id]['name']
            task_type = "Subtask" if task.parent_task_id is not None else "Task"
            overdue_tasks_list.append({
                'title': task.title,
                'deadline': task.deadline.strftime('%Y-%m-%d %H:%M'),
                'owner_name': owner_name,
                'status': task.status.value,
                'task_type': task_type
            })
            
        # --- Collaborator Stats Logic ---
        task_owner_id = task.owner_id
        # Check if the task owner is in our pre-populated list
        if task_owner_id in collaborator_stats:
            stats = collaborator_stats[task_owner_id]
            stats['total_tasks'] += 1
            if task.parent_task_id is None:
                stats['main_tasks'] += 1
            else:
                stats['sub_tasks'] += 1
            if task.status == models.TaskStatusEnum.ONGOING:
                stats['in_progress'] += 1
            elif task.status == models.TaskStatusEnum.UNDER_REVIEW:
                stats['under_review'] += 1
            elif task.status == models.TaskStatusEnum.COMPLETED:
                stats['completed'] += 1

    # --- 5. Format Metrics and Generate Charts ---
    
    section1_metrics = {
        'status_distribution': status_distribution,
        'priority_distribution': dict(sorted(priority_distribution.items())),
        'overdue_tasks': overdue_tasks_list,
        'overdue_count': len(overdue_tasks_list),
        'total_relevant_tasks': len(relevant_tasks)
    }

    # --- CHART GENERATION ---
    charts = {
        'status_chart': _generate_pie_chart_base64(status_distribution, "Task Status Distribution"),
        'priority_chart': _generate_hbar_chart_base64(
            priority_distribution, 
            "Task Priority Distribution (1-10)"
        )
    }
    
    # --- COLLABORATOR STATS & AVERAGE CALCULATION ---
    collaborator_stats_formatted = []
    total_project_tasks = 0
    total_project_completed = 0
    
    # This loop now iterates over ALL collaborators
    for user_id, stats in collaborator_stats.items():
        total = stats['total_tasks']
        completed = stats['completed']
        rate = (completed / total * 100) if total > 0 else 0
        
        # We only count tasks from the relevant period for the average
        total_project_tasks += total
        total_project_completed += completed
        
        collaborator_stats_formatted.append({
            # Use the pre-fetched user cache
            'name': user_cache.get(user_id, {}).get('name', f"User {user_id}"),
            'total_tasks': total,
            'main_tasks': stats['main_tasks'],
            'sub_tasks': stats['sub_tasks'],
            'in_progress': stats['in_progress'],
            'under_review': stats['under_review'],
            'completed': completed,
            'completion_rate': round(rate, 1)
        })
    
    collaborator_stats_formatted.sort(key=lambda x: x['name'])
    
    average_completion_rate = (total_project_completed / total_project_tasks * 100) if total_project_tasks > 0 else 0

    # --- 6. Fetch Section 2 Activity Details ---
    try:
        activity_query = models.TaskActivityLog.query.join(models.Task).filter(
            models.Task.project_id == project_id
        )
        if start_date and end_date:
            print(f"Applying date filter to activity logs.")
            activity_query = activity_query.filter(
                models.TaskActivityLog.timestamp >= start_date,
                models.TaskActivityLog.timestamp <= end_date
            )
        else:
            print("No date filter for activity logs. Fetching all logs.")

        activity_logs = activity_query.order_by(
            models.TaskActivityLog.task_id, 
            models.TaskActivityLog.timestamp.asc()
        ).all()
        print(f"Found {len(activity_logs)} activity log entries in the date range.")
    except Exception as e:
        print(f"Error fetching activity logs for project {project_id}: {e}")
        return None, f"Could not fetch activity logs: {e}"

    section2_details = []
    task_titles_cache = {} 
    for log in activity_logs:
        task_id = log.task_id
        if task_id not in task_titles_cache:
             task = models.Task.query.get(task_id)
             task_titles_cache[task_id] = task.title if task else f"Task {task_id}"
        task_title = task_titles_cache[task_id]

        user_id_changed = log.user_id
        if user_id_changed not in user_cache:
            user_cache[user_id_changed] = _fetch_user_details(user_id_changed)
        user_name_changed = user_cache[user_id_changed]['name']

        section2_details.append({
            'task_id': task_id,
            'task_title': task_title,
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'user_name': user_name_changed,
            'field_changed': log.field_changed.replace('_', ' ').title(),
            'old_value': log.old_value if log.old_value != "None" else "-",
            'new_value': log.new_value if log.new_value != "None" else "-",
        })

    # --- 7. Prepare Template Context ---
    report_period_str = "All Time"
    if start_date and end_date:
        report_period_str = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

    context = {
        "report_title": f"Project Activity Report: {project_title}",
        "project_details": project_details,
        "report_period": report_period_str,
        "generation_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "section1": section1_metrics,
        "collaborator_stats": collaborator_stats_formatted, 
        "average_completion_rate": round(average_completion_rate, 1),
        "section2": section2_details,
        "charts": charts,
    }

    # --- 8. Render HTML Template ---
    try:
        # *** Pointing to the correct, final template ***
        template = jinja_env.get_template('project_report_template.html')
        html_string = template.render(context)
        
    except Exception as e:
        print(f"Error rendering HTML template: {e}")
        error_html = f"<html><body><h1>Template Rendering Error</h1><p>{e}</p><p>NOTE: Ensure 'project_report_template.html' exists.</p></body></html>"
        return error_html.encode('utf-8'), f"Template Error: {e}"

    # --- 9. Generate PDF ---
    try:
        pdf_bytes = HTML(string=html_string).write_pdf()
        print(f"Successfully generated PDF ({len(pdf_bytes)} bytes) for project {project_id}.")
        return pdf_bytes, None # Return PDF bytes and no error

    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None, f"PDF Generation Error: {e}"