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
import uuid
from botocore.exceptions import BotoCoreError, ClientError
from werkzeug.utils import secure_filename

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
            user_data = response.json(); 
            return {"id": user_data.get("id"), "name": user_data.get("name", f"User {user_id}"), "role": user_data.get("role", "Unknown")}
        else: 
            print(f"Error fetching user {user_id}: {response.status_code}"); return {"id": user_id, "name": f"User {user_id} (Not Found)", "role": "Unknown"}
    except requests.exceptions.RequestException as e: 
        print(f"API call failed for user {user_id}: {e}"); return {"id": user_id, "name": f"User {user_id} (Service Down?)", "role": "Unknown"}
    except Exception as e: 
        print(f"Error fetching details for user {user_id}: {e}"); return {"id": user_id, "name": f"User {user_id} (Error)", "role": "Unknown"}


# Helper to get task state as of a specific date in UTC
# Helper to get task state as of a specific date in UTC
def get_task_state_as_of(task, end_date_utc):
    """
    [REPLAY METHOD] Determines the task's status, priority, and owner as of a 
    specific end_date (UTC) by starting from the initial state and replaying all
    activity logs up to the snapshot time.
    """
    utc_tz = pytz.utc

    # Localize task creation time
    task_created_at_utc = task.created_at
    if task_created_at_utc.tzinfo is None:
        task_created_at_utc = utc_tz.localize(task_created_at_utc)

    # 1. Check if the task existed yet
    if end_date_utc and task_created_at_utc > end_date_utc:
        return None # Task did not exist

    # --- 2. Establish Initial State (The Baseline) ---
    # We must use the ORM values as the starting point, assuming they reflect creation data.
    state = {
        'status': models.TaskStatusEnum(task.status.value) if task.status is not None else models.TaskStatusEnum.UNASSIGNED,
        'priority': task.priority if task.priority is not None else 5,
        'owner_id': task.owner_id
    }

    # --- 3. Fetch logs that happened UP TO AND INCLUDING the cutoff date ---
    # These are the changes we need to APPLY chronologically (Replay).
    logs_to_replay = models.TaskActivityLog.query.filter(
        models.TaskActivityLog.task_id == task.id,
        models.TaskActivityLog.timestamp <= end_date_utc
    ).order_by(models.TaskActivityLog.timestamp.asc()).all() # Oldest first

    # --- 4. Replay logs in forward chronological order ---
    for log in logs_to_replay:
        field = log.field_changed
        new_value_str = log.new_value # Use the NEW_VALUE to evolve the state forward

        if field == 'status':
             try: 
                 state['status'] = models.TaskStatusEnum(new_value_str)
             except ValueError: 
                 pass
        elif field == 'priority':
             try: state['priority'] = int(new_value_str)
             except (ValueError, TypeError): pass
        elif field == 'owner_id':
             try: state['owner_id'] = int(new_value_str)
             except (ValueError, TypeError): pass
        # Add elif for other fields if needed

    # --- 5. Final state validation (Remains the same) ---
    if not (isinstance(state['priority'], int) and 1 <= state['priority'] <= 10):
         state['priority'] = 5 

    if not isinstance(state['status'], models.TaskStatusEnum):
        state['status'] = models.TaskStatusEnum.UNASSIGNED

    return state

