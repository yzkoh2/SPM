import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import requests
from .email_templates import get_status_update_email, get_deadline_reminder_email, get_overdue_task_email, get_mention_alert_email  
from .models import db, DeadlineReminder, OverdueAlert, MentionNotification 

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
    #Format deadline string for display in email (converted to Singapore time)
    if not deadline_str or deadline_str == 'No deadline set':
        return 'No deadline set'
    
    try:
        singapore_tz = ZoneInfo('Asia/Singapore')
        
        #Parse the UTC datetime
        deadline_dt = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        
        #Convert to Singapore time
        deadline_sgt = deadline_dt.astimezone(singapore_tz)
        
        #Format for display
        return deadline_sgt.strftime('%B %d, %Y at %I:%M %p SGT')
    except:
        return 'No deadline set'


def extract_mention_context(comment_body, mentioned_username, context_chars=100):
    #Extract a snippet of text around the @mention for email display.
    mention_pattern = f"@{mentioned_username}"
    mention_index = comment_body.find(mention_pattern)
    
    if mention_index == -1:
        if len(comment_body) > 200:
            return comment_body[:197] + "..."
        return comment_body
    
    start = max(0, mention_index - context_chars)
    end = min(len(comment_body), mention_index + len(mention_pattern) + context_chars)
    snippet = comment_body[start:end]
    
    if start > 0:
        first_space = snippet.find(' ')
        if first_space > 0 and first_space < 15:
            snippet = snippet[first_space + 1:]
        snippet = "..." + snippet
    
    if end < len(comment_body):
        last_space = snippet.rfind(' ')
        if last_space > len(snippet) - 15:
            snippet = snippet[:last_space]
        snippet = snippet + "..."
    
    return snippet.strip()


def highlight_mention_in_text(text, mentioned_username, primary_color="#3b82f6"):
    #Add HTML highlighting to @mention in text for email display.
    mention_pattern = f"@{mentioned_username}"
    
    highlighted_mention = (
        f'<span style="'
        f'color: {primary_color}; '
        f'font-weight: 700; '
        f'background: #dbeafe; '
        f'padding: 2px 6px; '
        f'border-radius: 4px; '
        f'border: 1px solid {primary_color}; '
        f'white-space: nowrap;'
        f'">{mention_pattern}</span>'
    )
    
    return text.replace(mention_pattern, highlighted_mention)


def format_time_ago(timestamp):
    #Format timestamp as relative time (e.g., '2 hours ago', 'just now').
    singapore_tz = ZoneInfo('Asia/Singapore')
    now = datetime.now(singapore_tz)
    
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=singapore_tz)
    
    diff = now - timestamp
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        return timestamp.strftime('%B %d, %Y')


def get_user_initials(name):
    #Get initials from user's name for avatar display.
    if not name:
        return "?"
    
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    elif len(parts) == 1:
        return parts[0][0].upper()
    else:
        return "?"


def get_user_details_for_mention(user_id):
    #Helper function to fetch complete user details for mention notifications.
    try:
        user_service_url = current_app.config['USER_SERVICE_URL']
        response = requests.get(f"{user_service_url}/user/{user_id}", timeout=5)
        
        if response.status_code == 200:
            return response.json()
        return {}
            
    except Exception as e:
        print(f"❌ Failed to fetch user details for user {user_id}: {e}")
        return {}

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

# ==================== Mention Alert Notification ====================
def send_mention_alert_notification(task_id, comment_id, mentioned_user_id, author_id, comment_body):
    #Send mention alert notification when a user is mentioned in a comment.
    try:
        singapore_tz = ZoneInfo('Asia/Singapore')
        now = datetime.now(singapore_tz)
        
        print(f"\n{'='*70}")
        print(f"📨 MENTION ALERT NOTIFICATION")
        print(f"   Current Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"{'='*70}")
        
        #Check if notification already sent for this comment and user
        existing = MentionNotification.query.filter_by(
            comment_id=comment_id,
            mentioned_user_id=mentioned_user_id
        ).first()
        
        if existing:
            print(f"   ⚠️  Mention notification already sent")
            print(f"   Comment ID: {comment_id}, User ID: {mentioned_user_id}")
            print(f"{'='*70}\n")
            return True  
        
        #Get task details
        task = get_task_details(task_id)
        if not task:
            print(f"❌ Task not found: {task_id}")
            print(f"{'='*70}\n")
            return False
        
        task_title = task.get('title', 'Untitled Task')
        is_subtask = task.get('parent_task_id') is not None
        
        print(f"📋 Task {task_id}: {task_title}")
        print(f"   Type: {'Subtask' if is_subtask else 'Task'}")
        print(f"   Comment ID: {comment_id}")
        
        #Get author details (person who wrote the comment)
        author_details = get_user_details_for_mention(author_id)
        author_name = author_details.get('name', 'Unknown User')
        author_username = author_details.get('username', 'unknown')
        
        print(f"   Author: {author_name} (@{author_username})")
        
        #Get mentioned user details (person being notified)
        mentioned_user = get_user_details_for_mention(mentioned_user_id)
        mentioned_email = mentioned_user.get('email')
        mentioned_username = mentioned_user.get('username', 'user')
        mentioned_name = mentioned_user.get('name', 'User')
        
        if not mentioned_email:
            print(f"❌ No email found for mentioned user {mentioned_user_id}")
            print(f"{'='*70}\n")
            return False
        
        print(f"   Mentioned: {mentioned_name} (@{mentioned_username})")
        print(f"   Email: {mentioned_email}")
        
        #Extract comment snippet with context around the mention
        comment_snippet = extract_mention_context(comment_body, mentioned_username)
        
        #Highlight the @mention in the snippet
        highlighted_snippet = highlight_mention_in_text(comment_snippet, mentioned_username)
        
        #Prepare data for email template
        author_initials = get_user_initials(author_name)
        timestamp_relative = format_time_ago(now)
        
        comment_metadata = {
            'timestamp': timestamp_relative,
            'author_initials': author_initials,
            'task_id': task_id,
            'is_subtask': is_subtask
        }
        
        #Generate email content
        subject, body_html = get_mention_alert_email(
            task_title=task_title,
            comment_snippet=highlighted_snippet,
            author_name=author_name,
            mentioned_username=mentioned_username,
            is_subtask=is_subtask,
            comment_metadata=comment_metadata
        )
        
        #Send email
        print(f"   📧 Sending mention alert email...")
        success, error = send_email_via_smtp(mentioned_email, subject, body_html)
        
        if success:
            #Record notification in database
            mention_notification = MentionNotification(
                task_id=task_id,
                comment_id=comment_id,
                mentioned_user_id=mentioned_user_id,
                author_id=author_id
            )
            db.session.add(mention_notification)
            db.session.commit()
            
            print(f"   ✅ Mention alert sent successfully")
            print(f"   ✅ Notification recorded in database (ID: {mention_notification.id})")
            print(f"{'='*70}\n")
            return True
        else:
            print(f"   ❌ Failed to send mention alert email: {error}")
            print(f"{'='*70}\n")
            return False
            
    except Exception as e:
        print(f"❌ Error sending mention alert: {e}")
        print(f"{'='*70}\n")
        db.session.rollback()
        return False