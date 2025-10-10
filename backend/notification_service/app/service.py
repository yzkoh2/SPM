import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from datetime import datetime
import requests
from .email_templates import get_status_update_email


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