def get_task_completion_time(task, end_date_utc):
    """
    Get the timestamp when a task was completed, if it was completed by end_date_utc.
    Returns None if the task was not completed by end_date_utc.
    """
    utc_tz = pytz.utc

    # Get all status change logs for this task up to the snapshot date
    status_logs = models.TaskActivityLog.query.filter(
        models.TaskActivityLog.task_id == task.id,
        models.TaskActivityLog.field_changed == 'status',
        models.TaskActivityLog.timestamp <= end_date_utc
    ).order_by(models.TaskActivityLog.timestamp.desc()).all()

    # Find the most recent change to COMPLETED status
    # Note: TaskStatusEnum.COMPLETED has value 'Completed' (not 'COMPLETED')
    for log in status_logs:
        if log.new_value == 'Completed' or log.new_value == models.TaskStatusEnum.COMPLETED.value:
            completion_time = log.timestamp
            if completion_time.tzinfo is None:
                completion_time = utc_tz.localize(completion_time)
            return completion_time

    return None

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

    # --- 3. Fetch ALL Tasks for the Project (including subtasks) ---
    try:
        # Get all tasks with this project_id (includes both main tasks and subtasks)
        all_project_tasks = models.Task.query.filter(models.Task.project_id == project_id).all()
        print(f"Fetched {len(all_project_tasks)} tasks for project {project_id}")
    except Exception as e:
        print(f"Error fetching all tasks for project {project_id}: {e}")
        return None, f"Could not fetch tasks: {e}"

    # Get project creation date for overall metrics
    project_created_at = project.created_at
    if project_created_at and project_created_at.tzinfo is None:
        project_created_at = utc_tz.localize(project_created_at)

    print(f"Project created at: {project_created_at}")
    print(f"Report period: {start_date} to {end_date}")

    # --- Helper function to calculate complete section data for a date range ---
    def calculate_section_data_for_period(period_start, period_end, period_name):
        """Calculate all data for tasks active/updated within the given period"""
        print(f"Calculating {period_name} data for period: {period_start} to {period_end}")

        # Find tasks with activity during this period (any activity)
        tasks_with_activity = set()
        try:
            activity_logs_all = models.TaskActivityLog.query.join(models.Task).filter(
                models.Task.project_id == project_id,
                and_(
                    models.TaskActivityLog.timestamp >= period_start,
                    models.TaskActivityLog.timestamp <= period_end
                )
            ).all()
            tasks_with_activity = {log.task_id for log in activity_logs_all}
            print(f"Found {len(tasks_with_activity)} tasks with activity in {period_name}.")
        except Exception as e:
            print(f"Error fetching activity logs for {period_name}: {e}")

        # Fetch activity logs (STATUS CHANGES ONLY - like individual report)
        activity_details = []
        try:
            status_change_logs = models.TaskActivityLog.query.join(models.Task).filter(
                models.Task.project_id == project_id,
                models.TaskActivityLog.timestamp >= period_start,
                models.TaskActivityLog.timestamp <= period_end,
                models.TaskActivityLog.field_changed == 'status'  # Only status changes
            ).order_by(models.TaskActivityLog.task_id, models.TaskActivityLog.timestamp.asc()).all()

            print(f"Found {len(status_change_logs)} status change log entries in {period_name}.")

            task_titles_cache = {}
            for log in status_change_logs:
                task_id = log.task_id
                if task_id not in task_titles_cache:
                    task = models.Task.query.get(task_id)
                    task_titles_cache[task_id] = task.title if task else f"Task {task_id}"
                task_title = task_titles_cache[task_id]

                user_id_changed = log.user_id
                if user_id_changed not in user_cache:
                    user_cache[user_id_changed] = _fetch_user_details(user_id_changed)
                user_name_changed = user_cache[user_id_changed]['name']

                activity_details.append({
                    'task_id': task_id,
                    'task_title': task_title,
                    'timestamp': convert_to_user_tz(log.timestamp),
                    'user_name': user_name_changed,
                    'field_changed': log.field_changed.replace('_', ' ').title(),
                    'old_value': log.old_value if log.old_value != "None" else "-",
                    'new_value': log.new_value if log.new_value != "None" else "-",
                })
        except Exception as e:
            print(f"Error fetching status change logs for {period_name}: {e}")

        # Calculate metrics and prepare task list
        status_distribution = {status.value: 0 for status in models.TaskStatusEnum}
        priority_distribution = {p: 0 for p in range(1, 11)}
        completion_times = []
        overdue_count = 0
        tasks_count = 0
        overdue_tasks_list = []
        task_list = []

        # Collaborator stats for this period
        period_collaborator_stats = defaultdict(lambda: {
            'total_tasks': 0, 'main_tasks': 0, 'sub_tasks': 0,
            'in_progress': 0, 'under_review': 0, 'completed': 0
        })
        for collab_id in project_collaborator_ids:
            _ = period_collaborator_stats[collab_id]

        for task in all_project_tasks:
            state_as_of = get_task_state_as_of(task, period_end)

            if state_as_of is None:
                continue  # Task didn't exist at this time

            status_as_of = state_as_of['status']
            priority_as_of = state_as_of['priority']
            owner_id_as_of = state_as_of['owner_id']

            # Include task if it had activity during period OR is currently incomplete
            should_include = False
            if task.id in tasks_with_activity or status_as_of != models.TaskStatusEnum.COMPLETED:
                should_include = True

            if should_include:
                tasks_count += 1
                status_distribution[status_as_of.value] += 1
                if priority_as_of and 1 <= priority_as_of <= 10:
                    priority_distribution[priority_as_of] += 1

                # Update collaborator stats
                if owner_id_as_of in period_collaborator_stats:
                    stats = period_collaborator_stats[owner_id_as_of]
                    stats['total_tasks'] += 1
                    if task.parent_task_id is None:
                        stats['main_tasks'] += 1
                    else:
                        stats['sub_tasks'] += 1
                    if status_as_of == models.TaskStatusEnum.ONGOING:
                        stats['in_progress'] += 1
                    elif status_as_of == models.TaskStatusEnum.UNDER_REVIEW:
                        stats['under_review'] += 1
                    elif status_as_of == models.TaskStatusEnum.COMPLETED:
                        stats['completed'] += 1

                # Calculate completion time for completed tasks
                if status_as_of == models.TaskStatusEnum.COMPLETED and task.created_at:
                    completion_log = models.TaskActivityLog.query.filter(
                        and_(
                            models.TaskActivityLog.task_id == task.id,
                            models.TaskActivityLog.field_changed == 'status',
                            models.TaskActivityLog.new_value == 'Completed'
                        )
                    ).order_by(models.TaskActivityLog.timestamp.desc()).first()

                    if completion_log:
                        created_at_utc = task.created_at if task.created_at.tzinfo else utc_tz.localize(task.created_at)
                        completed_at_utc = completion_log.timestamp if completion_log.timestamp.tzinfo else utc_tz.localize(completion_log.timestamp)
                        completion_time_days = (completed_at_utc - created_at_utc).total_seconds() / 86400
                        completion_times.append(completion_time_days)

                # Check for overdue
                task_deadline_utc = task.deadline
                if task_deadline_utc and task_deadline_utc.tzinfo is None:
                    task_deadline_utc = utc_tz.localize(task_deadline_utc)

                is_overdue = False
                if task_deadline_utc:
                    if status_as_of == models.TaskStatusEnum.COMPLETED:
                        completion_time = get_task_completion_time(task, period_end)
                        if completion_time and completion_time > task_deadline_utc:
                            is_overdue = True
                    else:
                        if task_deadline_utc < period_end:
                            is_overdue = True

                if is_overdue:
                    overdue_count += 1
                    if owner_id_as_of not in user_cache:
                        user_cache[owner_id_as_of] = _fetch_user_details(owner_id_as_of)
                    owner_name = user_cache[owner_id_as_of]['name']
                    task_type = "Subtask" if task.parent_task_id is not None else "Task"
                    overdue_tasks_list.append({
                        'title': task.title,
                        'deadline': convert_to_user_tz(task.deadline),
                        'owner_name': owner_name,
                        'status': status_as_of.value,
                        'task_type': task_type
                    })

                # Add to task list
                if owner_id_as_of not in user_cache:
                    user_cache[owner_id_as_of] = _fetch_user_details(owner_id_as_of)
                owner_name = user_cache[owner_id_as_of]['name']
                task_type = "Subtask" if task.parent_task_id is not None else "Task"

                task_list.append({
                    'title': task.title,
                    'task_type': task_type,
                    'owner_name': owner_name,
                    'deadline': convert_to_user_tz(task.deadline),
                    'status': status_as_of.value,
                    'priority': priority_as_of or '-',
                    'is_overdue': is_overdue
                })

        # Sort task list by deadline and priority
        task_list_for_sort = []
        for task in task_list:
            try:
                deadline_sort = datetime.fromisoformat(task['deadline'].strip()) if task['deadline'] != 'N/A' else datetime.max
            except:
                deadline_sort = datetime.max
            priority_sort = int(task['priority']) if task['priority'] != '-' else 0
            task_list_for_sort.append((deadline_sort, priority_sort, task))

        sorted_list = sorted(task_list_for_sort, key=lambda item: (item[0], item[1]))
        task_list = [item[2] for item in sorted_list]

        # Format collaborator stats
        collab_stats_formatted = []
        total_period_tasks = 0
        total_period_completed = 0
        for collab_id, stats in period_collaborator_stats.items():
            total = stats['total_tasks']
            completed = stats['completed']
            rate = (completed / total * 100) if total > 0 else 0
            total_period_tasks += total
            total_period_completed += completed
            collab_stats_formatted.append({
                'name': user_cache.get(collab_id, {}).get('name', f"User {collab_id}"),
                'total_tasks': total,
                'main_tasks': stats['main_tasks'],
                'sub_tasks': stats['sub_tasks'],
                'in_progress': stats['in_progress'],
                'under_review': stats['under_review'],
                'completed': completed,
                'completion_rate': round(rate, 1)
            })
        collab_stats_formatted.sort(key=lambda x: x['name'])
        avg_completion_rate = (total_period_completed / total_period_tasks * 100) if total_period_tasks > 0 else 0

        # Calculate summary metrics
        completed_tasks = status_distribution.get('Completed', 0)
        completion_rate = (completed_tasks / tasks_count * 100) if tasks_count > 0 else 0
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0

        return {
            'total_tasks': tasks_count,
            'completed_tasks': completed_tasks,
            'velocity': completed_tasks,
            'completion_rate': round(completion_rate, 1),
            'average_completion_time': round(avg_completion_time, 1),
            'overdue_count': overdue_count,
            'status_distribution': status_distribution,
            'priority_distribution': dict(sorted(priority_distribution.items())),
            'overdue_tasks': overdue_tasks_list,
            'activity_log': activity_details,
            'task_list': task_list,
            'collaborator_stats': collab_stats_formatted,
            'average_completion_rate': round(avg_completion_rate, 1)
        }

    # --- 4. Calculate Overall Project Data (from project start to end_date) ---
    overall_section = calculate_section_data_for_period(project_created_at, as_of_date_utc, "Overall Project")

    # --- 5. Calculate Timeframe-Specific Data (from start_date to end_date) ---
    timeframe_section = None
    if start_date and end_date:
        timeframe_section = calculate_section_data_for_period(start_date, as_of_date_utc, "Timeframe-Specific")

        # Generate charts for timeframe section
        if timeframe_section:
            timeframe_section['status_chart'] = _generate_pie_chart_base64(
                timeframe_section['status_distribution'],
                f"Task Status (Timeframe)"
            )
            timeframe_section['priority_chart'] = _generate_hbar_chart_base64(
                timeframe_section['priority_distribution'],
                f"Task Priority (Timeframe)"
            )

    # --- 6. Generate Charts (Overall Section) ---
    charts = {
        'status_chart': _generate_pie_chart_base64(overall_section['status_distribution'], f"Task Status (Overall Project)"),
        'priority_chart': _generate_hbar_chart_base64(overall_section['priority_distribution'], f"Task Priority (Overall Project)")
    }


    # --- 7. Prepare Template Context ---
    report_period_str = f"{convert_to_user_tz(as_of_date_utc)}"
    overall_period_str = f"{project_created_at.astimezone(user_tz).strftime('%Y-%m-%d')} to {as_of_date_utc.astimezone(user_tz).strftime('%Y-%m-%d')}"
    timeframe_period_str = "N/A"
    if start_date and end_date:
        timeframe_period_str = f"{start_date.astimezone(user_tz).strftime('%Y-%m-%d')} to {end_date.astimezone(user_tz).strftime('%Y-%m-%d')}"

    generation_date_user_tz = datetime.now(user_tz).strftime('%Y-%m-%d %H:%M:%S %Z')

    project_title_safe = secure_filename(project_details.get('title', f"Project_{project_id}"))
    report_date_str = datetime.now(user_tz).strftime('%d%m%Y')
    filename_to_save = f"{project_title_safe}_Report_{report_date_str}.pdf"

    context = {
        "report_title": f"Project Report: {project_title}",
        "report_filename": filename_to_save,
        "project_details": project_details,
        "report_period": report_period_str,
        "overall_period": overall_period_str,
        "timeframe_period": timeframe_period_str,
        "generation_date": generation_date_user_tz,
        "overall_section": overall_section,
        "timeframe_section": timeframe_section,
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

        save_report(pdf_bytes, filename_to_save, user_id, "project", None, project_id=project_id)
        return pdf_bytes, None
    except Exception as e: print(f"Error generating PDF: {e}"); return None, f"PDF Generation Error: {e}"

def generate_individual_pdf_report(target_user_id: int, requesting_user_id: int, start_date: datetime = None, end_date: datetime = None, timezone_str: str = "UTC"):
    """
    Generates a PDF report for an individual user showing their task performance.

    Per user story: "The report displays all tasks that were active or updated during the selected timeframe."

    Task display logic:
    - Show if task has ANY activity during timeframe:
      * Task Update (status changes): Unassigned → Ongoing → Completed
      * Task Edit (field changes): priority, description, title, etc.
    - Show if task is currently incomplete (not completed as of end_date)

    Args:
        target_user_id: The user whose report is being generated
        requesting_user_id: The user requesting the report (for authorization)
        start_date: Start of timeframe (UTC)
        end_date: End of timeframe (UTC) - also used as snapshot date
        timezone_str: Timezone for display formatting
    """
    print(f"Generating individual report for User ID: {target_user_id}, requested by User ID: {requesting_user_id}")
    print(f"Querying data range (UTC): {start_date} to {end_date}")
    print(f"Displaying times in timezone: {timezone_str}")

    # --- 0. Setup Timezone Objects ---
    try:
        user_tz = pytz.timezone(timezone_str)
    except pytz.exceptions.UnknownTimeZoneError:
        print(f"Unknown timezone '{timezone_str}'. Defaulting to UTC.")
        user_tz = pytz.utc
        timezone_str = "UTC"
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

    # --- 1. Fetch Target User Details ---
    if target_user_id not in user_cache:
        user_cache[target_user_id] = _fetch_user_details(target_user_id)
    user_details = user_cache[target_user_id]

    if "Not Found" in user_details['name'] or "Service Down" in user_details['name']:
        return None, f"Could not fetch user details for user {target_user_id}"

    # --- 2. Fetch All Tasks Owned by User ---
    try:
        all_user_tasks = models.Task.query.filter(models.Task.owner_id == target_user_id).all()
        print(f"Fetched {len(all_user_tasks)} total tasks for user {target_user_id}.")
    except Exception as e:
        print(f"Error fetching tasks for user {target_user_id}: {e}")
        return None, f"Could not fetch tasks: {e}"

    # --- 3. Find tasks with activity during timeframe ---
    # Activity includes: task updates (status changes) AND task edits (field changes)
    tasks_with_activity_in_timeframe = set()
    if start_date and end_date:
        try:
            # Find all tasks with ANY activity log entry within the timeframe
            # This includes status updates and field edits (priority, title, description, etc.)
            activity_logs = models.TaskActivityLog.query.filter(
                and_(
                    models.TaskActivityLog.timestamp >= start_date,
                    models.TaskActivityLog.timestamp <= end_date
                )
            ).all()

            tasks_with_activity_in_timeframe = {log.task_id for log in activity_logs}
            print(f"Found {len(tasks_with_activity_in_timeframe)} tasks with activity (updates/edits) within timeframe.")
        except Exception as e:
            print(f"Error fetching activity logs: {e}")

    # --- 4. Calculate Metrics and Prepare Task List ---
    # Initialize metrics for tasks to be displayed only
    status_distribution_as_of = {status.value: 0 for status in models.TaskStatusEnum}
    priority_distribution_as_of = {p: 0 for p in range(1, 11)}
    overdue_tasks_as_of_list = []
    tasks_to_display = []

    # For velocity metrics - only for displayed tasks
    completion_times = []  # List of completion times in days

    for task in all_user_tasks:
        # Get task state as of the snapshot date
        state_as_of = get_task_state_as_of(task, as_of_date_utc)

        if state_as_of is None:
            continue  # Task didn't exist at snapshot time

        status_as_of = state_as_of['status']
        priority_as_of = state_as_of['priority']
        owner_id_as_of = state_as_of['owner_id']

        # Only count tasks where user is the owner at the snapshot date
        if owner_id_as_of != target_user_id:
            continue

        # --- Task Display Logic (Per User Story) ---
        # Show if: (1) Has activity (updates/edits) during timeframe OR (2) Currently incomplete
        should_display = False
        if start_date and end_date:
            # If timeframe is specified, show tasks with activity OR incomplete
            if task.id in tasks_with_activity_in_timeframe or status_as_of != models.TaskStatusEnum.COMPLETED:
                should_display = True
        else:
            # No timeframe: show all incomplete tasks
            if status_as_of != models.TaskStatusEnum.COMPLETED:
                should_display = True

        # ONLY calculate metrics and add to display if task should be shown
        if should_display:
            # Count for metrics (only for displayed tasks)
            status_distribution_as_of[status_as_of.value] += 1
            if priority_as_of and 1 <= priority_as_of <= 10:
                priority_distribution_as_of[priority_as_of] += 1

            # Calculate completion time for completed tasks (only if displayed)
            if status_as_of == models.TaskStatusEnum.COMPLETED and task.created_at:
                # Find when it was completed (task update - status change)
                completion_log = models.TaskActivityLog.query.filter(
                    and_(
                        models.TaskActivityLog.task_id == task.id,
                        models.TaskActivityLog.field_changed == 'status',
                        models.TaskActivityLog.new_value == 'Completed'
                    )
                ).order_by(models.TaskActivityLog.timestamp.desc()).first()

                if completion_log:
                    created_at_utc = task.created_at if task.created_at.tzinfo else utc_tz.localize(task.created_at)
                    completed_at_utc = completion_log.timestamp if completion_log.timestamp.tzinfo else utc_tz.localize(completion_log.timestamp)
                    completion_time_days = (completed_at_utc - created_at_utc).total_seconds() / 86400
                    completion_times.append(completion_time_days)

            # Check for overdue (only if displayed)
            task_deadline_utc = task.deadline
            if task_deadline_utc and task_deadline_utc.tzinfo is None:
                task_deadline_utc = utc_tz.localize(task_deadline_utc)

            # Improved overdue logic:
            # - If task is COMPLETED: check if it was completed AFTER the deadline (completed late)
            # - If task is NOT COMPLETED: check if the deadline has passed (still active but overdue)
            is_overdue_as_of = False
            if task_deadline_utc:
                if status_as_of == models.TaskStatusEnum.COMPLETED:
                    # Task is completed - check if it was completed after deadline
                    completion_time = get_task_completion_time(task, as_of_date_utc)
                    if completion_time and completion_time > task_deadline_utc:
                        is_overdue_as_of = True  # Completed late
                else:
                    # Task is not completed - check if deadline has passed
                    if task_deadline_utc < as_of_date_utc:
                        is_overdue_as_of = True  # Still active but past deadline

            if is_overdue_as_of:
                task_type = "Subtask" if task.parent_task_id is not None else "Task"
                project_name = "Standalone"
                if task.project_id:
                    project = models.Project.query.get(task.project_id)
                    project_name = project.title if project else f"Project {task.project_id}"

                overdue_tasks_as_of_list.append({
                    'title': task.title,
                    'deadline': convert_to_user_tz(task.deadline),
                    'status': status_as_of.value,
                    'task_type': task_type,
                    'project_name': project_name
                })

            # Add to display list
            task_type = "Subtask" if task.parent_task_id is not None else "Task"
            project_name = "Standalone"
            if task.project_id:
                project = models.Project.query.get(task.project_id)
                project_name = project.title if project else f"Project {task.project_id}"

            tasks_to_display.append({
                'title': task.title,
                'task_type': task_type,
                'deadline': convert_to_user_tz(task.deadline),
                'status': status_as_of.value,
                'priority': priority_as_of or '-',
                'project_name': project_name,
                'is_overdue_as_of': is_overdue_as_of
            })

    # Sort tasks by deadline and priority
    tasks_for_sort = []
    for task in tasks_to_display:
        try:
            deadline_sort = datetime.fromisoformat(task['deadline'].strip()) if task['deadline'] != 'N/A' else datetime.max
        except:
            deadline_sort = datetime.max
        priority_sort = int(task['priority']) if task['priority'] != '-' else 0
        tasks_for_sort.append((deadline_sort, priority_sort, task))

    sorted_list = sorted(tasks_for_sort, key=lambda item: (item[0], item[1]))
    tasks_to_display = [item[2] for item in sorted_list]

    # --- 5. Calculate Performance Metrics (Based on Displayed Tasks Only) ---
    # Total tasks: count of tasks shown in the report
    total_tasks = sum(status_distribution_as_of.values())

    # Completed tasks: completed tasks within displayed tasks
    completed_tasks = status_distribution_as_of.get('Completed', 0)

    # Completion rate: completed / total (within displayed tasks)
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # Average completion time: time taken for completed tasks (within displayed tasks)
    average_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0

    # Overdue count: tasks that missed deadline (within displayed tasks)
    overdue_count = len(overdue_tasks_as_of_list)

    # Velocity: number of completed tasks (within displayed tasks)
    velocity = completed_tasks

    section1_metrics = {
        'status_distribution': status_distribution_as_of,
        'priority_distribution': dict(sorted(priority_distribution_as_of.items())),
        'overdue_tasks': overdue_tasks_as_of_list,
        'overdue_count': overdue_count,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'completion_rate': round(completion_rate, 1),
        'average_completion_time': round(average_completion_time, 1),
        'velocity': velocity
    }

    charts = {
        'status_chart': _generate_pie_chart_base64(status_distribution_as_of, f"Task Status (As of {as_of_date_utc.strftime('%Y-%m-%d')})"),
        'priority_chart': _generate_hbar_chart_base64(priority_distribution_as_of, f"Task Priority (As of {as_of_date_utc.strftime('%Y-%m-%d')})")
    }

    # --- 6. Fetch Activity Details (Status Changes Only) ---
    section2_details = []
    if start_date and end_date:
        try:
            # Only fetch status changes (task updates), not field changes (task edits)
            activity_query = models.TaskActivityLog.query.join(models.Task).filter(
                models.Task.owner_id == target_user_id,
                models.TaskActivityLog.timestamp >= start_date,
                models.TaskActivityLog.timestamp <= end_date,
                models.TaskActivityLog.field_changed == 'status'  # Only status changes
            )
            activity_logs = activity_query.order_by(models.TaskActivityLog.task_id, models.TaskActivityLog.timestamp.asc()).all()
            print(f"Found {len(activity_logs)} status change log entries for user {target_user_id}.")

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
                    'timestamp': convert_to_user_tz(log.timestamp),
                    'user_name': user_name_changed,
                    'field_changed': log.field_changed.replace('_', ' ').title(),
                    'old_value': log.old_value if log.old_value != "None" else "-",
                    'new_value': log.new_value if log.new_value != "None" else "-",
                })
        except Exception as e:
            print(f"Error fetching activity logs for user {target_user_id}: {e}")
            return None, f"Could not fetch activity logs: {e}"

    # --- 7. Prepare Template Context ---
    report_period_str = f"{convert_to_user_tz(as_of_date_utc)}"
    activity_period_str = "N/A"
    if start_date and end_date:
        activity_period_str = f"{start_date.astimezone(user_tz).strftime('%Y-%m-%d')} to {end_date.astimezone(user_tz).strftime('%Y-%m-%d')}"

    generation_date_user_tz = datetime.now(user_tz).strftime('%Y-%m-%d %H:%M:%S %Z')

    # Format filename per user story: UserNameIndividualTaskPerformanceReport_DDMMYYYY
    report_date = datetime.now(user_tz).strftime('%d%m%Y')
    user_name_clean = user_details['name'].replace(' ', '')

    context = {
        "report_title": f"Individual Task Performance Report: {user_details['name']}",
        "report_filename": f"{user_name_clean}IndividualTaskPerformanceReport_{report_date}",
        "user_details": {
            'name': user_details['name'],
            'role': user_details['role'],
            'user_id': target_user_id
        },
        "report_period": report_period_str,
        "activity_period": activity_period_str,
        "generation_date": generation_date_user_tz,
        "section1": section1_metrics,
        "section2": section2_details,
        "section3_tasks": tasks_to_display,
        "charts": charts,
    }

    # --- 8. Render HTML Template ---
    try:
        template = jinja_env.get_template('individual_report_template.html')
        html_string = template.render(context)
    except Exception as e:
        print(f"Error rendering HTML template: {e}")
        error_html = f"<html><body><h1>Template Rendering Error</h1><p>{e}</p><p>NOTE: Ensure 'individual_report_template.html' exists and is correct.</p></body></html>"
        return error_html.encode('utf-8'), f"Template Error: {e}"

    # --- 9. Generate PDF ---
    try:
        pdf_bytes = HTML(string=html_string).write_pdf()
        print(f"Successfully generated PDF ({len(pdf_bytes)} bytes) for user {target_user_id}.")

        filename = context['report_filename'] + ".pdf"
        print(requesting_user_id, target_user_id)
        save_report(pdf_bytes, filename, requesting_user_id, "individual", target_user_id)

        return pdf_bytes, None
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None, f"PDF Generation Error: {e}"

