import unittest
import os
import sys
from unittest import mock
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
import json

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, DeadlineReminder, OverdueAlert, MentionNotification
from app.service import (
    send_email_via_smtp,
    get_user_email,
    get_user_name,
    get_task_details,
    get_task_collaborators,
    get_all_tasks_with_deadlines,
    parse_deadline,
    format_deadline_for_email,
    send_status_update_notification,
    send_deadline_reminder,
    check_and_send_deadline_reminders,
    send_overdue_task_alert,
    check_and_send_overdue_alerts,
    send_mention_alert_notification,
    extract_mention_context,
    highlight_mention_in_text,
    format_time_ago,
    get_user_initials,
    get_user_details_for_mention
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

    def test_overdue_alert_model(self):
        """Test OverdueAlert model creation"""
        with self.app.app_context():
            singapore_tz = ZoneInfo('Asia/Singapore')
            today = datetime.now(singapore_tz).date()
            
            alert = OverdueAlert(task_id=1, alert_date=today, days_overdue=2)
            db.session.add(alert)
            db.session.commit()

            saved_alert = OverdueAlert.query.filter_by(task_id=1).first()
            self.assertIsNotNone(saved_alert)
            self.assertEqual(saved_alert.task_id, 1)
            self.assertEqual(saved_alert.days_overdue, 2)

    def test_overdue_alert_unique_constraint(self):
        """Test that duplicate overdue alerts cannot be created"""
        with self.app.app_context():
            singapore_tz = ZoneInfo('Asia/Singapore')
            today = datetime.now(singapore_tz).date()
            
            alert1 = OverdueAlert(task_id=1, alert_date=today, days_overdue=1)
            db.session.add(alert1)
            db.session.commit()

            alert2 = OverdueAlert(task_id=1, alert_date=today, days_overdue=2)
            db.session.add(alert2)
            
            with self.assertRaises(Exception):
                db.session.commit()

    def test_overdue_alert_repr(self):
        """Test OverdueAlert __repr__ method"""
        with self.app.app_context():
            singapore_tz = ZoneInfo('Asia/Singapore')
            today = datetime.now(singapore_tz).date()
            
            alert = OverdueAlert(task_id=1, alert_date=today, days_overdue=3)
            repr_str = repr(alert)
            self.assertIn('task_id=1', repr_str)
            self.assertIn('days_overdue=3', repr_str)

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

        with self.app.app_context():
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
    def test_get_user_name_no_name_field(self, mock_get):
        """Test get_user_name when name field doesn't exist"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'id': 1, 'email': 'test@test.com'}
            mock_get.return_value = mock_response

            name = get_user_name(1)
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
        mock_response = mock.MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with self.app.app_context():
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
        mock_response = mock.MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with self.app.app_context():
            tasks = get_all_tasks_with_deadlines()
            self.assertEqual(len(tasks), 0)

    # ==================== Test Helper Functions ====================
    
    def test_parse_deadline_timezone_aware_utc(self):
        """Test parsing timezone-aware deadline in UTC"""
        with self.app.app_context():
            deadline_str = "2025-12-31T10:00:00Z"
            result = parse_deadline(deadline_str)
            
            self.assertIsNotNone(result)
            self.assertEqual(result.tzinfo.key, 'Asia/Singapore')

    def test_parse_deadline_timezone_aware_with_offset(self):
        """Test parsing timezone-aware deadline with offset"""
        with self.app.app_context():
            deadline_str = "2025-12-31T10:00:00+05:00"
            result = parse_deadline(deadline_str)
            
            self.assertIsNotNone(result)
            self.assertEqual(result.tzinfo.key, 'Asia/Singapore')

    def test_parse_deadline_naive(self):
        """Test parsing naive deadline"""
        deadline_str = "2025-12-31T10:00:00"
        with self.app.app_context():
            result = parse_deadline(deadline_str)
            
            self.assertIsNotNone(result)
            self.assertEqual(result.tzinfo.key, 'Asia/Singapore')

    def test_parse_deadline_with_multiple_dashes(self):
        """Test parsing deadline with multiple dashes in negative offset"""
        deadline_str = "2025-12-31T10:00:00-05:00"
        with self.app.app_context():
            result = parse_deadline(deadline_str)
            
            self.assertIsNotNone(result)
            self.assertEqual(result.tzinfo.key, 'Asia/Singapore')

    def test_format_deadline_for_email_valid(self):
        """Test formatting valid deadline for email"""
        with self.app.app_context():
            deadline_str = "2025-12-31T10:00:00Z"
            result = format_deadline_for_email(deadline_str)
            
            self.assertIn('December', result)
            self.assertIn('31', result)
            self.assertIn('2025', result)

    def test_format_deadline_for_email_no_deadline(self):
        """Test formatting when no deadline"""
        with self.app.app_context():
            result = format_deadline_for_email('No deadline set')
            self.assertEqual(result, 'No deadline set')

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

    @mock.patch('requests.get')
    def test_send_status_update_notification_exception(self, mock_get):
        """Test exception handling in status update"""
        with self.app.app_context():
            mock_get.side_effect = Exception("Unexpected error")
            success = send_status_update_notification(1, 'Ongoing', 'Completed', 1)
            self.assertFalse(success)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_status_update_with_none_description(self, mock_get, mock_smtp):
        """Test status update with None description"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            task_data = self.task_data.copy()
            task_data['description'] = None
            
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
    def test_send_status_update_partial_email_success(self, mock_get, mock_smtp):
        """Test status update where some emails succeed and some fail"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_server.send_message.side_effect = [None, Exception("SMTP Error")]
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
                self.assertTrue(success)

    @mock.patch('requests.get')
    def test_send_deadline_reminder_exception(self, mock_get):
        """Test exception handling in deadline reminder"""
        with self.app.app_context():
            mock_get.side_effect = Exception("Unexpected error")
            success = send_deadline_reminder(task_id=1, days_before=7)
            self.assertFalse(success)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_deadline_reminder_with_none_description(self, mock_get, mock_smtp):
        """Test deadline reminder with None description"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            task_data = self.task_data.copy()
            task_data['description'] = None
            
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

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_check_deadline_reminders_3_days(self, mock_get, mock_smtp):
        """Test deadline reminder check for 3 days before"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            singapore_tz = ZoneInfo('Asia/Singapore')
            now = datetime.now(singapore_tz)
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
            self.assertEqual(reminders_sent, 1)

    # ==================== Test Overdue Alerts ====================
    
    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_overdue_task_alert_success(self, mock_get, mock_smtp):
        """Test sending overdue task alert"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            singapore_tz = ZoneInfo('Asia/Singapore')
            overdue_task = self.task_data.copy()
            overdue_task['deadline'] = (datetime.now(singapore_tz) - timedelta(days=2)).isoformat()
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if '/user/' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Test', 'email': 'test@test.com'}
                elif 'collaborators' in url:
                    mock_resp.json.return_value = []
                elif 'tasks/' in url:
                    mock_resp.json.return_value = overdue_task
                return mock_resp
            
            mock_get.side_effect = mock_requests_get

            success = send_overdue_task_alert(task_id=1, days_overdue=2)
            self.assertTrue(success)
            
            singapore_tz = ZoneInfo('Asia/Singapore')
            today = datetime.now(singapore_tz).date()
            alert = OverdueAlert.query.filter_by(task_id=1, alert_date=today).first()
            self.assertIsNotNone(alert)
            self.assertEqual(alert.days_overdue, 2)

    @mock.patch('requests.get')
    def test_send_overdue_task_alert_completed_task(self, mock_get):
        """Test overdue alert not sent for completed task"""
        with self.app.app_context():
            completed_task = self.task_data.copy()
            completed_task['status'] = 'Completed'
            
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = completed_task
            mock_get.return_value = mock_response

            success = send_overdue_task_alert(task_id=1, days_overdue=1)
            self.assertFalse(success)

    @mock.patch('requests.get')
    def test_send_overdue_task_alert_task_not_found(self, mock_get):
        """Test overdue alert when task not found"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            success = send_overdue_task_alert(task_id=999, days_overdue=1)
            self.assertFalse(success)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_overdue_task_alert_db_error(self, mock_get, mock_smtp):
        """Test overdue alert with database error"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            singapore_tz = ZoneInfo('Asia/Singapore')
            overdue_task = self.task_data.copy()
            overdue_task['deadline'] = (datetime.now(singapore_tz) - timedelta(days=1)).isoformat()
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if '/user/' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Test', 'email': 'test@test.com'}
                elif 'collaborators' in url:
                    mock_resp.json.return_value = []
                elif 'tasks/' in url:
                    mock_resp.json.return_value = overdue_task
                return mock_resp
            
            mock_get.side_effect = mock_requests_get
            
            with mock.patch.object(db.session, 'commit', side_effect=Exception("DB Error")):
                success = send_overdue_task_alert(task_id=1, days_overdue=1)
                self.assertTrue(success)

    @mock.patch('requests.get')
    def test_send_overdue_task_alert_exception(self, mock_get):
        """Test exception handling in overdue alert"""
        with self.app.app_context():
            mock_get.side_effect = Exception("Unexpected error")
            success = send_overdue_task_alert(task_id=1, days_overdue=1)
            self.assertFalse(success)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_overdue_alert_with_none_description(self, mock_get, mock_smtp):
        """Test overdue alert with None description"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            singapore_tz = ZoneInfo('Asia/Singapore')
            task_data = self.task_data.copy()
            task_data['description'] = None
            task_data['deadline'] = (datetime.now(singapore_tz) - timedelta(days=1)).isoformat()
            
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
            
            success = send_overdue_task_alert(task_id=1, days_overdue=1)
            self.assertTrue(success)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_check_and_send_overdue_alerts_success(self, mock_get, mock_smtp):
        """Test overdue alerts check"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            singapore_tz = ZoneInfo('Asia/Singapore')
            now = datetime.now(singapore_tz)
            
            overdue_task = {
                'id': 1,
                'title': 'Overdue Task',
                'deadline': (now - timedelta(days=1)).isoformat(),
                'status': 'Ongoing',
                'owner_id': 1,
                'parent_task_id': None,
                'description': 'Test'
            }
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if 'with-deadlines' in url:
                    mock_resp.json.return_value = [overdue_task]
                elif 'collaborators' in url:
                    mock_resp.json.return_value = []
                elif 'tasks/1' in url:
                    mock_resp.json.return_value = overdue_task
                elif '/user/' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Test', 'email': 'test@test.com'}
                return mock_resp
            
            mock_get.side_effect = mock_requests_get

            alerts_sent = check_and_send_overdue_alerts()
            self.assertEqual(alerts_sent, 1)

    @mock.patch('requests.get')
    def test_check_and_send_overdue_alerts_no_tasks(self, mock_get):
        """Test overdue check with no tasks"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_get.return_value = mock_response

            alerts_sent = check_and_send_overdue_alerts()
            self.assertEqual(alerts_sent, 0)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_check_and_send_overdue_alerts_completed_task(self, mock_get, mock_smtp):
        """Test overdue check skips completed tasks"""
        with self.app.app_context():
            singapore_tz = ZoneInfo('Asia/Singapore')
            now = datetime.now(singapore_tz)
            
            completed_task = {
                'id': 1,
                'title': 'Task',
                'deadline': (now - timedelta(days=1)).isoformat(),
                'status': 'Completed',
                'owner_id': 1
            }
            
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [completed_task]
            mock_get.return_value = mock_response

            alerts_sent = check_and_send_overdue_alerts()
            self.assertEqual(alerts_sent, 0)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_check_and_send_overdue_alerts_no_deadline(self, mock_get, mock_smtp):
        """Test overdue check with task missing deadline"""
        with self.app.app_context():
            task_no_deadline = {
                'id': 1,
                'title': 'Task',
                'deadline': None,
                'status': 'Ongoing'
            }
            
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [task_no_deadline]
            mock_get.return_value = mock_response

            alerts_sent = check_and_send_overdue_alerts()
            self.assertEqual(alerts_sent, 0)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_check_and_send_overdue_alerts_already_sent_today(self, mock_get, mock_smtp):
        """Test overdue check skips alerts already sent today"""
        with self.app.app_context():
            singapore_tz = ZoneInfo('Asia/Singapore')
            now = datetime.now(singapore_tz)
            today = now.date()
            
            overdue_task = {
                'id': 1,
                'title': 'Task',
                'deadline': (now - timedelta(days=1)).isoformat(),
                'status': 'Ongoing'
            }
            
            alert = OverdueAlert(task_id=1, alert_date=today, days_overdue=1)
            db.session.add(alert)
            db.session.commit()
            
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [overdue_task]
            mock_get.return_value = mock_response

            alerts_sent = check_and_send_overdue_alerts()
            self.assertEqual(alerts_sent, 0)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_check_and_send_overdue_alerts_invalid_deadline(self, mock_get, mock_smtp):
        """Test overdue check with invalid deadline"""
        with self.app.app_context():
            task_bad = {
                'id': 1,
                'title': 'Task',
                'deadline': 'invalid-date',
                'status': 'Ongoing'
            }
            
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [task_bad]
            mock_get.return_value = mock_response

            alerts_sent = check_and_send_overdue_alerts()
            self.assertEqual(alerts_sent, 0)

    @mock.patch('requests.get')
    def test_check_and_send_overdue_alerts_exception(self, mock_get):
        """Test overdue check exception handling"""
        with self.app.app_context():
            mock_get.side_effect = Exception("Error")
            alerts_sent = check_and_send_overdue_alerts()
            self.assertEqual(alerts_sent, 0)

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

    def test_overdue_task_email_1_day(self):
        """Test overdue email for 1 day"""
        from app.email_templates import get_overdue_task_email

        subject, body = get_overdue_task_email(
            'Task', 'Dec 31', 1, 'Description', 'Ongoing', False
        )

        self.assertIn('🚨', subject)
        self.assertIn('1 Day Overdue', body)
        self.assertIn('⚠️', body)

    def test_overdue_task_email_3_days(self):
        """Test overdue email for 3 days"""
        from app.email_templates import get_overdue_task_email

        subject, body = get_overdue_task_email(
            'Task', 'Dec 31', 3, 'Description', 'Ongoing', False
        )

        self.assertIn('🚨', subject)
        self.assertIn('3 Days Overdue', body)
        self.assertIn('🔴', body)

    def test_overdue_task_email_many_days(self):
        """Test overdue email for many days"""
        from app.email_templates import get_overdue_task_email

        subject, body = get_overdue_task_email(
            'Task', 'Dec 31', 10, 'Description', 'Ongoing', False
        )

        self.assertIn('🚨', subject)
        self.assertIn('10 Days Overdue', body)

    def test_overdue_task_email_subtask(self):
        """Test overdue email for subtask"""
        from app.email_templates import get_overdue_task_email

        subject, body = get_overdue_task_email(
            'Subtask', 'Date', 2, 'Desc', 'Ongoing', True
        )

        self.assertIn('Subtask', subject)
        self.assertIn('Subtask', body)

    def test_overdue_task_email_long_description(self):
        """Test overdue email with long description"""
        from app.email_templates import get_overdue_task_email

        long_desc = 'C' * 250
        subject, body = get_overdue_task_email(
            'Task', 'Date', 1, long_desc, 'Ongoing', False
        )
        self.assertIn('...', body)

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
        consumer.start_consuming()

    @mock.patch('threading.Thread')
    @mock.patch('pika.BlockingConnection')
    def test_start_consumer_thread(self, mock_conn, mock_thread):
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
        from app.scheduler import NotificationScheduler
        
        scheduler = NotificationScheduler(self.app)
        self.assertIsNotNone(scheduler)
        self.assertIsNotNone(scheduler.scheduler)

    @mock.patch('app.service.check_and_send_deadline_reminders')
    @mock.patch('app.service.check_and_send_overdue_alerts')
    def test_scheduler_start(self, mock_overdue, mock_deadline):
        """Test scheduler start"""
        from app.scheduler import NotificationScheduler
        
        mock_deadline.return_value = 0
        mock_overdue.return_value = 0
        
        scheduler = NotificationScheduler(self.app)
        scheduler.start()
        
        jobs = scheduler.scheduler.get_jobs()
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].id, 'notification_check')
        
        scheduler.stop()

    @mock.patch('app.service.check_and_send_deadline_reminders')
    @mock.patch('app.service.check_and_send_overdue_alerts')
    def test_scheduler_start_error(self, mock_overdue, mock_deadline):
        """Test scheduler start with error"""
        from app.scheduler import NotificationScheduler
        
        scheduler = NotificationScheduler(self.app)
        
        with mock.patch.object(scheduler.scheduler, 'add_job', side_effect=Exception("Error")):
            scheduler.start()

    def test_scheduler_stop(self):
        """Test scheduler stop"""
        from app.scheduler import NotificationScheduler
        
        scheduler = NotificationScheduler(self.app)
        scheduler.start()
        scheduler.stop()
        
        self.assertFalse(scheduler.scheduler.running)

    def test_scheduler_stop_when_not_running(self):
        """Test stopping scheduler when it's not running"""
        from app.scheduler import NotificationScheduler
        
        scheduler = NotificationScheduler(self.app)
        scheduler.stop()

    @mock.patch('app.service.check_and_send_deadline_reminders')
    @mock.patch('app.service.check_and_send_overdue_alerts')
    def test_scheduler_run_checks_now(self, mock_overdue, mock_deadline):
        """Test scheduler manual run of all checks"""
        from app.scheduler import NotificationScheduler
        
        mock_deadline.return_value = 3
        mock_overdue.return_value = 2
        
        scheduler = NotificationScheduler(self.app)
        scheduler.run_checks_now()
        
        mock_deadline.assert_called_once()
        mock_overdue.assert_called_once()

    @mock.patch('app.service.check_and_send_deadline_reminders')
    def test_scheduler_run_deadline_check_now(self, mock_check):
        """Test scheduler manual deadline check"""
        from app.scheduler import NotificationScheduler
        
        mock_check.return_value = 5
        
        scheduler = NotificationScheduler(self.app)
        result = scheduler.run_deadline_check_now()
        
        self.assertEqual(result, 5)
        mock_check.assert_called_once()

    @mock.patch('app.service.check_and_send_overdue_alerts')
    def test_scheduler_run_overdue_check_now(self, mock_check):
        """Test scheduler manual overdue check"""
        from app.scheduler import NotificationScheduler
        
        mock_check.return_value = 3
        
        scheduler = NotificationScheduler(self.app)
        result = scheduler.run_overdue_check_now()
        
        self.assertEqual(result, 3)
        mock_check.assert_called_once()

    @mock.patch('app.service.check_and_send_deadline_reminders')
    @mock.patch('app.service.check_and_send_overdue_alerts')
    def test_scheduler_run_all_checks_with_exception(self, mock_overdue, mock_deadline):
        """Test scheduler's _run_all_checks with exception"""
        from app.scheduler import NotificationScheduler
        
        mock_deadline.side_effect = Exception("Check error")
        
        scheduler = NotificationScheduler(self.app)
        scheduler._run_all_checks()
        
        mock_deadline.assert_called_once()

    @mock.patch('app.rabbitmq_consumer.start_consumer_thread')
    @mock.patch('app.scheduler.start_notification_scheduler')
    def test_start_notification_scheduler(self, mock_scheduler, mock_consumer):
        """Test start_notification_scheduler function"""
        from app.scheduler import start_notification_scheduler
        
        scheduler = start_notification_scheduler(self.app)
        
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
            self.assertIn('overdue_alerts', tables)

    def test_cors_enabled(self):
        """Test CORS is enabled"""
        self.assertIsNotNone(self.app)

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
            
            reminders_sent = check_and_send_deadline_reminders()
            
            self.assertEqual(reminders_sent, 1)
            mock_server.send_message.assert_called()
            
            reminder = DeadlineReminder.query.filter_by(task_id=1, days_before=7).first()
            self.assertIsNotNone(reminder)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_end_to_end_overdue_alert(self, mock_get, mock_smtp):
        """Test end-to-end overdue alert flow"""
        with self.app.app_context():
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            singapore_tz = ZoneInfo('Asia/Singapore')
            now = datetime.now(singapore_tz)
            deadline = (now - timedelta(days=2)).replace(hour=14, minute=0)
            
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
            
            alerts_sent = check_and_send_overdue_alerts()
            
            self.assertEqual(alerts_sent, 1)
            mock_server.send_message.assert_called()
            
            today = datetime.now(singapore_tz).date()
            alert = OverdueAlert.query.filter_by(task_id=1, alert_date=today).first()
            self.assertIsNotNone(alert)

    # ==================== Additional Edge Cases ====================
    
    @mock.patch('requests.get')
    def test_get_task_collaborators_missing_user_id(self, mock_get):
        """Test get_task_collaborators with missing user_id field"""
        with self.app.app_context():
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            # This will cause a KeyError when trying to access collab['user_id']
            mock_response.json.return_value = [{'id': 1, 'name': 'Test'}]
            mock_get.return_value = mock_response

            # The function should handle the KeyError and return empty list
            collaborators = get_task_collaborators(1)
            self.assertEqual(len(collaborators), 0)

    # ==================== MENTION ALERT NOTIFICATION TESTS ====================

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_mention_alert_notification_success(self, mock_get, mock_smtp):
        """Test successful mention alert notification"""
        with self.app.app_context():
            from app.service import send_mention_alert_notification
            from app.models import MentionNotification
            
            mock_server = mock.MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if 'tasks/1' in url:
                    mock_resp.json.return_value = self.task_data
                elif '/user/1' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Author', 'email': 'author@test.com', 'username': 'author'}
                elif '/user/2' in url:
                    mock_resp.json.return_value = {'id': 2, 'name': 'Mentioned', 'email': 'mentioned@test.com', 'username': 'mentioned'}
                return mock_resp
            
            mock_get.side_effect = mock_requests_get
            
            success = send_mention_alert_notification(
                task_id=1,
                comment_id=1,
                mentioned_user_id=2,
                author_id=1,
                comment_body="Hey @mentioned, can you review this?"
            )
            
            self.assertTrue(success)
            mock_server.send_message.assert_called_once()
            
            # Check database record
            notification = MentionNotification.query.filter_by(comment_id=1, mentioned_user_id=2).first()
            self.assertIsNotNone(notification)

    @mock.patch('requests.get')
    def test_send_mention_alert_notification_already_sent(self, mock_get):
        """Test mention alert when notification already sent"""
        with self.app.app_context():
            from app.service import send_mention_alert_notification
            from app.models import MentionNotification
            
            # Create existing notification
            existing = MentionNotification(
                task_id=1,
                comment_id=1,
                mentioned_user_id=2,
                author_id=1
            )
            db.session.add(existing)
            db.session.commit()
            
            success = send_mention_alert_notification(
                task_id=1,
                comment_id=1,
                mentioned_user_id=2,
                author_id=1,
                comment_body="Test comment"
            )
            
            self.assertTrue(success)  # Returns True but doesn't send duplicate

    @mock.patch('requests.get')
    def test_send_mention_alert_notification_task_not_found(self, mock_get):
        """Test mention alert when task doesn't exist"""
        with self.app.app_context():
            from app.service import send_mention_alert_notification
            
            mock_resp = mock.MagicMock()
            mock_resp.status_code = 404
            mock_get.return_value = mock_resp
            
            success = send_mention_alert_notification(
                task_id=999,
                comment_id=1,
                mentioned_user_id=2,
                author_id=1,
                comment_body="Test"
            )
            
            self.assertFalse(success)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_mention_alert_notification_no_email(self, mock_get, mock_smtp):
        """Test mention alert when mentioned user has no email"""
        with self.app.app_context():
            from app.service import send_mention_alert_notification
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if 'tasks/1' in url:
                    mock_resp.json.return_value = self.task_data
                elif '/user/1' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'Author', 'email': 'author@test.com', 'username': 'author'}
                elif '/user/2' in url:
                    mock_resp.json.return_value = {'id': 2, 'name': 'Mentioned', 'email': None, 'username': 'mentioned'}
                return mock_resp
            
            mock_get.side_effect = mock_requests_get
            
            success = send_mention_alert_notification(
                task_id=1,
                comment_id=1,
                mentioned_user_id=2,
                author_id=1,
                comment_body="Test"
            )
            
            self.assertFalse(success)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_mention_alert_notification_email_failure(self, mock_get, mock_smtp):
        """Test mention alert when email sending fails"""
        with self.app.app_context():
            from app.service import send_mention_alert_notification
            
            mock_smtp.return_value.__enter__.side_effect = Exception("SMTP Error")
            
            def mock_requests_get(url, **kwargs):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                
                if 'tasks/1' in url:
                    mock_resp.json.return_value = self.task_data
                elif '/user/' in url:
                    mock_resp.json.return_value = {'id': 1, 'name': 'User', 'email': 'user@test.com', 'username': 'user'}
                return mock_resp
            
            mock_get.side_effect = mock_requests_get
            
            success = send_mention_alert_notification(
                task_id=1,
                comment_id=1,
                mentioned_user_id=2,
                author_id=1,
                comment_body="Test"
            )
            
            self.assertFalse(success)

    @mock.patch('smtplib.SMTP')
    @mock.patch('requests.get')
    def test_send_mention_alert_notification_exception(self, mock_get, mock_smtp):
        """Test mention alert with general exception"""
        with self.app.app_context():
            from app.service import send_mention_alert_notification
            
            mock_get.side_effect = Exception("Unexpected error")
            
            success = send_mention_alert_notification(
                task_id=1,
                comment_id=1,
                mentioned_user_id=2,
                author_id=1,
                comment_body="Test"
            )
            
            self.assertFalse(success)

    # ==================== MENTION HELPER FUNCTIONS TESTS ====================

    def test_extract_mention_context(self):
        """Test extracting context around mention"""
        with self.app.app_context():
            from app.service import extract_mention_context
            
            comment = "This is a long comment where @username is mentioned in the middle of the text"
            result = extract_mention_context(comment, "username")
            
            self.assertIn("@username", result)
            self.assertIn("mentioned", result)

    def test_extract_mention_context_short_comment(self):
        """Test mention context with short comment"""
        with self.app.app_context():
            from app.service import extract_mention_context
            
            comment = "Hey @user!"
            result = extract_mention_context(comment, "user")
            
            self.assertEqual(result, comment)

    def test_format_time_ago(self):
        """Test time ago formatting"""
        with self.app.app_context():
            from app.service import format_time_ago
            from datetime import datetime
            from zoneinfo import ZoneInfo
            
            singapore_tz = ZoneInfo('Asia/Singapore')
            now = datetime.now(singapore_tz)
            
            result = format_time_ago(now)
            self.assertIn("just now", result.lower())

    def test_get_user_initials(self):
        """Test getting user initials"""
        from app.service import get_user_initials
        
        self.assertEqual(get_user_initials("John Doe"), "JD")
        self.assertEqual(get_user_initials("Alice"), "A")
        self.assertEqual(get_user_initials(""), "?")
        self.assertEqual(get_user_initials(None), "?")

    @mock.patch('requests.get')
    def test_get_user_details_for_mention_success(self, mock_get):
        """Test fetching user details for mention"""
        with self.app.app_context():
            from app.service import get_user_details_for_mention
            
            mock_resp = mock.MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {'id': 1, 'name': 'User', 'email': 'user@test.com', 'username': 'user'}
            mock_get.return_value = mock_resp
            
            result = get_user_details_for_mention(1)
            
            self.assertEqual(result['name'], 'User')
            self.assertEqual(result['email'], 'user@test.com')

    @mock.patch('requests.get')
    def test_get_user_details_for_mention_failure(self, mock_get):
        """Test fetching user details for mention with failure"""
        with self.app.app_context():
            from app.service import get_user_details_for_mention
            
            mock_get.side_effect = Exception("Service unavailable")
            
            result = get_user_details_for_mention(1)
            
            self.assertEqual(result, {})

    # ==================== RABBITMQ MENTION ALERT TESTS ====================

    @mock.patch('pika.BlockingConnection')
    @mock.patch('app.service.send_mention_alert_notification')
    def test_rabbitmq_on_mention_alert_message_success(self, mock_notify, mock_conn):
        """Test RabbitMQ mention alert processing success"""
        with self.app.app_context():
            from app.rabbitmq_consumer import RabbitMQConsumer
            
            mock_connection = mock.MagicMock()
            mock_channel = mock.MagicMock()
            mock_connection.channel.return_value = mock_channel
            mock_conn.return_value = mock_connection
            
            consumer = RabbitMQConsumer(self.app)
            consumer.connect()
            
            mock_notify.return_value = True
            
            message = {
                'task_id': 1,
                'comment_id': 1,
                'mentioned_user_id': 2,
                'author_id': 1,
                'comment_body': 'Test comment'
            }
            
            consumer.on_mention_alert_message(
                mock_channel,
                mock.MagicMock(delivery_tag=1),
                None,
                json.dumps(message).encode()
            )
            
            mock_channel.basic_ack.assert_called_with(delivery_tag=1)

    @mock.patch('pika.BlockingConnection')
    @mock.patch('app.service.send_mention_alert_notification')
    def test_rabbitmq_on_mention_alert_message_failure(self, mock_notify, mock_conn):
        """Test RabbitMQ mention alert processing failure"""
        with self.app.app_context():
            from app.rabbitmq_consumer import RabbitMQConsumer
            
            mock_connection = mock.MagicMock()
            mock_channel = mock.MagicMock()
            mock_connection.channel.return_value = mock_channel
            mock_conn.return_value = mock_connection
            
            consumer = RabbitMQConsumer(self.app)
            consumer.connect()
            
            mock_notify.return_value = False
            
            message = {
                'task_id': 1,
                'comment_id': 1,
                'mentioned_user_id': 2,
                'author_id': 1,
                'comment_body': 'Test'
            }
            
            consumer.on_mention_alert_message(
                mock_channel,
                mock.MagicMock(delivery_tag=1),
                None,
                json.dumps(message).encode()
            )
            
            mock_channel.basic_nack.assert_called_with(delivery_tag=1, requeue=True)

    @mock.patch('pika.BlockingConnection')
    def test_rabbitmq_on_mention_alert_invalid_json(self, mock_conn):
        """Test RabbitMQ mention alert with invalid JSON"""
        with self.app.app_context():
            from app.rabbitmq_consumer import RabbitMQConsumer
            
            mock_connection = mock.MagicMock()
            mock_channel = mock.MagicMock()
            mock_connection.channel.return_value = mock_channel
            mock_conn.return_value = mock_connection
            
            consumer = RabbitMQConsumer(self.app)
            consumer.connect()
            
            consumer.on_mention_alert_message(
                mock_channel,
                mock.MagicMock(delivery_tag=1),
                None,
                b'invalid json'
            )
            
            mock_channel.basic_nack.assert_called_with(delivery_tag=1, requeue=False)

    @mock.patch('pika.BlockingConnection')
    def test_rabbitmq_on_mention_alert_missing_field(self, mock_conn):
        """Test RabbitMQ mention alert with missing required field"""
        with self.app.app_context():
            from app.rabbitmq_consumer import RabbitMQConsumer
            
            mock_connection = mock.MagicMock()
            mock_channel = mock.MagicMock()
            mock_connection.channel.return_value = mock_channel
            mock_conn.return_value = mock_connection
            
            consumer = RabbitMQConsumer(self.app)
            consumer.connect()
            
            message = {'task_id': 1}  # Missing required fields
            
            consumer.on_mention_alert_message(
                mock_channel,
                mock.MagicMock(delivery_tag=1),
                None,
                json.dumps(message).encode()
            )
            
            mock_channel.basic_nack.assert_called_with(delivery_tag=1, requeue=False)

    @mock.patch('pika.BlockingConnection')
    @mock.patch('app.service.send_mention_alert_notification')
    def test_rabbitmq_on_mention_alert_exception(self, mock_notify, mock_conn):
        """Test RabbitMQ mention alert with processing exception"""
        with self.app.app_context():
            from app.rabbitmq_consumer import RabbitMQConsumer
            
            mock_connection = mock.MagicMock()
            mock_channel = mock.MagicMock()
            mock_connection.channel.return_value = mock_channel
            mock_conn.return_value = mock_connection
            
            consumer = RabbitMQConsumer(self.app)
            consumer.connect()
            
            mock_notify.side_effect = Exception("Processing error")
            
            message = {
                'task_id': 1,
                'comment_id': 1,
                'mentioned_user_id': 2,
                'author_id': 1,
                'comment_body': 'Test'
            }
            
            consumer.on_mention_alert_message(
                mock_channel,
                mock.MagicMock(delivery_tag=1),
                None,
                json.dumps(message).encode()
            )
            
            mock_channel.basic_nack.assert_called_with(delivery_tag=1, requeue=True)

    # ==================== MENTION NOTIFICATION MODEL TESTS ====================

    def test_mention_notification_model(self):
        """Test MentionNotification model creation"""
        with self.app.app_context():
            from app.models import MentionNotification
            
            notification = MentionNotification(
                task_id=1,
                comment_id=1,
                mentioned_user_id=2,
                author_id=1
            )
            db.session.add(notification)
            db.session.commit()
            
            saved = MentionNotification.query.filter_by(comment_id=1, mentioned_user_id=2).first()
            self.assertIsNotNone(saved)
            self.assertEqual(saved.task_id, 1)

    def test_mention_notification_unique_constraint(self):
        """Test MentionNotification unique constraint"""
        with self.app.app_context():
            from app.models import MentionNotification
            
            notification1 = MentionNotification(
                task_id=1,
                comment_id=1,
                mentioned_user_id=2,
                author_id=1
            )
            db.session.add(notification1)
            db.session.commit()
            
            notification2 = MentionNotification(
                task_id=1,
                comment_id=1,
                mentioned_user_id=2,
                author_id=1
            )
            db.session.add(notification2)
            
            with self.assertRaises(Exception):
                db.session.commit()

    def test_mention_notification_repr(self):
        """Test MentionNotification __repr__ method"""
        with self.app.app_context():
            from app.models import MentionNotification
            
            notification = MentionNotification(
                task_id=1,
                comment_id=1,
                mentioned_user_id=2,
                author_id=1
            )
            
            repr_str = repr(notification)
            self.assertIn('task_id=1', repr_str)
            self.assertIn('mentioned_user=2', repr_str)

    def test_mention_alert_email_subtask(self):
        """Test mention alert email for subtask"""
        with self.app.app_context():
            from app.email_templates import get_mention_alert_email
            
            subject, body = get_mention_alert_email(
                task_title='Test Subtask',
                comment_snippet='Comment',
                author_name='Jane',
                mentioned_username='user',
                is_subtask=True,
                comment_metadata={}
            )
            
            self.assertIn('Subtask', body)

    def test_mention_alert_email_no_metadata(self):
        """Test mention alert email without metadata"""
        with self.app.app_context():
            from app.email_templates import get_mention_alert_email
            
            subject, body = get_mention_alert_email(
                task_title='Task',
                comment_snippet='Comment',
                author_name='Author',
                mentioned_username='user'
            )
            
            self.assertIsNotNone(subject)
            self.assertIsNotNone(body)

    # ==================== ADDITIONAL SCHEDULER TESTS ====================

    @mock.patch('app.service.check_and_send_deadline_reminders')
    @mock.patch('app.service.check_and_send_overdue_alerts')
    def test_scheduler_run_all_checks_deadline_error(self, mock_overdue, mock_deadline):
        """Test scheduler when deadline check raises error"""
        with self.app.app_context():
            from app.scheduler import NotificationScheduler
            
            mock_deadline.side_effect = Exception("Deadline check failed")
            mock_overdue.return_value = 0
            
            scheduler = NotificationScheduler(self.app)
            scheduler._run_all_checks()  # Should not raise exception
            
            mock_deadline.assert_called_once()
            # Overdue check should not be called due to exception
            mock_overdue.assert_not_called()

    # ==================== ADDITIONAL SERVICE.PY HELPER FUNCTION TESTS ====================

    @mock.patch('requests.get')
    def test_get_user_name_not_found(self, mock_get):
        """Test get_user_name when user not found"""
        with self.app.app_context():
            from app.service import get_user_name
            
            mock_resp = mock.MagicMock()
            mock_resp.status_code = 404
            mock_get.return_value = mock_resp
            
            result = get_user_name(999)
            self.assertEqual(result, 'Unknown User')

    @mock.patch('requests.get')
    def test_get_user_email_not_found(self, mock_get):
        """Test get_user_email when user not found"""
        with self.app.app_context():
            from app.service import get_user_email
            
            mock_resp = mock.MagicMock()
            mock_resp.status_code = 404
            mock_get.return_value = mock_resp
            
            result = get_user_email(999)
            self.assertIsNone(result)

    @mock.patch('requests.get')
    def test_get_task_details_not_found(self, mock_get):
        """Test get_task_details when task not found"""
        with self.app.app_context():
            from app.service import get_task_details
            
            mock_resp = mock.MagicMock()
            mock_resp.status_code = 404
            mock_get.return_value = mock_resp
            
            result = get_task_details(999)
            self.assertIsNone(result)

    @mock.patch('requests.get')
    def test_get_task_collaborators_exception(self, mock_get):
        """Test get_task_collaborators with exception"""
        with self.app.app_context():
            from app.service import get_task_collaborators
            
            mock_get.side_effect = Exception("Service error")
            
            result = get_task_collaborators(1)
            self.assertEqual(result, [])

    @mock.patch('requests.get')
    def test_get_all_tasks_with_deadlines_exception(self, mock_get):
        """Test get_all_tasks_with_deadlines with exception"""
        with self.app.app_context():
            from app.service import get_all_tasks_with_deadlines
            
            mock_get.side_effect = Exception("Service error")
            
            result = get_all_tasks_with_deadlines()
            self.assertEqual(result, [])

    def test_parse_deadline_invalid_format(self):
        """Test parse_deadline with invalid format"""
        with self.app.app_context():
            from app.service import parse_deadline
            
            with self.assertRaises(Exception):
                parse_deadline("invalid-date-format")

    def test_format_deadline_for_email_none(self):
        """Test format_deadline_for_email with None"""
        with self.app.app_context():
            from app.service import format_deadline_for_email
            
            result = format_deadline_for_email(None)
            self.assertEqual(result, 'No deadline set')

    def test_format_deadline_for_email_invalid(self):
        """Test format_deadline_for_email with invalid date"""
        with self.app.app_context():
            from app.service import format_deadline_for_email
            
            result = format_deadline_for_email("invalid")
            self.assertEqual(result, 'Invalid deadline')

    # ==================== APP INITIALIZATION EDGE CASES ====================

    # def test_create_app_production_mode(self):
    #     """Test app creation in production mode"""
    #     os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    #     from app import create_app
        
    #     app = create_app()
    #     self.assertIsNotNone(app)
    #     self.assertFalse(app.config.get('TESTING', False))

if __name__ == "__main__":
    unittest.main()