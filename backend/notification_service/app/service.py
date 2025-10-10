import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from datetime import datetime, timedelta
import requests
from .email_templates import get_status_update_email, get_deadline_reminder_email
from .models import db, DeadlineReminder


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
        
        print(f"✅ Email sent to {to_email}")
        return True, None
        
    except Exception as e:
        print(f"❌ Error sending email to {to_email}: {str(e)}")
        return False, str(e)


def get_user_email(user_id):
    #Fetch user's email from User Service
    try:
        user_service_url = current_app.config['USER_SERVICE_URL']
        response = requests.get(f"{user_service_url}/user/{user_id}", timeout=5)
        
        if response.status_code == 200:
            user_data = response.json()
            return user_data.get('email')
        return None
            
    except Exception as e:
        print(f"❌ Error fetching user email: {e}")
        return None


def get_user_name(user_id):
    #Fetch user's name from User Service
    try:
        user_service_url = current_app.config['USER_SERVICE_URL']
        response = requests.get(f"{user_service_url}/user/{user_id}", timeout=5)
        
        if response.status_code == 200:
            user_data = response.json()
            return user_data.get('name', 'A team member')
        return 'A team member'
            
    except Exception as e:
        print(f"❌ Error fetching user name: {e}")
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
        print(f"❌ Error fetching task details: {e}")
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
        print(f"❌ Error fetching collaborators: {e}")
        return []

def get_all_tasks_with_deadlines():
    #Fetch all tasks and subtasks that have upcoming deadlines.   
    try:
        task_service_url = current_app.config['TASK_SERVICE_URL']
        # Call the new dedicated endpoint
        response = requests.get(
            f"{task_service_url}/tasks/with-deadlines",
            timeout=15
        )
        
        if response.status_code == 200:
            tasks = response.json()
            print(f"📋 Found {len(tasks)} tasks/subtasks with upcoming deadlines")
            return tasks
        else:
            print(f"⚠️ Task service returned status {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error fetching tasks with deadlines: {e}")
        import traceback
        traceback.print_exc()
        return []

def send_status_update_notification(task_id, old_status, new_status, changed_by_id):
    #Send status update notification to all involved users
    try:
        print(f"📨 Processing status update for task {task_id}: {old_status} → {new_status}")
        
        #Get task details
        task = get_task_details(task_id)
        if not task:
            print(f"❌ Task {task_id} not found")
            return False
        
        #Check if subtask
        is_subtask = task.get('parent_task_id') is not None
        
        #Get name of person who made the change
        changed_by_name = get_user_name(changed_by_id)
        
        #Collect all recipients: owner + collaborators
        recipient_ids = set([task['owner_id']])
        collaborator_ids = get_task_collaborators(task_id)
        recipient_ids.update(collaborator_ids)
        
        if not recipient_ids:
            print(f"⚠️ No users to notify")
            return True
        
        #Format deadline for email
        deadline_str = task.get('deadline', 'No deadline set')
        if deadline_str and deadline_str != 'No deadline set':
            try:
                deadline_dt = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                deadline_str = deadline_dt.strftime('%B %d, %Y at %I:%M %p')
            except:
                deadline_str = 'No deadline set'
        
        #Get description
        description = task.get('description', 'No description provided')
        if not description:
            description = 'No description provided'
        
        #Generate email content
        subject, body_html = get_status_update_email(
            task['title'],
            old_status,
            new_status,
            changed_by_name,
            deadline_str,
            description,
            is_subtask
        )
        
        #Send to each recipient
        sent_count = 0
        for user_id in recipient_ids:
            email = get_user_email(user_id)
            if email:
                success, error = send_email_via_smtp(email, subject, body_html)
                if success:
                    sent_count += 1
            else:
                print(f"⚠️ No email found for user_id {user_id}")
        
        print(f"✅ Sent {sent_count}/{len(recipient_ids)} status update notifications")
        return sent_count > 0
        
    except Exception as e:
        print(f"❌ Error in send_status_update_notification: {e}")
        return False
    