def save_report(report_content: bytes, filename: str, requesting_user_id: int, report_type: str, target_user_id: int = None, project_id: int = None):
    """
    Atomically uploads report to S3 and saves metadata to the database.
    Includes rollback logic if the database save fails.
    """

    s3_object_key = None
    safe_filename = secure_filename(filename)

    try:
        s3_object_key = f"reports/{uuid.uuid4()}_{safe_filename}"

        current_app.s3_client.upload_fileobj(
            BytesIO(report_content),
            current_app.config['S3_BUCKET_NAME'],
            s3_object_key,
            ExtraArgs={'ContentType': 'application/pdf'}
        )

        print(f"Successfully saved report to S3: {s3_object_key}")
    except (BotoCoreError, ClientError) as e:
        print(f"Error saving report to S3: {e}")
        return None
    
    try:
        

        new_report_history = models.ReportHistory(
            filename=safe_filename,
            url=s3_object_key,
            user_id=requesting_user_id,
            target_user_id=target_user_id,
            report_type=report_type,
            project_id=project_id
        )

        models.db.session.add(new_report_history)
        models.db.session.commit()
        print(f"Report history recorded in database for report: {filename}")

        return s3_object_key

    except Exception as e:
# 4. DB SAVE FAILED! We must roll back the S3 upload.
        models.db.session.rollback()
        print(f"DATABASE SAVE FAILED: {e}. Rolling back session.")
        
        if s3_object_key: # s3_object_key will exist from the 'try' block
            print(f"Attempting to delete orphaned S3 file: {s3_object_key}")
            try:
                current_app.s3_client.delete_object(
                    Bucket=current_app.config['S3_BUCKET_NAME'],
                    Key=s3_object_key
                )
                print("Orphaned file deleted.")
            except Exception as del_e:
                print(f"CRITICAL: Failed to delete orphaned S3 file {s3_object_key}: {del_e}")
        
        return None # Total Failure
    
