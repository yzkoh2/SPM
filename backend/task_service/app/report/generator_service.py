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
import numpy as np
import pytz

# Set matplotlib backend
matplotlib.use('Agg')

# --- Configuration ---
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = Environment(loader=FileSystemLoader(template_dir))

# --- Chart Generation Helpers ---
# (Keep _generate_pie_chart_base64 and _generate_hbar_chart_base64 functions as they are)
def _generate_pie_chart_base64(data_dict, title):
    """Generates a Base64-encoded pie chart from a dictionary."""
    filtered_data = {k: v for k, v in data_dict.items() if v > 0}
    if not filtered_data: return None
    labels = filtered_data.keys(); values = filtered_data.values()
    try:
        fig, ax = plt.subplots(figsize=(5, 3.5)); colors = plt.cm.Paired(range(len(values)))
        wedges, texts, autotexts = ax.pie(values, autopct='%1.1f%%', startangle=90, colors=colors, textprops={'fontsize': 8})
        ax.axis('equal'); plt.title(title, fontsize=12, pad=10)
        ax.legend(wedges, labels, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize='small')
        buf = BytesIO(); fig.savefig(buf, format='png', bbox_inches='tight', transparent=True); buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8'); buf.close(); plt.close(fig)
        return img_base64
    except Exception as e: print(f"Error generating pie chart '{title}': {e}"); plt.close(); return None

def _generate_hbar_chart_base64(data_dict, title):
    """Generates a Base64-encoded horizontal bar chart for priority (1-10)."""
    try:
        labels = [f"P{i}" for i in range(1, 11)]; values = [data_dict.get(i, 0) for i in range(1, 11)]
        fig, ax = plt.subplots(figsize=(5, 3.5)); y_pos = np.arange(len(labels))
        ax.barh(y_pos, values, align='center', color='#3498db'); ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=8); ax.invert_yaxis()
        ax.set_xlabel('Task Count', fontsize=9); plt.title(title, fontsize=12, pad=10)
        for i, v in enumerate(values):
            if v > 0: ax.text(v + 0.1, i, str(v), color='black', fontsize=8, va='center')
        plt.tight_layout()
        buf = BytesIO(); fig.savefig(buf, format='png', bbox_inches='tight', transparent=True); buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8'); buf.close(); plt.close(fig)
        return img_base64
    except Exception as e: print(f"Error generating bar chart '{title}': {e}"); plt.close(); return None

# --- Fetch User Helper Function ---
def _fetch_user_details(user_id):
    """Fetches user details by making a real API call to the user_service."""
    try:
        user_service_url = current_app.config.get('USER_SERVICE_URL', 'http://spm_user_service:6000')
        response = requests.get(f"{user_service_url}/user/{user_id}", timeout=5)
        if response.status_code == 200:
            user_data = response.json(); return {"id": user_data.get("id"), "name": user_data.get("name", f"User {user_id}"), "role": user_data.get("role", "Unknown")}
        else: print(f"Error fetching user {user_id}: {response.status_code}"); return {"id": user_id, "name": f"User {user_id} (Not Found)", "role": "Unknown"}
    except requests.exceptions.RequestException as e: print(f"API call failed for user {user_id}: {e}"); return {"id": user_id, "name": f"User {user_id} (Service Down?)", "role": "Unknown"}
    except Exception as e: print(f"Error fetching details for user {user_id}: {e}"); return {"id": user_id, "name": f"User {user_id} (Error)", "role": "Unknown"}


