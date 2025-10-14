import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import requests
from .email_templates import get_status_update_email, get_deadline_reminder_email, get_overdue_task_email
from .models import db, DeadlineReminder, OverdueAlert


def send_email_via_smtp(to_email, subject, html_content):
    #Send email using SMTP (Brevo)
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = current_app.config['SMTP_FROM_EMAIL']
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(
            current_app.config['SMTP_HOST'], 
            current_app.config['SMTP_PORT']
        ) as server:
            server.starttls() 
            server.login(
                current_app.config['SMTP_USERNAME'],
                current_app.config['SMTP_PASSWORD']
            )
            server.send_message(msg)
        
        return True, None
        
    except Exception as e:
        print(f"❌ Email failed to {to_email}: {str(e)}")
        return False, str(e)

# ==================== Helper Functions ====================
def get_user_email(user_id):
    #Fetch user's email from User Service
    try:
        user_service_url = current_app.config['USER_SERVICE_URL']
        response = requests.get(f"{user_service_url}/user/{user_id}", timeout=5)
        
        if response.status_code == 200:
            return response.json().get('email')
        return None
            
    except Exception as e:
        print(f"❌ Failed to fetch email for user {user_id}: {e}")
        return None


def get_user_name(user_id):
    #Fetch user's name from User Service
    try:
        user_service_url = current_app.config['USER_SERVICE_URL']
        response = requests.get(f"{user_service_url}/user/{user_id}", timeout=5)
        
        if response.status_code == 200:
            return response.json().get('name', 'A team member')
        return 'A team member'
            
    except Exception as e:
        print(f"❌ Failed to fetch name for user {user_id}: {e}")
        return 'A team member'


def get_task_details(task_id):
    #Fetch task details from Task Service
    try:
        task_service_url = current_app.config['TASK_SERVICE_URL']
        response = requests.get(f"{task_service_url}/tasks/{task_id}", timeout=5)
        
        if response.status_code == 200:
            return response.json()
        return None
            
    except Exception as e:
        print(f"❌ Failed to fetch task {task_id}: {e}")
        return None


def get_task_collaborators(task_id):
    #Fetch collaborators for a task
    try:
        task_service_url = current_app.config['TASK_SERVICE_URL']
        response = requests.get(
            f"{task_service_url}/tasks/{task_id}/collaborators",
            timeout=5
        )
        
        if response.status_code == 200:
            collaborators = response.json()
            return [collab['user_id'] for collab in collaborators]
        return []
            
    except Exception as e:
        print(f"❌ Failed to fetch collaborators for task {task_id}: {e}")
        return []