def send_deadline_reminder(task_id, days_before):
    #Send deadline reminder notification for a specific task
    try:
        print(f"📅 Processing deadline reminder for task {task_id} ({days_before} days before)")
        
        #Get task details
        task = get_task_details(task_id)
        if not task:
            print(f"❌ Task {task_id} not found")
            return False
        
        #Check if task is completed
        if task.get('status') == 'Completed':
            print(f"⏭️ Task {task_id} is already completed, skipping reminder")
            return False
        
        #Check if subtask
        is_subtask = task.get('parent_task_id') is not None
        
        #Collect all recipients: owner + collaborators
        recipient_ids = set([task['owner_id']])
        collaborator_ids = get_task_collaborators(task_id)
        recipient_ids.update(collaborator_ids)
        
        if not recipient_ids:
            print(f"⚠️ No users to notify")
            return True
        
        #Format deadline for email
        deadline_str = task.get('deadline', 'No deadline set')
        if deadline_str and deadline_str != 'No deadline set':
            try:
                deadline_dt = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                deadline_str = deadline_dt.strftime('%B %d, %Y at %I:%M %p')
            except:
                deadline_str = 'No deadline set'
        
        #Get description
        description = task.get('description', 'No description provided')
        if not description:
            description = 'No description provided'
        
        #Get current status
        task_status = task.get('status', 'Unknown')
        
        #Generate email content
        subject, body_html = get_deadline_reminder_email(
            task['title'],
            days_before,
            deadline_str,
            description,
            task_status,
            is_subtask
        )
        
        #Send to each recipient
        sent_count = 0
        for user_id in recipient_ids:
            email = get_user_email(user_id)
            if email:
                success, error = send_email_via_smtp(email, subject, body_html)
                if success:
                    sent_count += 1
            else:
                print(f"⚠️ No email found for user_id {user_id}")
        
        #Record that we sent this reminder
        if sent_count > 0:
            try:
                reminder = DeadlineReminder(
                    task_id=task_id,
                    days_before=days_before
                )
                db.session.add(reminder)
                db.session.commit()
                print(f"✅ Recorded deadline reminder in database")
            except Exception as e:
                print(f"⚠️ Failed to record reminder in database: {e}")
                db.session.rollback()
        
        print(f"✅ Sent {sent_count}/{len(recipient_ids)} deadline reminders")
        return sent_count > 0
        
    except Exception as e:
        print(f"❌ Error in send_deadline_reminder: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_and_send_deadline_reminders():
    #Check all tasks and send deadline reminders where appropriate.
    try:
        print(f"\n{'='*70}")
        print(f"⏰ DEADLINE REMINDER CHECK - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"{'='*70}\n")
        
        now = datetime.utcnow()
        reminder_intervals = [7, 3, 1]  # Days before deadline
        
        #Get all tasks with deadlines
        tasks = get_all_tasks_with_deadlines()
        print(f"📋 Found {len(tasks)} tasks with deadlines")
        
        reminders_sent = 0
        
        for task in tasks:
            task_id = task['id']
            deadline_str = task.get('deadline')
            
            if not deadline_str:
                continue
            
            try:
                #Parse deadline
                deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                
                #Check each reminder interval
                for days_before in reminder_intervals:
                    #Calculate when to send reminder
                    reminder_date = deadline - timedelta(days=days_before)
                    
                    #Check if we should send reminder today
                    if reminder_date.date() == now.date():
                        
                        #Check if we already sent this reminder
                        existing_reminder = DeadlineReminder.query.filter_by(
                            task_id=task_id,
                            days_before=days_before
                        ).first()
                        
                        if existing_reminder:
                            print(f"⏭️ Already sent {days_before}-day reminder for task {task_id}")
                            continue
                        
                        #Send the reminder
                        print(f"📤 Sending {days_before}-day reminder for task {task_id}: {task['title']}")
                        success = send_deadline_reminder(task_id, days_before)
                        
                        if success:
                            reminders_sent += 1
                            print(f"✅ Sent {days_before}-day reminder for task {task_id}")
                        else:
                            print(f"❌ Failed to send {days_before}-day reminder for task {task_id}")
            
            except Exception as e:
                print(f"❌ Error processing task {task_id}: {e}")
                continue
        
        print(f"\n{'='*70}")
        print(f"✅ Deadline reminder check complete. Sent {reminders_sent} reminders.")
        print(f"{'='*70}\n")
        
        return reminders_sent
        
    except Exception as e:
        print(f"❌ Error in check_and_send_deadline_reminders: {e}")
        import traceback
        traceback.print_exc()
        return 0