# Helper to get task state as of a specific date in UTC
def get_task_state_as_of(task, end_date_utc):
    """
    Determines the task's status, priority, and owner as of a specific end_date (UTC)
    by starting from the task's CURRENT state and "rewinding" logs back to the end_date.
    Returns a dictionary {'status': TaskStatusEnum, 'priority': int, 'owner_id': int}
    or None if the task didn't exist at end_date_utc.
    """
    utc_tz = pytz.utc

    # Localize task creation time if naive
    task_created_at_utc = task.created_at
    if task_created_at_utc.tzinfo is None:
        task_created_at_utc = utc_tz.localize(task_created_at_utc)

    # If the task was created AFTER the 'as_of' date, it didn't exist yet.
    # Handle the edge case where end_date_utc might be None (report for "current time")
    if end_date_utc and task_created_at_utc > end_date_utc:
        return None # Indicate task didn't exist

    # --- 1. Start with the task's CURRENT state ---
    # The 'task' object holds the most recent values.
    state = {
        'status': task.status,
        'priority': task.priority if task.priority is not None else 5,
        'owner_id': task.owner_id
    }

    # --- 2. Fetch logs that happened AFTER the cutoff date ---
    # These are the changes we need to undo.
    logs_to_rewind = models.TaskActivityLog.query.filter(
        models.TaskActivityLog.task_id == task.id,
        # Only get logs that are *after* the date we care about
        models.TaskActivityLog.timestamp > end_date_utc
    ).order_by(models.TaskActivityLog.timestamp.desc()).all() # Newest first

    # --- 3. Replay logs in reverse (rewind) ---
    # By applying the 'old_value' from each log, we revert the state.
    for log in logs_to_rewind:
        field = log.field_changed
        old_value_str = log.old_value # Use the old_value to rewind

        if field == 'status':
            if old_value_str == 'None':
                 state['status'] = models.TaskStatusEnum.UNASSIGNED # Revert to default
            else:
                 try: state['status'] = models.TaskStatusEnum(old_value_str)
                 except ValueError: pass # Keep previous state if invalid enum
        elif field == 'priority':
             if old_value_str == 'None':
                 state['priority'] = 5 # Revert to default
             else:
                 try: state['priority'] = int(old_value_str)
                 except (ValueError, TypeError): pass # Keep previous state
        elif field == 'owner_id':
             if old_value_str == 'None': continue # Cannot have None owner
             try: state['owner_id'] = int(old_value_str)
             except (ValueError, TypeError): pass # Keep previous state
        # Add elif for other fields if needed

    # --- 4. Final state validation ---
    # The state dictionary now holds the values as they were at end_date_utc
    if not (isinstance(state['priority'], int) and 1 <= state['priority'] <= 10):
         state['priority'] = 5 # Fallback to default if invalid

    if not isinstance(state['status'], models.TaskStatusEnum):
        # Fallback to the task's original status if rewind fails
        state['status'] = task.status if isinstance(task.status, models.TaskStatusEnum) else models.TaskStatusEnum.UNASSIGNED

    return state