def get_all_reports_for_user(user_id):
    """
    Fetches all report history entries for a given user.
    """
    try:
        reports = models.ReportHistory.query.filter(models.ReportHistory.user_id == user_id).order_by(models.ReportHistory.created_at.desc()).all()

        return reports, None
    except Exception as e:
        print(f"Error fetching reports for user {user_id}: {e}")
        return None, f"Could not fetch reports: {e}"

def get_report_by_id(report_id: int, user_id: int):
    """
    Fetches a specific report by ID, ensuring it belongs to the requesting user.
    """
    try:
        report = models.ReportHistory.query.get(report_id)

        if not report:
            return None, "Report not found."
        if report.user_id != int(user_id):
            return None, "Unauthorized access to report."

        presigned_url = current_app.s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': current_app.config['S3_BUCKET_NAME'],
                'Key': report.url
            },
            ExpiresIn=3600  # URL valid for 1 hour
        )

        return presigned_url, None
    except Exception as e:
        print(f"Error fetching report {report_id} for user {user_id}: {e}")
        return None, f"Could not fetch report: {e}"
    
def delete_report_by_id(report_id: int, user_id: int):
    """
    Deletes a specific report by ID, ensuring it belongs to the requesting user.
    Also deletes the report file from S3.
    """
    try:
        report = models.ReportHistory.query.get(report_id)

        if not report:
            return False, "Report not found."
        if report.user_id != int(user_id):
            return False, "Unauthorized access to report."

        current_app.s3_client.delete_object(
            Bucket=current_app.config['S3_BUCKET_NAME'],
            Key=report.url
        )

        models.db.session.delete(report)
        models.db.session.commit()

        return True, None
    except Exception as e:
        print(f"Error deleting report {report_id} for user {user_id}: {e}")
        models.db.session.rollback()
        return False, f"Could not delete report: {e}"