def get_all_tasks_with_deadlines():
    #Fetch all tasks and subtasks that have deadlines
    try:
        task_service_url = current_app.config['TASK_SERVICE_URL']
        response = requests.get(
            f"{task_service_url}/tasks/with-deadlines",
            timeout=15
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️  Task service returned status {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Failed to fetch tasks with deadlines: {e}")
        return []


def parse_deadline(deadline_str):
    #Parse and Convert into SG Time
    singapore_tz = ZoneInfo('Asia/Singapore')
    
    #Check if timezone-aware (contains 'Z', '+', or multiple '-' for negative offset)
    is_timezone_aware = (
        deadline_str.endswith('Z') or 
        '+' in deadline_str or 
        deadline_str.count('-') > 2
    )
    
    if is_timezone_aware:
        #Parse as UTC and convert to Singapore time
        deadline_utc = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        return deadline_utc.astimezone(singapore_tz)
    else:
        #Naive datetime - assume it's already in Singapore time
        deadline_naive = datetime.fromisoformat(deadline_str)
        return deadline_naive.replace(tzinfo=singapore_tz)


def format_deadline_for_email(deadline_str):
    #Format deadline string for display in email
    if not deadline_str or deadline_str == 'No deadline set':
        return 'No deadline set'
    
    try:
        deadline_dt = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        return deadline_dt.strftime('%B %d, %Y at %I:%M %p')
    except:
        return 'No deadline set'


# ==================== Status Update Notification ====================
def send_status_update_notification(task_id, old_status, new_status, changed_by_id):
    #Send status update notification to all involved users
    try:
        singapore_tz = ZoneInfo('Asia/Singapore')
        now = datetime.now(singapore_tz)
        
        print(f"\n{'='*70}")
        print(f"📨 STATUS UPDATE NOTIFICATION")
        print(f"   Current Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"{'='*70}")
        
        #Get task details
        task = get_task_details(task_id)
        if not task:
            print(f"❌ Task not found")
            print(f"{'='*70}\n")
            return False
        
        task_title = task.get('title', 'Untitled')
        
        print(f"📋 Task {task_id}: {task_title}")
        print(f"   Notification Type: STATUS UPDATE")
        print(f"   Status Change: {old_status} → {new_status}")
        
        #Collect recipients
        is_subtask = task.get('parent_task_id') is not None
        changed_by_name = get_user_name(changed_by_id)
        recipient_ids = set([task['owner_id']])
        recipient_ids.update(get_task_collaborators(task_id))
        
        print(f"   Changed By: {changed_by_name}")
        
        if not recipient_ids:
            print(f"   ⚠️  No recipients found")
            print(f"{'='*70}\n")
            return True
        
        #Format data for email
        deadline_str = format_deadline_for_email(task.get('deadline'))
        description = task.get('description') or 'No description provided'
        
        #Generate and send emails
        subject, body_html = get_status_update_email(
            task['title'], old_status, new_status, changed_by_name,
            deadline_str, description, is_subtask
        )
        
        sent_count = 0
        recipient_emails = []
        for user_id in recipient_ids:
            email = get_user_email(user_id)
            if email:
                success, _ = send_email_via_smtp(email, subject, body_html)
                if success:
                    sent_count += 1
                    recipient_emails.append(email)
        
        #Log email recipients
        if recipient_emails:
            print(f"   📧 Email sent to: {', '.join(recipient_emails)}")
        
        print(f"   ✅ Sent to {sent_count}/{len(recipient_ids)} recipients")
        print(f"{'='*70}\n")
        
        return sent_count > 0
        
    except Exception as e:
        print(f"❌ Status update error: {e}")
        print(f"{'='*70}\n")
        return False

# ==================== Deadline Reminder Notification ====================
def send_deadline_reminder(task_id, days_before):
    #Send deadline reminder notification for a specific task
    try:
        #Get task details
        task = get_task_details(task_id)
        if not task:
            print(f"      ❌ Task not found")
            return False
        
        #Skip if completed
        if task.get('status') == 'Completed':
            print(f"      ⏭️  Task completed, skipping")
            return False
        
        #Collect recipients
        is_subtask = task.get('parent_task_id') is not None
        recipient_ids = set([task['owner_id']])
        recipient_ids.update(get_task_collaborators(task_id))
        
        if not recipient_ids:
            return True
        
        #Format data for email
        deadline_str = format_deadline_for_email(task.get('deadline'))
        description = task.get('description') or 'No description provided'
        task_status = task.get('status', 'Unknown')
        
        #Generate and send emails
        subject, body_html = get_deadline_reminder_email(
            task['title'], days_before, deadline_str, 
            description, task_status, is_subtask
        )
        
        sent_count = 0
        recipient_emails = []
        for user_id in recipient_ids:
            email = get_user_email(user_id)
            if email:
                success, _ = send_email_via_smtp(email, subject, body_html)
                if success:
                    sent_count += 1
                    recipient_emails.append(email)
        
        #Log email recipients
        if recipient_emails:
            print(f"      📧 Email sent to: {', '.join(recipient_emails)}")
        
        #Record in database
        if sent_count > 0:
            try:
                reminder = DeadlineReminder(task_id=task_id, days_before=days_before)
                db.session.add(reminder)
                db.session.commit()
            except Exception as e:
                print(f"      ⚠️  DB record failed: {e}")
                db.session.rollback()
        
        print(f"      ✅ Sent to {sent_count}/{len(recipient_ids)} recipients")
        return sent_count > 0
        
    except Exception as e:
        print(f"      ❌ Error: {e}")
        return False


def check_and_send_deadline_reminders():
    #Check for upcoming deadlines and send reminder notifications
    try:
        singapore_tz = ZoneInfo('Asia/Singapore')
        now = datetime.now(singapore_tz)
        today = now.date()
        
        print(f"\n{'='*70}")
        print(f"⏰ DEADLINE REMINDER CHECK")
        print(f"   Current Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"   Today's Date: {today}")
        print(f"{'='*70}")
        
        tasks = get_all_tasks_with_deadlines()
        print(f"📋 Total tasks with deadlines: {len(tasks)}")
        
        if not tasks:
            print(f"{'='*70}\n")
            return 0
        
        reminder_intervals = [7, 3, 1]
        reminders_sent = 0
        
        for task in tasks:
            task_id = task['id']
            task_title = task.get('title', 'Untitled')
            deadline_str = task.get('deadline')
            
            if not deadline_str:
                continue
            
            try:
                deadline = parse_deadline(deadline_str)
                deadline_date = deadline.date()
                
                for days_before in reminder_intervals:
                    reminder_date = (deadline - timedelta(days=days_before)).date()
                    
                    if reminder_date == today:
                        # Check if already sent
                        existing = DeadlineReminder.query.filter_by(
                            task_id=task_id,
                            days_before=days_before
                        ).first()
                        
                        if existing:
                            print(f"\n   ⏭️  Task {task_id}: {task_title}")
                            print(f"      {days_before}-day reminder already sent")
                            continue
                        
                        # Print task details
                        print(f"\n   📤 Task {task_id}: {task_title}")
                        print(f"      Notification Type: DEADLINE REMINDER")
                        print(f"      Deadline (SGT): {deadline.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                        print(f"      Deadline Date: {deadline_date}")
                        print(f"      Today's Date: {today}")
                        print(f"      Days Before Deadline: {days_before}")
                        
                        if send_deadline_reminder(task_id, days_before):
                            reminders_sent += 1
            
            except Exception as e:
                print(f"\n   ❌ Task {task_id}: {task_title}")
                print(f"      Error: {e}")
                continue
        
        print(f"\n{'='*70}")
        print(f"✅ Check Complete: {reminders_sent} deadline reminder(s) sent")
        print(f"{'='*70}\n")
        
        return reminders_sent
        
    except Exception as e:
        print(f"❌ Deadline check failed: {e}\n")
        return 0


# ==================== Overdue Task Alert Notification ====================
def send_overdue_task_alert(task_id, days_overdue):
    #Send overdue alert notification for a specific task
    try:
        #Get task details
        task = get_task_details(task_id)
        if not task:
            print(f"      ❌ Task not found")
            return False
        
        #Skip if completed
        if task.get('status') == 'Completed':
            print(f"      ⏭️  Task completed, skipping")
            return False
        
        #Collect recipients
        is_subtask = task.get('parent_task_id') is not None
        recipient_ids = set([task['owner_id']])
        recipient_ids.update(get_task_collaborators(task_id))
        
        if not recipient_ids:
            return True
        
        #Format data for email
        deadline_str = format_deadline_for_email(task.get('deadline'))
        description = task.get('description') or 'No description provided'
        task_status = task.get('status', 'Unknown')
        
        #Generate and send emails
        subject, body_html = get_overdue_task_email(
            task['title'], deadline_str, days_overdue,
            description, task_status, is_subtask
        )
        
        sent_count = 0
        recipient_emails = []
        for user_id in recipient_ids:
            email = get_user_email(user_id)
            if email:
                success, _ = send_email_via_smtp(email, subject, body_html)
                if success:
                    sent_count += 1
                    recipient_emails.append(email)
        
        #Log email recipients
        if recipient_emails:
            print(f"      📧 Email sent to: {', '.join(recipient_emails)}")
        
        #Record in database
        if sent_count > 0:
            try:
                singapore_tz = ZoneInfo('Asia/Singapore')
                today = datetime.now(singapore_tz).date()
                
                alert = OverdueAlert(
                    task_id=task_id,
                    alert_date=today,
                    days_overdue=days_overdue
                )
                db.session.add(alert)
                db.session.commit()
            except Exception as e:
                print(f"      ⚠️  DB record failed: {e}")
                db.session.rollback()
        
        print(f"      ✅ Sent to {sent_count}/{len(recipient_ids)} recipients")
        return sent_count > 0
        
    except Exception as e:
        print(f"      ❌ Error: {e}")
        return False


def check_and_send_overdue_alerts():
    #Check for overdue tasks and send alert notifications
    try:
        singapore_tz = ZoneInfo('Asia/Singapore')
        now = datetime.now(singapore_tz)
        today = now.date()
        
        print(f"\n{'='*70}")
        print(f"🚨 OVERDUE TASK CHECK")
        print(f"   Current Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"   Today's Date: {today}")
        print(f"{'='*70}")
        
        tasks = get_all_tasks_with_deadlines()
        print(f"📋 Total tasks with deadlines: {len(tasks)}")
        
        if not tasks:
            print(f"{'='*70}\n")
            return 0
        
        alerts_sent = 0
        
        for task in tasks:
            task_id = task['id']
            task_title = task.get('title', 'Untitled')
            deadline_str = task.get('deadline')
            status = task.get('status')
            
            #Skip if no deadline or completed
            if not deadline_str or status == 'Completed':
                continue
            
            try:
                deadline = parse_deadline(deadline_str)
                deadline_date = deadline.date()
                
                #Check if overdue (deadline date passed OR same-day but time passed)
                is_overdue = (
                    deadline_date < today or 
                    (deadline_date == today and deadline < now)
                )
                
                if is_overdue:
                    days_overdue = max(1, (today - deadline_date).days)
                    
                    #Check if already sent today
                    existing = OverdueAlert.query.filter_by(
                        task_id=task_id,
                        alert_date=today
                    ).first()
                    
                    if existing:
                        print(f"\n   ⏭️  Task {task_id}: {task_title}")
                        print(f"      Overdue alert already sent today")
                        continue
                    
                    #Print task details
                    print(f"\n   🚨 Task {task_id}: {task_title}")
                    print(f"      Notification Type: OVERDUE ALERT")
                    print(f"      Deadline (SGT): {deadline.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                    print(f"      Deadline Date: {deadline_date}")
                    print(f"      Today's Date: {today}")
                    print(f"      Overdue By: {days_overdue} day(s)")
                    
                    if send_overdue_task_alert(task_id, days_overdue):
                        alerts_sent += 1
            
            except Exception as e:
                print(f"\n   ❌ Task {task_id}: {task_title}")
                print(f"      Error: {e}")
                continue
        
        print(f"\n{'='*70}")
        print(f"✅ Check Complete: {alerts_sent} overdue alert(s) sent")
        print(f"{'='*70}\n")
        
        return alerts_sent
        
    except Exception as e:
        print(f"❌ Overdue check failed: {e}\n")
        return 0