def generate_project_pdf_report(project_id: int, user_id: int, start_date: datetime = None, end_date: datetime = None, timezone_str: str = "UTC"):
    """
    Generates a PDF report snapshot as of end_date, activity log for date range,
    and lists non-completed tasks as of end_date.
    start_date and end_date are expected in UTC for querying.
    timezone_str is used for display formatting.
    """
    print(f"Generating activity report for Project ID: {project_id}, requested by User ID: {user_id}")
    print(f"Querying data range (UTC): {start_date} to {end_date}")
    print(f"Displaying times in timezone: {timezone_str}")
    print(f"Report snapshot as of: {end_date or 'Current Time (UTC)'}")

    # --- 0. Setup Timezone Objects ---
    try:
        user_tz = pytz.timezone(timezone_str) # <-- Uses corrected timezone_str
    except pytz.exceptions.UnknownTimeZoneError:
        print(f"Unknown timezone '{timezone_str}'. Defaulting to UTC.")
        user_tz = pytz.utc; timezone_str = "UTC" # Correct the string
    utc_tz = pytz.utc
    
    as_of_date_utc = end_date or utc_tz.localize(datetime.utcnow())

    def convert_to_user_tz(utc_dt):
        if not utc_dt: return 'N/A'
        dt_to_convert = utc_dt
        if isinstance(utc_dt, str):
            try: dt_to_convert = datetime.fromisoformat(utc_dt.replace('Z', '+00:00'))
            except ValueError: return 'Invalid Date'
        if dt_to_convert.tzinfo is None:
            dt_to_convert = utc_tz.localize(dt_to_convert)
        return dt_to_convert.astimezone(user_tz).strftime('%Y-%m-%d %H:%M:%S')

    user_cache = {} 

    # --- 1. Fetch Project and Authorize ---
    try:
        project, error = task_service.get_project_by_id(project_id, user_id)
        if error: return None, f"Error: {error}"
        if not project: return None, "Project not found."
        if isinstance(project, dict):
             project_model = models.Project.query.get(project_id)
             if not project_model: return None, "Project model not found after initial fetch."
             project = project_model 
        
        project_title = project.title
        project_description = project.description
        project_deadline = project.deadline
        project_owner_id = project.owner_id
        project_collaborator_ids = project.collaborator_ids() 
    except Exception as e: print(f"Error fetching project {project_id}: {e}"); return None, f"Could not fetch project details: {e}"

    # --- 2. Fetch Project Details (Owner & Collaborator Names) ---
    if project_owner_id not in user_cache: user_cache[project_owner_id] = _fetch_user_details(project_owner_id)
    project_owner_name = user_cache[project_owner_id]['name']
    project_collaborator_names = []
    for collab_id in project_collaborator_ids:
        if collab_id not in user_cache: user_cache[collab_id] = _fetch_user_details(collab_id)
        project_collaborator_names.append(user_cache[collab_id]['name'])
    unique_collaborator_names = sorted(list(set(project_collaborator_names)))
    project_details = {
        'title': project_title, 'description': project_description,
        'deadline': convert_to_user_tz(project_deadline),
        'owner_name': project_owner_name,
        'collaborator_names': ", ".join(unique_collaborator_names) or "None",
    }

    # --- 3. Fetch ALL Tasks for the Project (Needed for "As Of" calculations) ---
    try:
        all_project_tasks = models.Task.query.filter(models.Task.project_id == project_id).all()
        print(f"Fetched {len(all_project_tasks)} total tasks for project {project_id}.")
    except Exception as e:
        print(f"Error fetching all tasks for project {project_id}: {e}")
        return None, f"Could not fetch tasks: {e}"

    # --- 4. Calculate "As Of" Metrics (Section 1) & Prepare Section 3 Data ---
    status_distribution_as_of = {status.value: 0 for status in models.TaskStatusEnum}
    priority_distribution_as_of = {p: 0 for p in range(1, 11)} 
    overdue_tasks_as_of_list = []
    section3_tasks = [] 

    collaborator_stats_as_of = defaultdict(lambda: {
        'total_tasks': 0, 'main_tasks': 0, 'sub_tasks': 0,
        'in_progress': 0, 'under_review': 0, 'completed': 0
    })
    for collab_id in project_collaborator_ids: _ = collaborator_stats_as_of[collab_id] 

    print(f"DEBUG: generator - Received start_date (UTC): {start_date}")
    print(f"DEBUG: generator - Received end_date (UTC): {end_date}") # <-- Check this value carefully!
    print(f"DEBUG: generator - Received timezone_str: {timezone_str}")
    print(f"DEBUG: generator - Calculated as_of_date_utc: {as_of_date_utc}")

    for task in all_project_tasks:
        state_as_of = get_task_state_as_of(task, as_of_date_utc)
        status_as_of = state_as_of['status']
        priority_as_of = state_as_of['priority']
        owner_id_as_of = state_as_of['owner_id']
        
        status_distribution_as_of[status_as_of.value] += 1
        if priority_as_of and 1 <= priority_as_of <= 10:
            priority_distribution_as_of[priority_as_of] += 1

        task_deadline_utc = task.deadline
        if task_deadline_utc and task_deadline_utc.tzinfo is None: task_deadline_utc = utc_tz.localize(task_deadline_utc)
        is_overdue_as_of = task_deadline_utc and task_deadline_utc < as_of_date_utc and status_as_of != models.TaskStatusEnum.COMPLETED
        
        if is_overdue_as_of:
            if owner_id_as_of not in user_cache: user_cache[owner_id_as_of] = _fetch_user_details(owner_id_as_of)
            owner_name_as_of = user_cache[owner_id_as_of]['name']
            task_type = "Subtask" if task.parent_task_id is not None else "Task"
            overdue_tasks_as_of_list.append({
                'title': task.title, 'deadline': convert_to_user_tz(task.deadline),
                'owner_name': owner_name_as_of, 'status': status_as_of.value, 'task_type': task_type
            })

        if owner_id_as_of in collaborator_stats_as_of:
            stats = collaborator_stats_as_of[owner_id_as_of]
            stats['total_tasks'] += 1
            if task.parent_task_id is None: stats['main_tasks'] += 1
            else: stats['sub_tasks'] += 1
            if status_as_of == models.TaskStatusEnum.ONGOING: stats['in_progress'] += 1
            elif status_as_of == models.TaskStatusEnum.UNDER_REVIEW: stats['under_review'] += 1
            elif status_as_of == models.TaskStatusEnum.COMPLETED: stats['completed'] += 1
            
        if status_as_of != models.TaskStatusEnum.COMPLETED:
            if owner_id_as_of not in user_cache: user_cache[owner_id_as_of] = _fetch_user_details(owner_id_as_of)
            owner_name_as_of = user_cache[owner_id_as_of]['name']
            task_type = "Subtask" if task.parent_task_id is not None else "Task"
            section3_tasks.append({
                 'title': task.title, 'task_type': task_type, 'owner_name': owner_name_as_of,
                 'deadline': convert_to_user_tz(task.deadline), 'status': status_as_of.value,
                 'priority': priority_as_of or '-', 'is_overdue_as_of': is_overdue_as_of
            })

    section3_tasks.sort(key=lambda x: (x['deadline'] == 'N/A', x['deadline'], x['priority'] == '-', x['priority']))


    # --- 5. Format Metrics and Generate Charts ---
    section1_metrics = {
        'status_distribution': status_distribution_as_of,
        'priority_distribution': dict(sorted(priority_distribution_as_of.items())),
        'overdue_tasks': overdue_tasks_as_of_list,
        'overdue_count': len(overdue_tasks_as_of_list),
        'total_relevant_tasks': len(all_project_tasks) 
    }

    charts = {
        'status_chart': _generate_pie_chart_base64(status_distribution_as_of, f"Task Status (As of {as_of_date_utc.strftime('%Y-%m-%d')})"),
        'priority_chart': _generate_hbar_chart_base64(priority_distribution_as_of, f"Task Priority (As of {as_of_date_utc.strftime('%Y-%m-%d')})")
    }
    
    collaborator_stats_formatted = []
    total_project_tasks_as_of = 0
    total_project_completed_as_of = 0
    for user_id, stats in collaborator_stats_as_of.items():
        total = stats['total_tasks']; completed = stats['completed']
        rate = (completed / total * 100) if total > 0 else 0
        total_project_tasks_as_of += total; total_project_completed_as_of += completed
        collaborator_stats_formatted.append({
            'name': user_cache.get(user_id, {}).get('name', f"User {user_id}"),
            'total_tasks': total, 'main_tasks': stats['main_tasks'], 'sub_tasks': stats['sub_tasks'],
            'in_progress': stats['in_progress'], 'under_review': stats['under_review'],
            'completed': completed, 'completion_rate': round(rate, 1)
        })
    collaborator_stats_formatted.sort(key=lambda x: x['name'])
    average_completion_rate_as_of = (total_project_completed_as_of / total_project_tasks_as_of * 100) if total_project_tasks_as_of > 0 else 0

    # --- 6. Fetch Section 2 Activity Details (Uses original start_date/end_date for range) ---
    section2_details = []
    if start_date and end_date: 
        try:
            activity_query = models.TaskActivityLog.query.join(models.Task).filter(
                models.Task.project_id == project_id,
                models.TaskActivityLog.timestamp >= start_date, 
                models.TaskActivityLog.timestamp <= end_date    
            )
            activity_logs = activity_query.order_by(models.TaskActivityLog.task_id, models.TaskActivityLog.timestamp.asc()).all()
            print(f"Found {len(activity_logs)} activity log entries in the date range {start_date} to {end_date}.")

            task_titles_cache = {} 
            for log in activity_logs:
                task_id = log.task_id
                if task_id not in task_titles_cache:
                    task = models.Task.query.get(task_id); task_titles_cache[task_id] = task.title if task else f"Task {task_id}"
                task_title = task_titles_cache[task_id]
                user_id_changed = log.user_id
                if user_id_changed not in user_cache: user_cache[user_id_changed] = _fetch_user_details(user_id_changed)
                user_name_changed = user_cache[user_id_changed]['name']
                section2_details.append({
                    'task_id': task_id, 'task_title': task_title,
                    'timestamp': convert_to_user_tz(log.timestamp), 
                    'user_name': user_name_changed, 'field_changed': log.field_changed.replace('_', ' ').title(),
                    'old_value': log.old_value if log.old_value != "None" else "-",
                    'new_value': log.new_value if log.new_value != "None" else "-",
                })
        except Exception as e: print(f"Error fetching activity logs for project {project_id}: {e}"); return None, f"Could not fetch activity logs: {e}"
    else:
        print("No date range provided, skipping Section 2 Activity Log.")


    # --- 7. Prepare Template Context ---
    report_period_str = f"{convert_to_user_tz(as_of_date_utc)}"
    activity_period_str = "N/A"
    if start_date and end_date:
        activity_period_str = f"{start_date.astimezone(user_tz).strftime('%Y-%m-%d')} to {end_date.astimezone(user_tz).strftime('%Y-%m-%d')}"

    generation_date_user_tz = datetime.now(user_tz).strftime('%Y-%m-%d %H:%M:%S %Z')

    context = {
        "report_title": f"Project Report: {project_title}",
        "project_details": project_details,
        "report_period": report_period_str, 
        "activity_period": activity_period_str, 
        "generation_date": generation_date_user_tz,
        "section1": section1_metrics,
        "collaborator_stats": collaborator_stats_formatted, 
        "average_completion_rate": round(average_completion_rate_as_of, 1),
        "section2": section2_details,
        "section3_tasks": section3_tasks, 
        "charts": charts,
    }

    # --- 8. Render HTML Template ---
    try:
        # *** FIX 2: Pointing to the correct final template ***
        template = jinja_env.get_template('project_report_template.html') # Ensure this file exists
        html_string = template.render(context)
    except Exception as e:
        print(f"Error rendering HTML template: {e}")
        error_html = f"<html><body><h1>Template Rendering Error</h1><p>{e}</p><p>NOTE: Ensure 'project_report_template.html' exists and is correct.</p></body></html>"
        return error_html.encode('utf-8'), f"Template Error: {e}"

    # --- 9. Generate PDF ---
    try:
        pdf_bytes = HTML(string=html_string).write_pdf()
        print(f"Successfully generated PDF ({len(pdf_bytes)} bytes) for project {project_id}.")
        return pdf_bytes, None 
    except Exception as e: print(f"Error generating PDF: {e}"); return None, f"PDF Generation Error: {e}"