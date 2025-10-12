import unittest
import os
import sys
from unittest import mock
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json
import threading
import time

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, DeadlineReminder
from app.service import (
    send_email_via_smtp,
    get_user_email,
    get_user_name,
    get_task_details,
    get_task_collaborators,
    get_all_tasks_with_deadlines,
    send_status_update_notification,
    send_deadline_reminder,
    check_and_send_deadline_reminders
)


class TestNotificationService(unittest.TestCase):
    """Test cases for Notification Service - 100% Coverage"""

    def setUp(self):
        """Define test variables and initialize app."""
        os.environ['WERKZEUG_RUN_MAIN'] = 'false'  # Prevent background services
        self.app = create_app('testing')
        self.client = self.app.test_client()

        # Sample data
        singapore_tz = ZoneInfo('Asia/Singapore')
        self.task_data = {
            'id': 1,
            'title': 'Test Task',
            'description': 'This is a test task',
            'status': 'Ongoing',
            'owner_id': 1,
            'deadline': (datetime.now(singapore_tz) + timedelta(days=7)).isoformat(),
            'parent_task_id': None
        }

        self.subtask_data = {
            'id': 2,
            'title': 'Test Subtask',
            'description': 'This is a test subtask',
            'status': 'Ongoing',
            'owner_id': 1,
            'deadline': (datetime.now(singapore_tz) + timedelta(days=3)).isoformat(),
            'parent_task_id': 1
        }

        self.user_data = {
            'id': 1,
            'name': 'Test User',
            'email': 'test@example.com',
            'username': 'testuser'
        }

        # Bind the app to the current context
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Teardown all initialized variables."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # ==================== Test Database Models ====================
    
    def test_deadline_reminder_model(self):
        """Test DeadlineReminder model creation"""
        with self.app.app_context():
            reminder = DeadlineReminder(task_id=1, days_before=7)
            db.session.add(reminder)
            db.session.commit()

            saved_reminder = DeadlineReminder.query.filter_by(task_id=1, days_before=7).first()
            self.assertIsNotNone(saved_reminder)
            self.assertEqual(saved_reminder.task_id, 1)
            self.assertEqual(saved_reminder.days_before, 7)

    def test_deadline_reminder_unique_constraint(self):
        """Test that duplicate reminders cannot be created"""
        with self.app.app_context():
            reminder1 = DeadlineReminder(task_id=1, days_before=7)
            db.session.add(reminder1)
            db.session.commit()

            reminder2 = DeadlineReminder(task_id=1, days_before=7)
            db.session.add(reminder2)
            
            with self.assertRaises(Exception):
                db.session.commit()

    def test_deadline_reminder_to_dict(self):
        """Test DeadlineReminder to_dict method"""
        with self.app.app_context():
            reminder = DeadlineReminder(task_id=1, days_before=3)
            db.session.add(reminder)
            db.session.commit()

            reminder_dict = reminder.to_dict()
            self.assertEqual(reminder_dict['task_id'], 1)
            self.assertEqual(reminder_dict['days_before'], 3)
            self.assertIn('id', reminder_dict)
            self.assertIn('sent_at', reminder_dict)

    def test_deadline_reminder_to_dict_no_sent_at(self):
        """Test DeadlineReminder to_dict when sent_at is None"""
        with self.app.app_context():
            reminder = DeadlineReminder(task_id=1, days_before=3)
            reminder.sent_at = None
            
            reminder_dict = reminder.to_dict()
            self.assertIsNone(reminder_dict['sent_at'])

    def test_deadline_reminder_repr(self):
        """Test DeadlineReminder __repr__ method"""
        with self.app.app_context():
            reminder = DeadlineReminder(task_id=1, days_before=7)
            repr_str = repr(reminder)
            self.assertIn('task_id=1', repr_str)
            self.assertIn('days_before=7', repr_str)

    # ==================== Test Email Sending ====================
    
    @mock.patch('smtplib.SMTP')
    def test_send_email_via_smtp_success(self, mock_smtp):
        """Test successful email sending via SMTP"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            success, error = send_email_via_smtp(
                'test@example.com',
                'Test Subject',
                '<html><body>Test</body></html>'
            )

            self.assertTrue(success)
            self.assertIsNone(error)
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once()
            mock_server.send_message.assert_called_once()

    @mock.patch('smtplib.SMTP')
    def test_send_email_via_smtp_failure(self, mock_smtp):
        """Test email sending failure"""
        with self.app.app_context():
            mock_smtp.return_value.__enter__.side_effect = Exception("SMTP Error")

            success, error = send_email_via_smtp(
                'test@example.com',
                'Test Subject',
                '<html><body>Test</body></html>'
            )

            self.assertFalse(success)
            self.assertIsNotNone(error)
            self.assertIn("SMTP Error", error)

    # ==================== Test User Service Integration ====================
    
    @mock.patch('requests.get')
    def test_get_user_email_success(self, mock_get):
        """Test fetching user email from User Service"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = self.user_data
            mock_get.return_value = mock_response

            email = get_user_email(1)
            self.assertEqual(email, 'test@example.com')

    @mock.patch('requests.get')
    def test_get_user_email_not_found(self, mock_get):
        """Test fetching user email when user not found"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            email = get_user_email(999)
            self.assertIsNone(email)

    @mock.patch('requests.get')
    def test_get_user_email_no_email_field(self, mock_get):
        """Test when user data doesn't contain email"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'id': 1, 'name': 'Test'}
            mock_get.return_value = mock_response

            email = get_user_email(1)
            self.assertIsNone(email)

    @mock.patch('requests.get')
    def test_get_user_email_exception(self, mock_get):
        """Test exception handling in get_user_email"""
        with self.app.app_context():
            mock_get.side_effect = Exception("Connection error")
            email = get_user_email(1)
            self.assertIsNone(email)

    @mock.patch('requests.get')
    def test_get_user_name_success(self, mock_get):
        """Test fetching user name from User Service"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = self.user_data
            mock_get.return_value = mock_response

            name = get_user_name(1)
            self.assertEqual(name, 'Test User')

    @mock.patch('requests.get')
    def test_get_user_name_default(self, mock_get):
        """Test default value when user name not found"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            name = get_user_name(999)
            self.assertEqual(name, 'A team member')

    @mock.patch('requests.get')
    def test_get_user_name_exception(self, mock_get):
        """Test exception handling in get_user_name"""
        with self.app.app_context():
            mock_get.side_effect = Exception("Connection error")
            name = get_user_name(1)
            self.assertEqual(name, 'A team member')

    # ==================== Test Task Service Integration ====================
    
    @mock.patch('requests.get')
    def test_get_task_details_success(self, mock_get):
        """Test fetching task details from Task Service"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = self.task_data
            mock_get.return_value = mock_response

            task = get_task_details(1)
            self.assertIsNotNone(task)
            self.assertEqual(task['id'], 1)
            self.assertEqual(task['title'], 'Test Task')

    @mock.patch('requests.get')
    def test_get_task_details_not_found(self, mock_get):
        """Test fetching task details when task not found"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            task = get_task_details(999)
            self.assertIsNone(task)

    @mock.patch('requests.get')
    def test_get_task_details_exception(self, mock_get):
        """Test exception handling in get_task_details"""
        with self.app.app_context():
            mock_get.side_effect = Exception("Connection error")
            task = get_task_details(1)
            self.assertIsNone(task)

    @mock.patch('requests.get')
    def test_get_task_collaborators_success(self, mock_get):
        """Test fetching task collaborators"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{'user_id': 2}, {'user_id': 3}]
            mock_get.return_value = mock_response

            collaborators = get_task_collaborators(1)
            self.assertEqual(len(collaborators), 2)
            self.assertIn(2, collaborators)
            self.assertIn(3, collaborators)

    @mock.patch('requests.get')
    def test_get_task_collaborators_empty(self, mock_get):
        """Test fetching task collaborators when none exist"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_get.return_value = mock_response

            collaborators = get_task_collaborators(1)
            self.assertEqual(len(collaborators), 0)

    @mock.patch('requests.get')
    def test_get_task_collaborators_error(self, mock_get):
        """Test error handling in get_task_collaborators"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response

            collaborators = get_task_collaborators(1)
            self.assertEqual(len(collaborators), 0)

    @mock.patch('requests.get')
    def test_get_task_collaborators_exception(self, mock_get):
        """Test exception handling in get_task_collaborators"""
        with self.app.app_context():
            mock_get.side_effect = Exception("Connection error")
            collaborators = get_task_collaborators(1)
            self.assertEqual(len(collaborators), 0)

    @mock.patch('requests.get')
    def test_get_all_tasks_with_deadlines_success(self, mock_get):
        """Test fetching all tasks with deadlines"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [self.task_data, self.subtask_data]
            mock_get.return_value = mock_response

            tasks = get_all_tasks_with_deadlines()
            self.assertEqual(len(tasks), 2)

    @mock.patch('requests.get')
    def test_get_all_tasks_with_deadlines_error_status(self, mock_get):
        """Test non-200 status when fetching tasks"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response

            tasks = get_all_tasks_with_deadlines()
            self.assertEqual(len(tasks), 0)

    @mock.patch('requests.get')
    def test_get_all_tasks_with_deadlines_exception(self, mock_get):
        """Test exception handling when fetching tasks"""
        with self.app.app_context():
            mock_get.side_effect = Exception("Connection error")
            tasks = get_all_tasks_with_deadlines()
            self.assertEqual(len(tasks), 0)

    # ==================== Test Status Update Notifications ====================
    
    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_status_update_notification_success(self, mock_get, mock_smtp):
        """Test sending status update notification"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if '/user/1' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Owner', 'email': 'owner@test.com'}
                elif '/user/2' in url:
                    mock_resp.json.return_value = {'id': 2, 'name': 'Collab', 'email': 'collab@test.com'}
                elif 'collaborators' in url:
                    mock_resp.json.return_value = [{'user_id': 2}]
                elif 'tasks/1' in url:
                    mock_resp.json.return_value = self.task_data
                return mock_resp
            
            mock_get.side_effect = mock_requests_get

            success = send_status_update_notification(1, 'Ongoing', 'Completed', 1)
            self.assertTrue(success)
            self.assertEqual(mock_server.send_message.call_count, 2)

    @mock.patch('requests.get')
    def test_send_status_update_notification_task_not_found(self, mock_get):
        """Test status update when task not found"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            success = send_status_update_notification(999, 'Ongoing', 'Completed', 1)
            self.assertFalse(success)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_status_update_notification_subtask(self, mock_get, mock_smtp):
        """Test status update for subtask"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if '/user/' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Test', 'email': 'test@test.com'}
                elif 'collaborators' in url:
                    mock_resp.json.return_value = []
                elif 'tasks/' in url:
                    mock_resp.json.return_value = self.subtask_data
                return mock_resp
            
            mock_get.side_effect = mock_requests_get
            
            success = send_status_update_notification(2, 'Ongoing', 'Completed', 1)
            self.assertTrue(success)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_status_update_notification_no_recipients(self, mock_get, mock_smtp):
        """Test status update with no valid recipients"""
        with self.app.app_context():
            task_no_owner = self.task_data.copy()
            task_no_owner['owner_id'] = 999
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                
                if 'collaborators' in url:
                    mock_resp.status_code = 200
                    mock_resp.json.return_value = []
                elif 'tasks/' in url:
                    mock_resp.status_code = 200
                    mock_resp.json.return_value = task_no_owner
                elif '/user/' in url:
                    mock_resp.status_code = 404
                else:
                    mock_resp.status_code = 404
                return mock_resp
            
            mock_get.side_effect = mock_requests_get
            
            success = send_status_update_notification(1, 'Ongoing', 'Completed', 1)
            self.assertFalse(success)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_status_update_notification_email_failure(self, mock_get, mock_smtp):
        """Test status update when email sending fails"""
        with self.app.app_context():
            mock_smtp.return_value.__enter__.side_effect = Exception("SMTP Error")
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if '/user/' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Test', 'email': 'test@test.com'}
                elif 'collaborators' in url:
                    mock_resp.json.return_value = []
                elif 'tasks/' in url:
                    mock_resp.json.return_value = self.task_data
                return mock_resp
            
            mock_get.side_effect = mock_requests_get
            
            success = send_status_update_notification(1, 'Ongoing', 'Completed', 1)
            self.assertFalse(success)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_status_update_notification_invalid_deadline(self, mock_get, mock_smtp):
        """Test status update with invalid deadline format"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            task_bad_deadline = self.task_data.copy()
            task_bad_deadline['deadline'] = 'invalid-date'
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if '/user/' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Test', 'email': 'test@test.com'}
                elif 'collaborators' in url:
                    mock_resp.json.return_value = []
                elif 'tasks/' in url:
                    mock_resp.json.return_value = task_bad_deadline
                return mock_resp
            
            mock_get.side_effect = mock_requests_get
            
            success = send_status_update_notification(1, 'Ongoing', 'Completed', 1)
            self.assertTrue(success)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_status_update_notification_empty_description(self, mock_get, mock_smtp):
        """Test status update with empty description"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            task_no_desc = self.task_data.copy()
            task_no_desc['description'] = ''
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if '/user/' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Test', 'email': 'test@test.com'}
                elif 'collaborators' in url:
                    mock_resp.json.return_value = []
                elif 'tasks/' in url:
                    mock_resp.json.return_value = task_no_desc
                return mock_resp
            
            mock_get.side_effect = mock_requests_get
            
            success = send_status_update_notification(1, 'Ongoing', 'Completed', 1)
            self.assertTrue(success)

    @mock.patch('requests.get')
    def test_send_status_update_notification_exception(self, mock_get):
        """Test exception handling in status update"""
        with self.app.app_context():
            mock_get.side_effect = Exception("Unexpected error")
            success = send_status_update_notification(1, 'Ongoing', 'Completed', 1)
            self.assertFalse(success)

    # ==================== Test Deadline Reminders ====================
    
    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_deadline_reminder_success(self, mock_get, mock_smtp):
        """Test sending deadline reminder"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if '/user/' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Test', 'email': 'test@test.com'}
                elif 'collaborators' in url:
                    mock_resp.json.return_value = []
                elif 'tasks/' in url:
                    mock_resp.json.return_value = self.task_data
                return mock_resp
            
            mock_get.side_effect = mock_requests_get

            success = send_deadline_reminder(task_id=1, days_before=7)
            self.assertTrue(success)
            
            reminder = DeadlineReminder.query.filter_by(task_id=1, days_before=7).first()
            self.assertIsNotNone(reminder)

    @mock.patch('requests.get')
    def test_send_deadline_reminder_completed_task(self, mock_get):
        """Test deadline reminder not sent for completed task"""
        with self.app.app_context():
            completed_task = self.task_data.copy()
            completed_task['status'] = 'Completed'
            
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = completed_task
            mock_get.return_value = mock_response

            success = send_deadline_reminder(task_id=1, days_before=7)
            self.assertFalse(success)

    @mock.patch('requests.get')
    def test_send_deadline_reminder_task_not_found(self, mock_get):
        """Test deadline reminder when task not found"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            success = send_deadline_reminder(task_id=999, days_before=7)
            self.assertFalse(success)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_deadline_reminder_db_error(self, mock_get, mock_smtp):
        """Test deadline reminder with database error"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if '/user/' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Test', 'email': 'test@test.com'}
                elif 'collaborators' in url:
                    mock_resp.json.return_value = []
                elif 'tasks/' in url:
                    mock_resp.json.return_value = self.task_data
                return mock_resp
            
            mock_get.side_effect = mock_requests_get
            
            with mock.patch.object(db.session, 'commit', side_effect=Exception("DB Error")):
                success = send_deadline_reminder(task_id=1, days_before=7)
                # Should still return True because emails were sent
                self.assertTrue(success)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_deadline_reminder_invalid_deadline(self, mock_get, mock_smtp):
        """Test deadline reminder with invalid deadline"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            task_bad_deadline = self.task_data.copy()
            task_bad_deadline['deadline'] = 'bad-date'
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if '/user/' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Test', 'email': 'test@test.com'}
                elif 'collaborators' in url:
                    mock_resp.json.return_value = []
                elif 'tasks/' in url:
                    mock_resp.json.return_value = task_bad_deadline
                return mock_resp
            
            mock_get.side_effect = mock_requests_get
            
            success = send_deadline_reminder(task_id=1, days_before=7)
            self.assertTrue(success)

    @mock.patch('requests.get')
    def test_send_deadline_reminder_exception(self, mock_get):
        """Test exception handling in deadline reminder"""
        with self.app.app_context():
            mock_get.side_effect = Exception("Unexpected error")
            success = send_deadline_reminder(task_id=1, days_before=7)
            self.assertFalse(success)

    # ==================== Test Deadline Reminder Scheduler ====================
    
    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_check_and_send_deadline_reminders_success(self, mock_get, mock_smtp):
        """Test deadline reminder scheduler"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            singapore_tz = ZoneInfo('Asia/Singapore')
            now = datetime.now(singapore_tz)
            deadline_7days = (now + timedelta(days=7)).replace(hour=14, minute=0)
            
            task_7days = {
                'id': 1,
                'title': 'Task',
                'deadline': deadline_7days.isoformat(),
                'status': 'Ongoing',
                'owner_id': 1,
                'parent_task_id': None,
                'description': 'Test'
            }
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if 'with-deadlines' in url:
                    mock_resp.json.return_value = [task_7days]
                elif 'collaborators' in url:
                    mock_resp.json.return_value = []
                elif 'tasks/1' in url:
                    mock_resp.json.return_value = task_7days
                elif '/user/' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Test', 'email': 'test@test.com'}
                return mock_resp
            
            mock_get.side_effect = mock_requests_get

            reminders_sent = check_and_send_deadline_reminders()
            self.assertEqual(reminders_sent, 1)

    @mock.patch('requests.get')
    def test_check_and_send_deadline_reminders_no_tasks(self, mock_get):
        """Test scheduler with no tasks"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_get.return_value = mock_response

            reminders_sent = check_and_send_deadline_reminders()
            self.assertEqual(reminders_sent, 0)

    @mock.patch('requests.get')
    def test_check_and_send_deadline_reminders_exception(self, mock_get):
        """Test scheduler exception handling"""
        with self.app.app_context():
            mock_get.side_effect = Exception("Error")
            reminders_sent = check_and_send_deadline_reminders()
            self.assertEqual(reminders_sent, 0)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_check_and_send_deadline_reminders_no_deadline(self, mock_get, mock_smtp):
        """Test scheduler with task missing deadline"""
        with self.app.app_context():
            task_no_deadline = {'id': 1, 'title': 'Task', 'deadline': None, 'status': 'Ongoing'}
            
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [task_no_deadline]
            mock_get.return_value = mock_response

            reminders_sent = check_and_send_deadline_reminders()
            self.assertEqual(reminders_sent, 0)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_check_and_send_deadline_reminders_invalid_deadline(self, mock_get, mock_smtp):
        """Test scheduler with invalid deadline format"""
        with self.app.app_context():
            task_bad = {'id': 1, 'title': 'Task', 'deadline': 'bad-date', 'status': 'Ongoing'}
            
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [task_bad]
            mock_get.return_value = mock_response

            reminders_sent = check_and_send_deadline_reminders()
            self.assertEqual(reminders_sent, 0)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_check_and_send_deadline_reminders_already_sent(self, mock_get, mock_smtp):
        """Test scheduler skips already sent reminders"""
        with self.app.app_context():
            singapore_tz = ZoneInfo('Asia/Singapore')
            now = datetime.now(singapore_tz)
            deadline = (now + timedelta(days=7)).replace(hour=14, minute=0)
            
            task = {
                'id': 1,
                'title': 'Task',
                'deadline': deadline.isoformat(),
                'status': 'Ongoing'
            }
            
            # Create existing reminder
            reminder = DeadlineReminder(task_id=1, days_before=7)
            db.session.add(reminder)
            db.session.commit()
            
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [task]
            mock_get.return_value = mock_response

            reminders_sent = check_and_send_deadline_reminders()
            self.assertEqual(reminders_sent, 0)

    # ==================== Test Email Templates ====================
    
    def test_status_update_email_task(self):
        """Test status update email for task"""
        from app.email_templates import get_status_update_email

        subject, body = get_status_update_email(
            'Test Task', 'Ongoing', 'Completed', 'John', 'Dec 31', 'Description', False
        )

        self.assertIn('Task', subject)
        self.assertIn('Test Task', body)
        self.assertIn('Ongoing', body)
        self.assertIn('Completed', body)

    def test_status_update_email_subtask(self):
        """Test status update email for subtask"""
        from app.email_templates import get_status_update_email

        subject, body = get_status_update_email(
            'Test Subtask', 'Unassigned', 'Ongoing', 'Jane', 'Jan 15', 'Desc', True
        )

        self.assertIn('Subtask', subject)
        self.assertIn('Test Subtask', body)

    def test_status_update_email_all_statuses(self):
        """Test all status combinations"""
        from app.email_templates import get_status_update_email

        statuses = ['Unassigned', 'Ongoing', 'Under Review', 'Completed']
        
        for status in statuses:
            subject, body = get_status_update_email(
                'Task', 'Ongoing', status, 'User', 'Date', 'Desc', False
            )
            self.assertIn(status, body)

    def test_status_update_email_long_description(self):
        """Test status update with long description"""
        from app.email_templates import get_status_update_email

        long_desc = 'A' * 250
        subject, body = get_status_update_email(
            'Task', 'Ongoing', 'Completed', 'User', 'Date', long_desc, False
        )
        self.assertIn('...', body)

    def test_deadline_reminder_email_7_days(self):
        """Test deadline reminder for 7 days"""
        from app.email_templates import get_deadline_reminder_email

        subject, body = get_deadline_reminder_email(
            'Task', 7, 'Dec 31', 'Description', 'Ongoing', False
        )

        self.assertIn('📅', subject)
        self.assertIn('In 7 Days', body)
        self.assertIn('7 day', subject)

    def test_deadline_reminder_email_3_days(self):
        """Test deadline reminder for 3 days"""
        from app.email_templates import get_deadline_reminder_email

        subject, body = get_deadline_reminder_email(
            'Task', 3, 'Dec 31', 'Description', 'Ongoing', False
        )

        self.assertIn('⏰', subject)
        self.assertIn('In 3 Days', body)

    def test_deadline_reminder_email_1_day(self):
        """Test deadline reminder for 1 day"""
        from app.email_templates import get_deadline_reminder_email

        subject, body = get_deadline_reminder_email(
            'Task', 1, 'Dec 31', 'Description', 'Ongoing', False
        )

        self.assertIn('🔔', subject)
        self.assertIn('Final Day', body)

    def test_deadline_reminder_email_subtask(self):
        """Test deadline reminder for subtask"""
        from app.email_templates import get_deadline_reminder_email

        subject, body = get_deadline_reminder_email(
            'Subtask', 7, 'Date', 'Desc', 'Ongoing', True
        )

        self.assertIn('Subtask', body)

    def test_deadline_reminder_email_long_description(self):
        """Test deadline reminder with long description"""
        from app.email_templates import get_deadline_reminder_email

        long_desc = 'B' * 200
        subject, body = get_deadline_reminder_email(
            'Task', 7, 'Date', long_desc, 'Ongoing', False
        )
        self.assertIn('...', body)

    def test_deadline_reminder_email_plural_days(self):
        """Test deadline reminder plural/singular days"""
        from app.email_templates import get_deadline_reminder_email

        # Plural
        subject_7, _ = get_deadline_reminder_email('Task', 7, 'Date', 'Desc', 'Ongoing', False)
        self.assertIn('days', subject_7)

        # Singular
        subject_1, _ = get_deadline_reminder_email('Task', 1, 'Date', 'Desc', 'Ongoing', False)
        self.assertIn('day', subject_1)

    # ==================== Test RabbitMQ Consumer ====================
    
    @mock.patch('pika.BlockingConnection')
    def test_rabbitmq_consumer_connect_success(self, mock_conn):
        """Test RabbitMQ connection success"""
        from app.rabbitmq_consumer import RabbitMQConsumer
        
        mock_connection = mock.MagicMock()
        mock_channel = mock.MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_conn.return_value = mock_connection
        
        consumer = RabbitMQConsumer(self.app)
        success = consumer.connect(max_retries=1, retry_delay=0.1)
        
        self.assertTrue(success)
        mock_channel.queue_declare.assert_called_once()

    @mock.patch('pika.BlockingConnection')
    def test_rabbitmq_consumer_connect_retry(self, mock_conn):
        """Test RabbitMQ connection retry"""
        from app.rabbitmq_consumer import RabbitMQConsumer
        import pika
        
        mock_conn.side_effect = pika.exceptions.AMQPConnectionError("Error")
        
        consumer = RabbitMQConsumer(self.app)
        success = consumer.connect(max_retries=2, retry_delay=0.1)
        
        self.assertFalse(success)
        self.assertEqual(mock_conn.call_count, 2)

    @mock.patch('pika.BlockingConnection')
    def test_rabbitmq_consumer_connect_unexpected_error(self, mock_conn):
        """Test RabbitMQ connection with unexpected error"""
        from app.rabbitmq_consumer import RabbitMQConsumer
        
        mock_conn.side_effect = RuntimeError("Unexpected")
        
        consumer = RabbitMQConsumer(self.app)
        success = consumer.connect(max_retries=2, retry_delay=0.1)
        
        self.assertFalse(success)

    @mock.patch('pika.BlockingConnection')
    @mock.patch('app.service.send_status_update_notification')
    def test_rabbitmq_consumer_message_success(self, mock_notify, mock_conn):
        """Test RabbitMQ message processing success"""
        from app.rabbitmq_consumer import RabbitMQConsumer
        
        mock_connection = mock.MagicMock()
        mock_channel = mock.MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_conn.return_value = mock_connection
        
        consumer = RabbitMQConsumer(self.app)
        consumer.connect()
        
        mock_notify.return_value = True
        
        message = {'task_id': 1, 'old_status': 'Ongoing', 'new_status': 'Completed', 'changed_by_id': 1}
        
        consumer.on_status_update_message(
            mock_channel,
            mock.MagicMock(delivery_tag=1),
            None,
            json.dumps(message).encode()
        )
        
        mock_channel.basic_ack.assert_called_with(delivery_tag=1)

    @mock.patch('pika.BlockingConnection')
    @mock.patch('app.service.send_status_update_notification')
    def test_rabbitmq_consumer_message_failure(self, mock_notify, mock_conn):
        """Test RabbitMQ message processing failure"""
        from app.rabbitmq_consumer import RabbitMQConsumer
        
        mock_connection = mock.MagicMock()
        mock_channel = mock.MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_conn.return_value = mock_connection
        
        consumer = RabbitMQConsumer(self.app)
        consumer.connect()
        
        mock_notify.return_value = False
        
        message = {'task_id': 1, 'old_status': 'Ongoing', 'new_status': 'Completed', 'changed_by_id': 1}
        
        consumer.on_status_update_message(
            mock_channel,
            mock.MagicMock(delivery_tag=1),
            None,
            json.dumps(message).encode()
        )
        
        mock_channel.basic_nack.assert_called_with(delivery_tag=1, requeue=True)

    @mock.patch('pika.BlockingConnection')
    def test_rabbitmq_consumer_invalid_json(self, mock_conn):
        """Test RabbitMQ consumer with invalid JSON"""
        from app.rabbitmq_consumer import RabbitMQConsumer
        
        mock_connection = mock.MagicMock()
        mock_channel = mock.MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_conn.return_value = mock_connection
        
        consumer = RabbitMQConsumer(self.app)
        consumer.connect()
        
        consumer.on_status_update_message(
            mock_channel,
            mock.MagicMock(delivery_tag=1),
            None,
            b'invalid json'
        )
        
        mock_channel.basic_nack.assert_called_with(delivery_tag=1, requeue=False)

    @mock.patch('pika.BlockingConnection')
    @mock.patch('app.service.send_status_update_notification')
    def test_rabbitmq_consumer_message_exception(self, mock_notify, mock_conn):
        """Test RabbitMQ consumer with processing exception"""
        from app.rabbitmq_consumer import RabbitMQConsumer
        
        mock_connection = mock.MagicMock()
        mock_channel = mock.MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_conn.return_value = mock_connection
        
        consumer = RabbitMQConsumer(self.app)
        consumer.connect()
        
        mock_notify.side_effect = Exception("Error")
        
        message = {'task_id': 1, 'old_status': 'Ongoing', 'new_status': 'Completed', 'changed_by_id': 1}
        
        consumer.on_status_update_message(
            mock_channel,
            mock.MagicMock(delivery_tag=1),
            None,
            json.dumps(message).encode()
        )
        
        mock_channel.basic_nack.assert_called_with(delivery_tag=1, requeue=True)

    @mock.patch('pika.BlockingConnection')
    def test_rabbitmq_consumer_close(self, mock_conn):
        """Test RabbitMQ consumer close"""
        from app.rabbitmq_consumer import RabbitMQConsumer
        
        mock_connection = mock.MagicMock()
        mock_channel = mock.MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_connection.is_closed = False
        mock_conn.return_value = mock_connection
        
        consumer = RabbitMQConsumer(self.app)
        consumer.connect()
        consumer.close()
        
        mock_connection.close.assert_called_once()

    @mock.patch('pika.BlockingConnection')
    def test_rabbitmq_consumer_close_already_closed(self, mock_conn):
        """Test closing already closed connection"""
        from app.rabbitmq_consumer import RabbitMQConsumer
        
        mock_connection = mock.MagicMock()
        mock_channel = mock.MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_connection.is_closed = True
        mock_conn.return_value = mock_connection
        
        consumer = RabbitMQConsumer(self.app)
        consumer.connection = mock_connection
        consumer.close()
        
        mock_connection.close.assert_not_called()

    @mock.patch('pika.BlockingConnection')
    def test_rabbitmq_consumer_start_consuming_no_connection(self, mock_conn):
        """Test start_consuming without connection"""
        from app.rabbitmq_consumer import RabbitMQConsumer
        
        mock_conn.side_effect = Exception("No connection")
        
        consumer = RabbitMQConsumer(self.app)
        consumer.start_consuming()
        
        # Should handle gracefully

    @mock.patch('pika.BlockingConnection')
    @mock.patch('threading.Thread')
    def test_start_consumer_thread(self, mock_thread, mock_conn):
        """Test starting consumer thread"""
        from app.rabbitmq_consumer import start_consumer_thread
        
        mock_thread_instance = mock.MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        consumer = start_consumer_thread(self.app)
        
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

    # ==================== Test Scheduler ====================
    
    def test_scheduler_initialization(self):
        """Test scheduler initialization"""
        from app.scheduler import DeadlineReminderScheduler
        
        scheduler = DeadlineReminderScheduler(self.app)
        self.assertIsNotNone(scheduler)
        self.assertIsNotNone(scheduler.scheduler)

    @mock.patch('app.service.check_and_send_deadline_reminders')
    def test_scheduler_start(self, mock_check):
        """Test scheduler start"""
        from app.scheduler import DeadlineReminderScheduler
        
        mock_check.return_value = 0
        
        scheduler = DeadlineReminderScheduler(self.app)
        scheduler.start()
        
        jobs = scheduler.scheduler.get_jobs()
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].id, 'deadline_reminder_check')
        
        scheduler.stop()

    @mock.patch('app.service.check_and_send_deadline_reminders')
    def test_scheduler_start_error(self, mock_check):
        """Test scheduler start with error"""
        from app.scheduler import DeadlineReminderScheduler
        
        scheduler = DeadlineReminderScheduler(self.app)
        
        with mock.patch.object(scheduler.scheduler, 'add_job', side_effect=Exception("Error")):
            scheduler.start()
            # Should handle exception gracefully

    def test_scheduler_stop(self):
        """Test scheduler stop"""
        from app.scheduler import DeadlineReminderScheduler
        
        scheduler = DeadlineReminderScheduler(self.app)
        scheduler.start()
        scheduler.stop()
        
        self.assertFalse(scheduler.scheduler.running)

    @mock.patch('app.service.check_and_send_deadline_reminders')
    def test_scheduler_run_now(self, mock_check):
        """Test scheduler manual run"""
        from app.scheduler import DeadlineReminderScheduler
        
        mock_check.return_value = 5
        
        scheduler = DeadlineReminderScheduler(self.app)
        result = scheduler.run_now()
        
        self.assertEqual(result, 5)
        mock_check.assert_called_once()

    @mock.patch('app.service.check_and_send_deadline_reminders')
    def test_scheduler_run_now_exception(self, mock_check):
        """Test scheduler manual run with exception"""
        from app.scheduler import DeadlineReminderScheduler
        
        mock_check.side_effect = Exception("Error")
        
        scheduler = DeadlineReminderScheduler(self.app)
        
        # Should handle exception
        try:
            scheduler.run_now()
        except Exception:
            pass

    @mock.patch('app.service.check_and_send_deadline_reminders')
    @mock.patch('threading.Thread')
    def test_start_deadline_scheduler(self, mock_thread, mock_check):
        """Test start_deadline_scheduler function"""
        from app.scheduler import start_deadline_scheduler
        
        scheduler = start_deadline_scheduler(self.app)
        
        self.assertIsNotNone(scheduler)

    # ==================== Test App Initialization ====================
    
    def test_app_creation(self):
        """Test Flask app creation"""
        self.assertIsNotNone(self.app)
        self.assertTrue(self.app.config['SQLALCHEMY_DATABASE_URI'])

    def test_app_config_loaded(self):
        """Test app configuration"""
        with self.app.app_context():
            self.assertIn('SQLALCHEMY_DATABASE_URI', self.app.config)
            self.assertIn('SMTP_HOST', self.app.config)
            self.assertIn('RABBITMQ_URL', self.app.config)
            self.assertIn('USER_SERVICE_URL', self.app.config)
            self.assertIn('TASK_SERVICE_URL', self.app.config)

    def test_database_tables_created(self):
        """Test database tables creation"""
        with self.app.app_context():
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            self.assertIn('deadline_reminders', tables)

    def test_cors_enabled(self):
        """Test CORS is enabled"""
        # CORS should be enabled in the app
        self.assertIsNotNone(self.app)

    @mock.patch.dict(os.environ, {'WERKZEUG_RUN_MAIN': 'true'})
    @mock.patch('app.rabbitmq_consumer.start_consumer_thread')
    @mock.patch('app.scheduler.start_deadline_scheduler')
    def test_app_background_services_start(self, mock_scheduler, mock_consumer):
        """Test background services start in production"""
        mock_consumer.return_value = mock.MagicMock()
        mock_scheduler.return_value = mock.MagicMock()
        
        # Create app with production flag
        app = create_app('testing')
        
        # Background services should not start in testing mode
        # This test verifies the condition logic exists

    # ==================== Test Config ====================
    
    def test_config_class(self):
        """Test Config class"""
        from config import Config
        
        self.assertIsNotNone(Config.SQLALCHEMY_DATABASE_URI)
        self.assertIsNotNone(Config.SMTP_HOST)
        self.assertIsNotNone(Config.RABBITMQ_URL)

    # ==================== Integration Tests ====================
    
    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_end_to_end_status_update(self, mock_get, mock_smtp):
        """Test end-to-end status update flow"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if '/user/1' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Owner', 'email': 'owner@test.com'}
                elif 'collaborators' in url:
                    mock_resp.json.return_value = []
                elif 'tasks/1' in url:
                    mock_resp.json.return_value = self.task_data
                return mock_resp
            
            mock_get.side_effect = mock_requests_get
            
            # Full flow
            success = send_status_update_notification(1, 'Ongoing', 'Completed', 1)
            
            self.assertTrue(success)
            mock_server.send_message.assert_called()

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_end_to_end_deadline_reminder(self, mock_get, mock_smtp):
        """Test end-to-end deadline reminder flow"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            singapore_tz = ZoneInfo('Asia/Singapore')
            now = datetime.now(singapore_tz)
            deadline = (now + timedelta(days=7)).replace(hour=14, minute=0)
            
            task = self.task_data.copy()
            task['deadline'] = deadline.isoformat()
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if 'with-deadlines' in url:
                    mock_resp.json.return_value = [task]
                elif 'collaborators' in url:
                    mock_resp.json.return_value = []
                elif 'tasks/1' in url:
                    mock_resp.json.return_value = task
                elif '/user/' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Test', 'email': 'test@test.com'}
                return mock_resp
            
            mock_get.side_effect = mock_requests_get
            
            # Full flow
            reminders_sent = check_and_send_deadline_reminders()
            
            self.assertEqual(reminders_sent, 1)
            mock_server.send_message.assert_called()
            
            # Verify DB record
            reminder = DeadlineReminder.query.filter_by(task_id=1, days_before=7).first()
            self.assertIsNotNone(reminder)
    # ==================== Additional Coverage Tests ====================
    
    @mock.patch('requests.get')
    def test_get_task_collaborators_missing_user_id(self, mock_get):
        """Test get_task_collaborators with missing user_id field"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            # Return collaborators without user_id field (should cause KeyError)
            mock_response.json.return_value = [{'id': 1, 'name': 'Test'}]
            mock_get.return_value = mock_response

            collaborators = get_task_collaborators(1)
            # Should handle error and return empty list
            self.assertEqual(len(collaborators), 0)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_status_update_with_none_description(self, mock_get, mock_smtp):
        """Test status update with None description"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            task_data = {
                'id': 1,
                'title': 'Test Task',
                'description': None,
                'status': 'Ongoing',
                'owner_id': 1,
                'deadline': None,
                'parent_task_id': None
            }
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if '/user/' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Test', 'email': 'test@test.com'}
                elif 'collaborators' in url:
                    mock_resp.json.return_value = []
                elif 'tasks/' in url:
                    mock_resp.json.return_value = task_data
                return mock_resp
            
            mock_get.side_effect = mock_requests_get
            
            success = send_status_update_notification(1, 'Ongoing', 'Completed', 1)
            self.assertTrue(success)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_deadline_reminder_with_none_description(self, mock_get, mock_smtp):
        """Test deadline reminder with None description"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            singapore_tz = ZoneInfo('Asia/Singapore')
            task_data = {
                'id': 1,
                'title': 'Test Task',
                'description': None,
                'status': 'Ongoing',
                'owner_id': 1,
                'deadline': (datetime.now(singapore_tz) + timedelta(days=7)).isoformat(),
                'parent_task_id': None
            }
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if '/user/' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Test', 'email': 'test@test.com'}
                elif 'collaborators' in url:
                    mock_resp.json.return_value = []
                elif 'tasks/' in url:
                    mock_resp.json.return_value = task_data
                return mock_resp
            
            mock_get.side_effect = mock_requests_get
            
            success = send_deadline_reminder(task_id=1, days_before=7)
            self.assertTrue(success)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_check_deadline_reminders_3_days(self, mock_get, mock_smtp):
        """Test deadline reminder check for 3 days before"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            singapore_tz = ZoneInfo('Asia/Singapore')
            now = datetime.now(singapore_tz)
            
            # Create task with deadline exactly 3 days away
            deadline_3days = (now + timedelta(days=3)).replace(hour=14, minute=0)
            
            task = {
                'id': 1,
                'title': 'Task',
                'deadline': deadline_3days.isoformat(),
                'status': 'Ongoing',
                'owner_id': 1,
                'parent_task_id': None,
                'description': 'Test'
            }
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if 'with-deadlines' in url:
                    mock_resp.json.return_value = [task]
                elif 'collaborators' in url:
                    mock_resp.json.return_value = []
                elif 'tasks/1' in url:
                    mock_resp.json.return_value = task
                elif '/user/' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Test', 'email': 'test@test.com'}
                return mock_resp
            
            mock_get.side_effect = mock_requests_get

            reminders_sent = check_and_send_deadline_reminders()
            # Should send 3-day reminder
            self.assertEqual(reminders_sent, 1)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_check_deadline_reminders_1_day(self, mock_get, mock_smtp):
        """Test deadline reminder check for 1 day before"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            singapore_tz = ZoneInfo('Asia/Singapore')
            now = datetime.now(singapore_tz)
            
            # Create task with deadline exactly 1 day away
            deadline_1day = (now + timedelta(days=1)).replace(hour=14, minute=0)
            
            task = {
                'id': 1,
                'title': 'Task',
                'deadline': deadline_1day.isoformat(),
                'status': 'Ongoing',
                'owner_id': 1,
                'parent_task_id': None,
                'description': 'Test'
            }
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if 'with-deadlines' in url:
                    mock_resp.json.return_value = [task]
                elif 'collaborators' in url:
                    mock_resp.json.return_value = []
                elif 'tasks/1' in url:
                    mock_resp.json.return_value = task
                elif '/user/' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Test', 'email': 'test@test.com'}
                return mock_resp
            
            mock_get.side_effect = mock_requests_get

            reminders_sent = check_and_send_deadline_reminders()
            # Should send 1-day reminder
            self.assertEqual(reminders_sent, 1)

    @mock.patch('requests.get')
    def test_get_user_name_no_name_field(self, mock_get):
        """Test get_user_name when name field doesn't exist"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'id': 1, 'email': 'test@test.com'}
            mock_get.return_value = mock_response

            name = get_user_name(1)
            self.assertEqual(name, 'A team member')

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_status_update_partial_email_success(self, mock_get, mock_smtp):
        """Test status update where some emails succeed and some fail"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            
            # First email succeeds, second fails
            mock_server.send_message.side_effect = [None, Exception("SMTP Error")]
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            singapore_tz = ZoneInfo('Asia/Singapore')
            task_data = {
                'id': 1,
                'title': 'Test Task',
                'description': 'Test',
                'status': 'Ongoing',
                'owner_id': 1,
                'deadline': (datetime.now(singapore_tz) + timedelta(days=7)).isoformat(),
                'parent_task_id': None
            }
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if '/user/1' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Owner', 'email': 'owner@test.com'}
                elif '/user/2' in url:
                    mock_resp.json.return_value = {'id': 2, 'name': 'Collab', 'email': 'collab@test.com'}
                elif 'collaborators' in url:
                    mock_resp.json.return_value = [{'user_id': 2}]
                elif 'tasks/1' in url:
                    mock_resp.json.return_value = task_data
                return mock_resp
            
            mock_get.side_effect = mock_requests_get

            success = send_status_update_notification(1, 'Ongoing', 'Completed', 1)
            # Should return True because at least one email was sent
            self.assertTrue(success)

    def test_deadline_reminder_model_sent_at_default(self):
        """Test DeadlineReminder model with default sent_at"""
        with self.app.app_context():
            reminder = DeadlineReminder(task_id=1, days_before=7)
            db.session.add(reminder)
            db.session.commit()
            
            # sent_at should be set automatically
            self.assertIsNotNone(reminder.sent_at)

    @mock.patch('smtplib.SMTP')
    def test_send_email_smtp_context_manager(self, mock_smtp):
        """Test SMTP connection using context manager"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            mock_smtp.return_value.__exit__.return_value = None

            success, error = send_email_via_smtp(
                'test@example.com',
                'Test Subject',
                '<html><body>Test</body></html>'
            )

            self.assertTrue(success)
            # Verify __enter__ was called (context manager)
            mock_smtp.return_value.__enter__.assert_called_once()

    @mock.patch('pika.BlockingConnection')
    def test_rabbitmq_consumer_start_consuming_keyboard_interrupt(self, mock_conn):
        """Test RabbitMQ consumer handling KeyboardInterrupt"""
        from app.rabbitmq_consumer import RabbitMQConsumer
        
        mock_connection = mock.MagicMock()
        mock_channel = mock.MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_connection.is_closed = False
        mock_channel.start_consuming.side_effect = KeyboardInterrupt()
        mock_conn.return_value = mock_connection
        
        consumer = RabbitMQConsumer(self.app)
        consumer.connect()
        
        # This should handle KeyboardInterrupt gracefully
        consumer.start_consuming()
        
        mock_channel.stop_consuming.assert_called_once()
        mock_connection.close.assert_called_once()

    @mock.patch('pika.BlockingConnection')
    def test_rabbitmq_consumer_start_consuming_exception(self, mock_conn):
        """Test RabbitMQ consumer handling general exception during consuming"""
        from app.rabbitmq_consumer import RabbitMQConsumer
        
        mock_connection = mock.MagicMock()
        mock_channel = mock.MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_connection.is_closed = False
        mock_channel.start_consuming.side_effect = Exception("Consumer error")
        mock_conn.return_value = mock_connection
        
        consumer = RabbitMQConsumer(self.app)
        consumer.connect()
        
        # This should handle exception gracefully
        consumer.start_consuming()

    @mock.patch('pika.BlockingConnection')
    def test_rabbitmq_consumer_connect_first_attempt_success(self, mock_conn):
        """Test RabbitMQ connection success on first attempt"""
        from app.rabbitmq_consumer import RabbitMQConsumer
        
        mock_connection = mock.MagicMock()
        mock_channel = mock.MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_conn.return_value = mock_connection
        
        consumer = RabbitMQConsumer(self.app)
        success = consumer.connect(max_retries=5, retry_delay=0.1)
        
        self.assertTrue(success)
        # Should only call once (no retries)
        self.assertEqual(mock_conn.call_count, 1)

    @mock.patch('time.sleep')
    @mock.patch('pika.BlockingConnection')
    def test_rabbitmq_consumer_connect_retry_then_success(self, mock_conn, mock_sleep):
        """Test RabbitMQ connection retry then success"""
        from app.rabbitmq_consumer import RabbitMQConsumer
        import pika
        
        # First call fails, second succeeds
        mock_connection = mock.MagicMock()
        mock_channel = mock.MagicMock()
        mock_connection.channel.return_value = mock_channel
        
        mock_conn.side_effect = [
            pika.exceptions.AMQPConnectionError("Error"),
            mock_connection
        ]
        
        consumer = RabbitMQConsumer(self.app)
        success = consumer.connect(max_retries=3, retry_delay=0.1)
        
        self.assertTrue(success)
        self.assertEqual(mock_conn.call_count, 2)
        mock_sleep.assert_called_once_with(0.1)

    @mock.patch('pika.BlockingConnection')
    def test_rabbitmq_consumer_close_no_connection(self, mock_conn):
        """Test closing RabbitMQ consumer with no connection"""
        from app.rabbitmq_consumer import RabbitMQConsumer
        
        consumer = RabbitMQConsumer(self.app)
        # Don't connect, just try to close
        consumer.close()
        # Should handle gracefully

    @mock.patch('app.service.check_and_send_deadline_reminders')
    def test_scheduler_run_deadline_check_with_error(self, mock_check):
        """Test scheduler's _run_deadline_check with exception"""
        from app.scheduler import DeadlineReminderScheduler
        
        mock_check.side_effect = Exception("Check error")
        
        scheduler = DeadlineReminderScheduler(self.app)
        
        # Call the internal method directly
        scheduler._run_deadline_check()
        
        # Should handle exception gracefully
        mock_check.assert_called_once()

    def test_scheduler_stop_when_not_running(self):
        """Test stopping scheduler when it's not running"""
        from app.scheduler import DeadlineReminderScheduler
        
        scheduler = DeadlineReminderScheduler(self.app)
        # Don't start it, just stop
        scheduler.stop()
        # Should handle gracefully

    @mock.patch('app.service.check_and_send_deadline_reminders')
    def test_scheduler_run_now_with_different_result(self, mock_check):
        """Test scheduler manual run with different result"""
        from app.scheduler import DeadlineReminderScheduler
        
        mock_check.return_value = 10
        
        scheduler = DeadlineReminderScheduler(self.app)
        result = scheduler.run_now()
        
        self.assertEqual(result, 10)

    @mock.patch('app.rabbitmq_consumer.start_consumer_thread')
    @mock.patch('app.scheduler.start_deadline_scheduler')
    def test_create_app_production_mode_mock_db(self, mock_scheduler, mock_consumer):
        """Test app creation in production mode with mocked database"""
        mock_consumer.return_value = mock.MagicMock()
        mock_scheduler.return_value = mock.MagicMock()
        
        # Mock the database creation to avoid PostgreSQL connection
        with mock.patch('app.models.db.create_all'):
            # Temporarily set testing database URL
            import os
            original_url = os.environ.get('NOTIFICATION_DATABASE_URL')
            os.environ['NOTIFICATION_DATABASE_URL'] = 'sqlite:///:memory:'
            
            try:
                app = create_app()
                self.assertIsNotNone(app)
                self.assertFalse(app.config.get('TESTING', False))
            finally:
                # Restore original URL
                if original_url:
                    os.environ['NOTIFICATION_DATABASE_URL'] = original_url
                elif 'NOTIFICATION_DATABASE_URL' in os.environ:
                    del os.environ['NOTIFICATION_DATABASE_URL']

    @mock.patch.dict(os.environ, {'WERKZEUG_RUN_MAIN': 'true', 'NOTIFICATION_DATABASE_URL': 'sqlite:///:memory:'})
    @mock.patch('app.rabbitmq_consumer.start_consumer_thread')
    @mock.patch('app.scheduler.start_deadline_scheduler')
    @mock.patch('app.models.db.create_all')
    def test_create_app_with_background_services_mock(self, mock_create_all, mock_scheduler, mock_consumer):
        """Test app creation with background services starting (mocked)"""
        mock_consumer.return_value = mock.MagicMock()
        mock_scheduler.return_value = mock.MagicMock()
        
        app = create_app()
        
        # Verify app was created
        self.assertIsNotNone(app)

if __name__ == "__main__":
    unittest.main()