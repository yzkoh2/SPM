# to run:
# docker-compose exec task_service pip install coverage
# docker-compose exec task_service coverage run -m unittest test.test
# docker-compose exec task_service coverage report

import unittest
from unittest.mock import patch, MagicMock, Mock, call, mock_open
import sys
import os
from datetime import datetime, timedelta
from io import BytesIO
import requests

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from app.routes import task_bp
from app.models import Task, TaskStatusEnum, Project, db, Attachment, Comment, task_collaborators, project_collaborators, comment_mentions
from app import service
import json


# ==================== BASE TEST CLASSES ====================

class TestTaskRoutesUnit(unittest.TestCase):
    """Base test class for unit tests with mocks"""
    
    def setUp(self):
        """Set up test client and mock data"""
        self.app = Flask(__name__)
        self.app.config['S3_BUCKET_NAME'] = 'test-bucket'
        self.app.s3_client = MagicMock()
        self.app.register_blueprint(task_bp, url_prefix='/api')
        self.client = self.app.test_client()
        self.app.testing = True

        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Mock task data
        self.mock_task1 = self._create_mock_task(
            id=1,
            title="Test Task 1",
            description="Description 1",
            owner_id=1,
            status=TaskStatusEnum.ONGOING,
            project_id=None,
            parent_task_id=None
        )
        
        self.mock_task2 = self._create_mock_task(
            id=2,
            title="Test Task 2",
            description="Description 2",
            owner_id=1,
            status=TaskStatusEnum.COMPLETED,
            project_id=None,
            parent_task_id=None
        )
        
        self.mock_task3 = self._create_mock_task(
            id=3,
            title="Project Task 1",
            description="Project Task Description",
            owner_id=2,
            status=TaskStatusEnum.ONGOING,
            project_id=1,
            parent_task_id=None
        )
        
        self.mock_subtask = self._create_mock_task(
            id=4,
            title="Subtask 1",
            description="Subtask Description",
            owner_id=1,
            status=TaskStatusEnum.UNASSIGNED,
            project_id=None,
            parent_task_id=1
        )

    def tearDown(self):
        self.app_context.pop()
    
    def _create_mock_task(self, id, title, description, owner_id, status, 
                         project_id=None, parent_task_id=None, deadline=None,
                         priority=None, is_recurring=False):
        """Helper method to create a mock task"""
        mock_task = MagicMock(spec=Task)
        mock_task.id = id
        mock_task.title = title
        mock_task.description = description
        mock_task.owner_id = owner_id
        mock_task.status = status
        mock_task.project_id = project_id
        mock_task.parent_task_id = parent_task_id
        mock_task.deadline = deadline
        mock_task.priority = priority
        mock_task.is_recurring = is_recurring
        mock_task.subtasks = []
        mock_task.comments = []
        mock_task.attachments = []
        mock_task.collaborator_ids.return_value = []
        
        mock_task.to_json.return_value = {
            'id': id,
            'title': title,
            'description': description,
            'owner_id': owner_id,
            'status': status.value,
            'project_id': project_id,
            'parent_task_id': parent_task_id,
            'deadline': deadline.isoformat() if deadline else None,
            'priority': priority,
            'is_recurring': is_recurring,
            'recurrence_interval': None,
            'recurrence_days': None,
            'recurrence_end_date': None,
            'collaborator_ids': [],
            'subtasks': [],
            'subtask_count': 0,
            'comments': [],
            'comment_count': 0,
            'attachments': [],
            'attachment_count': 0
        }
        
        return mock_task


class TestTaskRoutesIntegration(unittest.TestCase):
    """Base test class for integration tests with real database"""
    
    def setUp(self):
        """Set up test client and database"""
        from app import create_app
        # Adjust based on your actual create_app signature
        try:
            self.app = create_app(config_name="testing")
        except TypeError:
            # If create_app doesn't accept config_name, just call it
            self.app = create_app()
            self.app.config['TESTING'] = True
            self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test data
        self._create_test_data()
    
    def tearDown(self):
        """Clean up database"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def _create_test_data(self):
        """Create test projects and tasks"""
        # Create test project
        self.project = Project(
            id=1,
            title="Test Project",
            description="Test Description",
            owner_id=1
        )
        db.session.add(self.project)
        
        # Add project collaborator
        db.session.execute(
            project_collaborators.insert().values(
                project_id=1,
                user_id=1
            )
        )
        
        db.session.commit()


# ==================== UNIT TESTS - GET /tasks ====================

class TestGetAllTasksUnit(TestTaskRoutesUnit):
    """Unit test cases for GET /tasks route"""
    
    @patch('app.routes.service.get_all_tasks')
    def test_get_all_tasks_success(self, mock_get_all_tasks):
        """Test successfully retrieving all tasks for a user"""
        mock_get_all_tasks.return_value = [self.mock_task1, self.mock_task2]
        
        response = self.client.get('/api/tasks?owner_id=1')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['title'], 'Test Task 1')
        self.assertEqual(data[1]['title'], 'Test Task 2')
        mock_get_all_tasks.assert_called_once_with(1)
    
    @patch('app.routes.service.get_all_tasks')
    def test_get_all_tasks_no_owner_id(self, mock_get_all_tasks):
        """Test get all tasks without owner_id returns 400"""
        response = self.client.get('/api/tasks')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Owner ID is required')
    
    @patch('app.routes.service.get_all_tasks')
    def test_get_all_tasks_empty_list(self, mock_get_all_tasks):
        """Test get all tasks when user has no tasks"""
        mock_get_all_tasks.return_value = []
        
        response = self.client.get('/api/tasks?owner_id=1')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)
    
    @patch('app.routes.service.get_all_tasks')
    def test_get_all_tasks_service_exception(self, mock_get_all_tasks):
        """Test get all tasks when service raises exception"""
        mock_get_all_tasks.side_effect = Exception("Database error")
        
        response = self.client.get('/api/tasks?owner_id=1')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Database error')


# ==================== UNIT TESTS - GET /tasks/with-deadlines ====================

class TestGetTasksWithDeadlinesUnit(TestTaskRoutesUnit):
    """Unit test cases for GET /tasks/with-deadlines route"""
    
    @patch('app.models.Task')
    def test_get_tasks_with_deadlines_success(self, mock_task_model):
        """Test getting tasks with upcoming deadlines"""
        mock_query = MagicMock()
        mock_task_model.query = mock_query
        mock_query.filter.return_value.filter.return_value.all.return_value = [self.mock_task1]
        
        response = self.client.get('/api/tasks/with-deadlines')
        
        self.assertEqual(response.status_code, 200)
    
    @patch('app.models.Task')
    def test_get_tasks_with_deadlines_exception(self, mock_task_model):
        """Test exception handling in get tasks with deadlines"""
        mock_task_model.query.filter.side_effect = Exception("Database error")
        
        response = self.client.get('/api/tasks/with-deadlines')
        
        self.assertEqual(response.status_code, 500)


# ==================== UNIT TESTS - POST /tasks ====================

class TestCreateTaskUnit(TestTaskRoutesUnit):
    """Unit test cases for POST /tasks route"""
    
    @patch('app.routes.service.create_task')
    def test_create_task_success(self, mock_create_task):
        """Test successfully creating a task"""
        task_data = {
            'title': 'New Task',
            'description': 'Task description',
            'owner_id': 1,
            'status': 'Unassigned'
        }
        mock_create_task.return_value = {
            'id': 1,
            'title': 'New Task',
            'description': 'Task description',
            'owner_id': 1,
            'status': 'Unassigned'
        }
        
        response = self.client.post('/api/tasks', 
                                   data=json.dumps(task_data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'New Task')
    
    @patch('app.routes.service.create_task')
    def test_create_task_missing_title(self, mock_create_task):
        """Test create task without title"""
        task_data = {
            'description': 'Task description',
            'owner_id': 1
        }
        
        response = self.client.post('/api/tasks',
                                   data=json.dumps(task_data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Title', data['error'])
    
    @patch('app.routes.service.create_task')
    def test_create_task_missing_owner_id(self, mock_create_task):
        """Test create task without owner_id"""
        task_data = {
            'title': 'New Task',
            'description': 'Task description'
        }
        
        response = self.client.post('/api/tasks',
                                   data=json.dumps(task_data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Owner ID', data['error'])
    
    @patch('app.routes.service.create_task')
    def test_create_task_with_empty_title(self, mock_create_task):
        """Test create task with empty title"""
        task_data = {
            'title': '',
            'owner_id': 1
        }
        
        response = self.client.post('/api/tasks',
                                   data=json.dumps(task_data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)


# ==================== UNIT TESTS - GET /tasks/<int:task_id> ====================

class TestGetTaskByIdUnit(TestTaskRoutesUnit):
    """Unit test cases for GET /tasks/<int:task_id> route"""
    
    @patch('app.routes.service.get_task_details')
    def test_get_task_success(self, mock_get_task_details):
        """Test successfully retrieving a task by ID"""
        mock_get_task_details.return_value = self.mock_task1.to_json()
        
        response = self.client.get('/api/tasks/1')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['title'], 'Test Task 1')
        mock_get_task_details.assert_called_once_with(1)
    
    @patch('app.routes.service.get_task_details')
    def test_get_task_not_found(self, mock_get_task_details):
        """Test get task when task doesn't exist"""
        mock_get_task_details.return_value = None
        
        response = self.client.get('/api/tasks/999')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Task not found')
    
    @patch('app.routes.service.get_task_details')
    def test_get_task_service_exception(self, mock_get_task_details):
        """Test get task when service raises exception"""
        mock_get_task_details.side_effect = Exception("Database error")
        
        response = self.client.get('/api/tasks/1')
        
        self.assertEqual(response.status_code, 500)


# ==================== UNIT TESTS - PUT /tasks/<int:task_id> ====================

class TestUpdateTaskUnit(TestTaskRoutesUnit):
    """Unit test cases for PUT /tasks/<int:task_id> route"""
    
    @patch('app.routes.service.update_task')
    def test_update_task_success(self, mock_update_task):
        """Test successfully updating a task"""
        update_data = {
            'title': 'Updated Title',
            'user_id': 1
        }
        mock_update_task.return_value = (
            {'id': 1, 'title': 'Updated Title'},
            "Task updated successfully"
        )
        
        response = self.client.put('/api/tasks/1',
                                  data=json.dumps(update_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Updated Title')
    
    @patch('app.routes.service.update_task')
    def test_update_task_not_found(self, mock_update_task):
        """Test update task when task doesn't exist"""
        update_data = {'title': 'Updated Title', 'user_id': 1}
        mock_update_task.return_value = (None, "Task not found")
        
        response = self.client.put('/api/tasks/999',
                                  data=json.dumps(update_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    @patch('app.routes.service.update_task')
    def test_update_task_forbidden(self, mock_update_task):
        """Test update task when user doesn't have permission"""
        update_data = {'title': 'Updated Title', 'user_id': 2}
        mock_update_task.return_value = (None, "Forbidden: You do not have permission")
        
        response = self.client.put('/api/tasks/1',
                                  data=json.dumps(update_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertIn('Forbidden', data['error'])
    
    @patch('app.routes.service.update_task')
    def test_update_task_invalid_status(self, mock_update_task):
        """Test update task with invalid status"""
        update_data = {'status': 'InvalidStatus', 'user_id': 1}
        mock_update_task.return_value = (None, "Invalid status value")
        
        response = self.client.put('/api/tasks/1',
                                  data=json.dumps(update_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)


# ==================== UNIT TESTS - DELETE /tasks/<int:task_id> ====================

class TestDeleteTaskUnit(TestTaskRoutesUnit):
    """Unit test cases for DELETE /tasks/<int:task_id> route"""
    
    @patch('app.routes.service.delete_task')
    def test_delete_task_success(self, mock_delete_task):
        """Test successfully deleting a task"""
        mock_delete_task.return_value = (True, "Task deleted successfully")
        
        response = self.client.delete('/api/tasks/1',
                                     data=json.dumps({'user_id': 1}),
                                     content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
    
    @patch('app.routes.service.delete_task')
    def test_delete_task_not_found(self, mock_delete_task):
        """Test delete task when task doesn't exist"""
        mock_delete_task.return_value = (False, "Task not found")
        
        response = self.client.delete('/api/tasks/999',
                                     data=json.dumps({'user_id': 1}),
                                     content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    @patch('app.routes.service.delete_task')
    def test_delete_task_with_subtasks(self, mock_delete_task):
        """Test delete task that has incomplete subtasks"""
        mock_delete_task.return_value = (False, "Cannot delete task. All subtasks must be completed first.")
        
        response = self.client.delete('/api/tasks/1',
                                     data=json.dumps({'user_id': 1}),
                                     content_type='application/json')
        
        self.assertEqual(response.status_code, 404)


# ==================== UNIT TESTS - COMMENTS ====================

class TestCommentsUnit(TestTaskRoutesUnit):
    """Unit tests for comment operations"""
    
    @patch('app.routes.service.add_comment')
    def test_add_comment_success(self, mock_add_comment):
        """Test adding a comment to a task"""
        comment_data = {
            'body': 'Test comment',
            'author_id': 1
        }
        mock_add_comment.return_value = ({'id': 1, 'body': 'Test comment'}, "Comment added successfully")
        
        response = self.client.post('/api/tasks/1/comments',
                                   data=json.dumps(comment_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 201)
    
    @patch('app.routes.service.add_comment')
    def test_add_comment_missing_body(self, mock_add_comment):
        """Test adding a comment without body"""
        comment_data = {
            'author_id': 1
        }
        
        response = self.client.post('/api/tasks/1/comments',
                                   data=json.dumps(comment_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    @patch('app.routes.service.add_comment')
    def test_add_comment_missing_author(self, mock_add_comment):
        """Test adding a comment without author_id"""
        comment_data = {
            'body': 'Test comment'
        }
        
        response = self.client.post('/api/tasks/1/comments',
                                   data=json.dumps(comment_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    @patch('app.routes.service.add_comment')
    def test_add_comment_task_not_found(self, mock_add_comment):
        """Test adding a comment to non-existent task"""
        comment_data = {
            'body': 'Test comment',
            'author_id': 1
        }
        mock_add_comment.return_value = None
        
        response = self.client.post('/api/tasks/999/comments',
                                   data=json.dumps(comment_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)
    
    @patch('app.routes.service.add_comment')
    def test_add_comment_with_mentions(self, mock_add_comment):
        """Test adding a comment with mentions"""
        comment_data = {
            'body': 'Test comment @user',
            'author_id': 1,
            'mention_ids': [2, 3]
        }
        mock_add_comment.return_value = ({'id': 1, 'body': 'Test comment @user'}, "Comment added successfully")
        
        response = self.client.post('/api/tasks/1/comments',
                                   data=json.dumps(comment_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 201)
    
    @patch('app.routes.service.delete_comment')
    def test_delete_comment_success(self, mock_delete_comment):
        """Test deleting a comment"""
        mock_delete_comment.return_value = True
        
        response = self.client.delete('/api/tasks/deletecomment/1')
        self.assertEqual(response.status_code, 200)
    
    @patch('app.routes.service.delete_comment')
    def test_delete_comment_not_found(self, mock_delete_comment):
        """Test deleting a non-existent comment"""
        mock_delete_comment.return_value = False
        
        response = self.client.delete('/api/tasks/deletecomment/999')
        self.assertEqual(response.status_code, 404)
    
    @patch('app.routes.service.delete_comment')
    def test_delete_comment_exception(self, mock_delete_comment):
        """Test delete comment with exception"""
        mock_delete_comment.side_effect = Exception("Database error")
        
        response = self.client.delete('/api/tasks/deletecomment/1')
        self.assertEqual(response.status_code, 500)


# ==================== UNIT TESTS - COLLABORATORS ====================

class TestCollaboratorsUnit(TestTaskRoutesUnit):
    """Unit tests for collaborator operations"""
    
    @patch('app.routes.service.get_task_collaborators')
    def test_get_task_collaborators_success(self, mock_get_collaborators):
        """Test getting task collaborators"""
        mock_collaborators = [
            {'user_id': 2},
            {'user_id': 3}
        ]
        mock_get_collaborators.return_value = mock_collaborators
        
        response = self.client.get('/api/tasks/1/collaborators')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
    
    @patch('app.routes.service.get_task_collaborators')
    def test_get_task_collaborators_empty(self, mock_get_collaborators):
        """Test getting collaborators for task with none"""
        mock_get_collaborators.return_value = []
        
        response = self.client.get('/api/tasks/1/collaborators')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)
    
    @patch('app.routes.service.get_task_collaborators')
    def test_get_task_collaborators_exception(self, mock_get_collaborators):
        """Test get collaborators with exception"""
        mock_get_collaborators.side_effect = Exception("Database error")
        
        response = self.client.get('/api/tasks/1/collaborators')
        self.assertEqual(response.status_code, 500)
    
    @patch('app.routes.service.add_task_collaborators')
    def test_add_collaborator_success(self, mock_add_collaborators):
        """Test adding collaborators to a task"""
        data = {
            'collaborator_ids': [2, 3],
            'requested_by': 1
        }
        mock_add_collaborators.return_value = {'message': 'Success'}
        
        response = self.client.post('/api/tasks/1/collaborators',
                                   data=json.dumps(data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 201)
    
    @patch('app.routes.service.add_task_collaborators')
    def test_add_collaborator_missing_ids(self, mock_add_collaborators):
        """Test adding collaborators without IDs"""
        data = {
            'requested_by': 1
        }
        
        response = self.client.post('/api/tasks/1/collaborators',
                                   data=json.dumps(data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    @patch('app.routes.service.add_task_collaborators')
    def test_add_collaborator_missing_requester(self, mock_add_collaborators):
        """Test adding collaborators without requester"""
        data = {
            'collaborator_ids': [2, 3]
        }
        
        response = self.client.post('/api/tasks/1/collaborators',
                                   data=json.dumps(data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    @patch('app.routes.service.add_task_collaborators')
    def test_add_collaborator_exception(self, mock_add_collaborators):
        """Test add collaborator with exception"""
        data = {
            'collaborator_ids': [2, 3],
            'requested_by': 1
        }
        mock_add_collaborators.side_effect = Exception("Permission denied")
        
        response = self.client.post('/api/tasks/1/collaborators',
                                   data=json.dumps(data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 500)
    
    @patch('app.routes.service.remove_task_collaborator')
    def test_remove_collaborator_success(self, mock_remove_collaborator):
        """Test removing a collaborator from a task"""
        data = {
            'collaborator_id': [2],
            'requested_by': 1
        }
        mock_remove_collaborator.return_value = {'message': 'Success'}
        
        response = self.client.delete('/api/tasks/1/collaborators',
                                     data=json.dumps(data),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 200)
    
    @patch('app.routes.service.remove_task_collaborator')
    def test_remove_collaborator_missing_id(self, mock_remove_collaborator):
        """Test removing collaborator without ID"""
        data = {
            'requested_by': 1
        }
        
        response = self.client.delete('/api/tasks/1/collaborators',
                                     data=json.dumps(data),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)


# ==================== UNIT TESTS - ATTACHMENTS ====================

class TestAttachmentsUnit(TestTaskRoutesUnit):
    """Unit tests for attachment operations"""
    
    @patch('app.routes.service.add_attachment')
    def test_add_attachment_success(self, mock_add_attachment):
        """Test adding an attachment to a task"""
        mock_add_attachment.return_value = {
            'id': 1,
            'filename': 'test.pdf',
            'url': 'https://s3.amazonaws.com/test.pdf'
        }
        
        data = {'filename': 'test.pdf'}
        data['file'] = (BytesIO(b"file content"), 'test.pdf')
        
        response = self.client.post('/api/tasks/1/attachments',
                                   data=data,
                                   content_type='multipart/form-data')
        self.assertEqual(response.status_code, 201)
    
    @patch('app.routes.service.add_attachment')
    def test_add_attachment_no_file(self, mock_add_attachment):
        """Test adding attachment without file"""
        response = self.client.post('/api/tasks/1/attachments',
                                   data={},
                                   content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
    
    @patch('app.routes.service.add_attachment')
    def test_add_attachment_empty_filename(self, mock_add_attachment):
        """Test adding attachment with empty filename"""
        data = {}
        data['file'] = (BytesIO(b"file content"), '')
        
        response = self.client.post('/api/tasks/1/attachments',
                                   data=data,
                                   content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
    
    @patch('app.routes.service.add_attachment')
    def test_add_attachment_task_not_found(self, mock_add_attachment):
        """Test adding attachment to non-existent task"""
        mock_add_attachment.return_value = None
        
        data = {'filename': 'test.pdf'}
        data['file'] = (BytesIO(b"file content"), 'test.pdf')
        
        response = self.client.post('/api/tasks/999/attachments',
                                   data=data,
                                   content_type='multipart/form-data')
        self.assertEqual(response.status_code, 404)
    
    @patch('app.routes.service.add_attachment')
    def test_add_attachment_exception(self, mock_add_attachment):
        """Test add attachment with exception"""
        mock_add_attachment.side_effect = Exception("S3 error")
        
        data = {'filename': 'test.pdf'}
        data['file'] = (BytesIO(b"file content"), 'test.pdf')
        
        response = self.client.post('/api/tasks/1/attachments',
                                   data=data,
                                   content_type='multipart/form-data')
        self.assertEqual(response.status_code, 500)
    
    @patch('app.routes.service.get_attachment_url')
    def test_get_attachment_success(self, mock_get_attachment):
        """Test getting an attachment"""
        mock_get_attachment.return_value = (
            {
                'id': 1,
                'filename': 'test.pdf',
                'url': 'https://presigned-url.com'
            },
            "Success"
        )
        
        response = self.client.get('/api/tasks/1/attachments/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('url', data)
    
    @patch('app.routes.service.get_attachment_url')
    def test_get_attachment_not_found(self, mock_get_attachment):
        """Test getting non-existent attachment"""
        mock_get_attachment.return_value = (None, "Attachment not found")
        
        response = self.client.get('/api/tasks/1/attachments/999')
        self.assertEqual(response.status_code, 404)
    
    @patch('app.routes.service.get_attachment_url')
    def test_get_attachment_exception(self, mock_get_attachment):
        """Test get attachment with exception"""
        mock_get_attachment.side_effect = Exception("S3 error")
        
        response = self.client.get('/api/tasks/1/attachments/1')
        self.assertEqual(response.status_code, 500)
    
    @patch('app.routes.service.delete_attachment_url')
    def test_delete_attachment_success(self, mock_delete_attachment):
        """Test deleting an attachment"""
        mock_delete_attachment.return_value = (True, "Attachment deleted successfully")
        
        response = self.client.delete('/api/tasks/1/attachments/1')
        self.assertEqual(response.status_code, 200)
    
    @patch('app.routes.service.delete_attachment_url')
    def test_delete_attachment_not_found(self, mock_delete_attachment):
        """Test deleting non-existent attachment"""
        mock_delete_attachment.return_value = (False, "Attachment not found")
        
        response = self.client.delete('/api/tasks/1/attachments/999')
        self.assertEqual(response.status_code, 404)
    
    @patch('app.routes.service.delete_attachment_url')
    def test_delete_attachment_exception(self, mock_delete_attachment):
        """Test delete attachment with exception"""
        mock_delete_attachment.side_effect = Exception("S3 error")
        
        response = self.client.delete('/api/tasks/1/attachments/1')
        self.assertEqual(response.status_code, 500)


# ==================== UNIT TESTS - PROJECTS ====================

class TestProjectRoutesUnit(TestTaskRoutesUnit):
    """Unit tests for project routes"""
    
    @patch('app.routes.service.create_project')
    def test_create_project_success(self, mock_create_project):
        """Test creating a project"""
        project_data = {
            'title': 'New Project',
            'description': 'Project description',
            'owner_id': 1
        }
        mock_create_project.return_value = {
            'id': 1,
            'title': 'New Project',
            'owner_id': 1
        }
        
        response = self.client.post('/api/projects',
                                   data=json.dumps(project_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 201)
    
    @patch('app.routes.service.create_project')
    def test_create_project_missing_title(self, mock_create_project):
        """Test creating project without title"""
        project_data = {
            'description': 'Project description',
            'owner_id': 1
        }
        
        response = self.client.post('/api/projects',
                                   data=json.dumps(project_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    @patch('app.routes.service.create_project')
    def test_create_project_missing_owner(self, mock_create_project):
        """Test creating project without owner_id"""
        project_data = {
            'title': 'New Project',
            'description': 'Project description'
        }
        
        response = self.client.post('/api/projects',
                                   data=json.dumps(project_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    @patch('app.routes.service.get_project_by_id')
    def test_get_project_success(self, mock_get_project):
        """Test getting a project"""
        # Create a proper dict response instead of mock object
        mock_project_dict = {
            'id': 1,
            'title': 'Test Project',
            'description': 'Test Description',
            'owner_id': 1,
            'collaborator_ids': [1, 2],
            'tasks': []
        }
        # Return a mock that has to_json method
        mock_project_obj = MagicMock()
        mock_project_obj.to_json.return_value = mock_project_dict
        mock_get_project.return_value = (mock_project_obj, None)
        
        response = self.client.get('/api/projects/1?user_id=1')
        self.assertEqual(response.status_code, 200)
    
    @patch('app.routes.service.get_project_by_id')
    def test_get_project_no_user_id(self, mock_get_project):
        """Test getting project without user_id"""
        response = self.client.get('/api/projects/1')
        self.assertEqual(response.status_code, 400)
    
    @patch('app.routes.service.get_project_by_id')
    def test_get_project_not_found(self, mock_get_project):
        """Test getting non-existent project"""
        mock_get_project.return_value = (None, "Project not found")
        
        response = self.client.get('/api/projects/999?user_id=1')
        self.assertEqual(response.status_code, 404)
    
    @patch('app.routes.service.get_project_by_id')
    def test_get_project_forbidden(self, mock_get_project):
        """Test getting project without access"""
        mock_get_project.return_value = (None, "Forbidden: You don't have access")
        
        response = self.client.get('/api/projects/1?user_id=999')
        self.assertEqual(response.status_code, 403)
    
    @patch('app.routes.service.get_project_dashboard')
    def test_get_project_dashboard_success(self, mock_get_dashboard):
        """Test getting project dashboard"""
        mock_get_dashboard.return_value = (
            {
                'project': {'id': 1, 'title': 'Test Project'},
                'tasks': [],
                'collaborators': [1, 2],
                'task_count': 0
            },
            None
        )
        
        response = self.client.get('/api/projects/1/dashboard?user_id=1')
        self.assertEqual(response.status_code, 200)
    
    @patch('app.routes.service.get_project_dashboard')
    def test_get_project_dashboard_with_filters(self, mock_get_dashboard):
        """Test getting project dashboard with filters"""
        mock_get_dashboard.return_value = (
            {
                'project': {'id': 1, 'title': 'Test Project'},
                'tasks': [],
                'collaborators': [1, 2],
                'task_count': 0
            },
            None
        )
        
        response = self.client.get('/api/projects/1/dashboard?user_id=1&status=Ongoing&sort_by=deadline&owner=me')
        self.assertEqual(response.status_code, 200)
    
    @patch('app.routes.service.get_user_projects')
    def test_get_user_projects_success(self, mock_get_user_projects):
        """Test getting user projects"""
        mock_get_user_projects.return_value = [
            {'id': 1, 'title': 'Project 1', 'user_role': 'owner'}
        ]
        
        response = self.client.get('/api/projects/user/1')
        self.assertEqual(response.status_code, 200)
    
    @patch('app.routes.service.get_user_projects')
    def test_get_user_projects_with_role_filter(self, mock_get_user_projects):
        """Test getting user projects with role filter"""
        mock_get_user_projects.return_value = [
            {'id': 1, 'title': 'Project 1', 'user_role': 'owner'}
        ]
        
        response = self.client.get('/api/projects/user/1?role=owner')
        self.assertEqual(response.status_code, 200)
    
    @patch('app.routes.service.update_project')
    def test_update_project_success(self, mock_update_project):
        """Test updating a project"""
        update_data = {
            'title': 'Updated Project',
            'user_id': 1
        }
        mock_update_project.return_value = (
            {'id': 1, 'title': 'Updated Project'},
            "Project updated successfully"
        )
        
        response = self.client.put('/api/projects/1',
                                  data=json.dumps(update_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
    
    @patch('app.routes.service.update_project')
    def test_update_project_missing_user_id(self, mock_update_project):
        """Test updating project without user_id"""
        update_data = {
            'title': 'Updated Project'
        }
        
        response = self.client.put('/api/projects/1',
                                  data=json.dumps(update_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    @patch('app.routes.service.update_project')
    def test_update_project_not_found(self, mock_update_project):
        """Test updating non-existent project"""
        update_data = {
            'title': 'Updated Project',
            'user_id': 1
        }
        mock_update_project.return_value = (None, "Project not found")
        
        response = self.client.put('/api/projects/999',
                                  data=json.dumps(update_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 404)
    
    @patch('app.routes.service.update_project')
    def test_update_project_forbidden(self, mock_update_project):
        """Test updating project without permission"""
        update_data = {
            'title': 'Updated Project',
            'user_id': 2
        }
        mock_update_project.return_value = (None, "Forbidden: Only the project owner can update")
        
        response = self.client.put('/api/projects/1',
                                  data=json.dumps(update_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 403)
    
    @patch('app.routes.service.delete_project')
    def test_delete_project_success(self, mock_delete_project):
        """Test deleting a project"""
        mock_delete_project.return_value = (True, None)
        
        response = self.client.delete('/api/projects/1',
                                     data=json.dumps({'user_id': 1}),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 200)
    
    @patch('app.routes.service.delete_project')
    def test_delete_project_missing_user_id(self, mock_delete_project):
        """Test deleting project without user_id"""
        response = self.client.delete('/api/projects/1',
                                     data=json.dumps({}),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    @patch('app.routes.service.delete_project')
    def test_delete_project_not_found(self, mock_delete_project):
        """Test deleting non-existent project"""
        mock_delete_project.return_value = (False, "Project not found")
        
        response = self.client.delete('/api/projects/999',
                                     data=json.dumps({'user_id': 1}),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 404)
    
    @patch('app.routes.service.add_project_collaborator')
    def test_add_project_collaborator_success(self, mock_add_collaborator):
        """Test adding collaborator to project"""
        data = {
            'user_id': 1,
            'collaborator_user_id': 2
        }
        mock_add_collaborator.return_value = ({'message': 'Success'}, None)
        
        response = self.client.post('/api/projects/1/collaborators',
                                   data=json.dumps(data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 201)
    
    @patch('app.routes.service.add_project_collaborator')
    def test_add_project_collaborator_missing_user_id(self, mock_add_collaborator):
        """Test adding collaborator without user_id"""
        data = {
            'collaborator_user_id': 2
        }
        
        response = self.client.post('/api/projects/1/collaborators',
                                   data=json.dumps(data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    @patch('app.routes.service.add_project_collaborator')
    def test_add_project_collaborator_already_exists(self, mock_add_collaborator):
        """Test adding collaborator that already exists"""
        data = {
            'user_id': 1,
            'collaborator_user_id': 2
        }
        mock_add_collaborator.return_value = (None, "User is already a collaborator")
        
        response = self.client.post('/api/projects/1/collaborators',
                                   data=json.dumps(data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 409)
    
    @patch('app.routes.service.remove_project_collaborator')
    def test_remove_project_collaborator_success(self, mock_remove_collaborator):
        """Test removing collaborator from project"""
        data = {
            'user_id': 1
        }
        mock_remove_collaborator.return_value = ({'message': 'Success'}, None)
        
        response = self.client.delete('/api/projects/1/collaborators/2',
                                     data=json.dumps(data),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 200)
    
    @patch('app.routes.service.get_project_tasks')
    def test_get_project_tasks_success(self, mock_get_tasks):
        """Test getting project tasks"""
        mock_get_tasks.return_value = ([self.mock_task3], None)
        
        response = self.client.get('/api/projects/1/tasks')
        self.assertEqual(response.status_code, 200)
    
    @patch('app.routes.service.get_project_tasks')
    def test_get_project_tasks_not_found(self, mock_get_tasks):
        """Test getting tasks for non-existent project"""
        mock_get_tasks.return_value = (None, "Project not found")
        
        response = self.client.get('/api/projects/999/tasks')
        self.assertEqual(response.status_code, 404)
    
    @patch('app.routes.service.create_task_in_project')
    def test_create_task_in_project_success(self, mock_create_task):
        """Test creating task in project"""
        task_data = {
            'title': 'Project Task',
            'user_id': 1
        }
        mock_create_task.return_value = ({'id': 1, 'title': 'Project Task'}, None)
        
        response = self.client.post('/api/projects/1/tasks',
                                   data=json.dumps(task_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 201)
    
    @patch('app.routes.service.create_task_in_project')
    def test_create_task_in_project_missing_user_id(self, mock_create_task):
        """Test creating task in project without user_id"""
        task_data = {
            'title': 'Project Task'
        }
        
        response = self.client.post('/api/projects/1/tasks',
                                   data=json.dumps(task_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    @patch('app.routes.service.create_task_in_project')
    def test_create_task_in_project_missing_title(self, mock_create_task):
        """Test creating task in project without title"""
        task_data = {
            'user_id': 1
        }
        
        response = self.client.post('/api/projects/1/tasks',
                                   data=json.dumps(task_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    @patch('app.routes.service.add_existing_task_to_project')
    def test_add_existing_task_to_project_success(self, mock_add_task):
        """Test adding existing task to project"""
        data = {
            'project_id': 1,
            'user_id': 1
        }
        mock_add_task.return_value = ({'id': 1, 'project_id': 1}, None)
        
        response = self.client.post('/api/tasks/1/add-to-project',
                                   data=json.dumps(data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
    
    @patch('app.routes.service.add_existing_task_to_project')
    def test_add_existing_task_missing_project_id(self, mock_add_task):
        """Test adding task to project without project_id"""
        data = {
            'user_id': 1
        }
        
        response = self.client.post('/api/tasks/1/add-to-project',
                                   data=json.dumps(data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    @patch('app.routes.service.add_existing_task_to_project')
    def test_add_existing_task_already_assigned(self, mock_add_task):
        """Test adding task that's already in a project"""
        data = {
            'project_id': 1,
            'user_id': 1
        }
        mock_add_task.return_value = (None, "Task is already assigned to a project")
        
        response = self.client.post('/api/tasks/1/add-to-project',
                                   data=json.dumps(data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 409)
    
    @patch('app.routes.service.remove_task_from_project')
    def test_remove_task_from_project_success(self, mock_remove_task):
        """Test removing task from project"""
        data = {
            'user_id': 1
        }
        mock_remove_task.return_value = ({'id': 1, 'project_id': None}, None)
        
        response = self.client.post('/api/tasks/1/remove-from-project',
                                   data=json.dumps(data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
    
    @patch('app.routes.service.remove_task_from_project')
    def test_remove_task_not_in_project(self, mock_remove_task):
        """Test removing task that's not in a project"""
        data = {
            'user_id': 1
        }
        mock_remove_task.return_value = (None, "Task is not assigned to any project")
        
        response = self.client.post('/api/tasks/1/remove-from-project',
                                   data=json.dumps(data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    @patch('app.routes.service.get_standalone_tasks_for_user')
    def test_get_standalone_tasks_success(self, mock_get_tasks):
        """Test getting standalone tasks"""
        mock_get_tasks.return_value = [
            {'id': 1, 'title': 'Task 1', 'project_id': None}
        ]
        
        response = self.client.get('/api/tasks/standalone?user_id=1')
        self.assertEqual(response.status_code, 200)
    
    @patch('app.routes.service.get_standalone_tasks_for_user')
    def test_get_standalone_tasks_missing_user_id(self, mock_get_tasks):
        """Test getting standalone tasks without user_id"""
        response = self.client.get('/api/tasks/standalone')
        self.assertEqual(response.status_code, 400)


# ==================== UNIT TESTS - HEALTH CHECK ====================

class TestHealthCheckUnit(TestTaskRoutesUnit):
    """Unit tests for health check endpoint"""
    
    def test_health_check(self, ):
        """Test health check endpoint"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'task_management')



# ==================== RUN TESTS ====================

# ==================== UNIT TESTS - APP/INIT ====================

class TestAppFactory(unittest.TestCase):

    @patch('app.boto3.client')
    def test_create_app_production(self, mock_boto3_client):
        """Test creating app in production mode"""
        from app import create_app
        from config import Config

        with patch.object(Config, 'SQLALCHEMY_DATABASE_URI', 'sqlite:///:memory:'), \
             patch.object(Config, 'S3_REGION', 'us-east-1'), \
             patch.object(Config, 'S3_ACCESS_KEY', 'test'), \
             patch.object(Config, 'S3_SECRET_KEY', 'test'), \
             patch('app.db.create_all') as mock_create_all:

            app = create_app(config_name="production")

            self.assertFalse(app.config['TESTING'])
            self.assertIsNotNone(app.s3_client)
            mock_create_all.assert_called_once()

    def test_create_app_testing(self):
        """Test creating app in testing mode"""
        from app import create_app
        app = create_app(config_name="testing")

        self.assertTrue(app.config['TESTING'])
        self.assertIsNone(app.s3_client)
        self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'], 'sqlite:///:memory:')


# ==================== UNIT TESTS - RABBITMQ PUBLISHER ====================

# ==================== UNIT TESTS - SERVICE FUNCTIONS ====================

class TestServiceFunctions(TestTaskRoutesIntegration):

    def test_create_task_with_deadline(self):
        """Test creating a task with a deadline"""
        from app.service import create_task
        task_data = {
            'title': 'Service Task',
            'description': 'Service Task Description',
            'owner_id': 1,
            'deadline': '2025-12-31T10:00:00'
        }
        create_task(task_data)
        task = Task.query.filter_by(title='Service Task').first()
        self.assertIsNotNone(task)
        self.assertEqual(task.deadline, datetime.fromisoformat('2025-12-31T10:00:00'))

    def test_update_task_status(self):
        """Test updating a task's status"""
        from app.service import update_task
        task = Task(title="Update Task", owner_id=1, status=TaskStatusEnum.ONGOING)
        db.session.add(task)
        db.session.commit()

        update_data = {'status': 'Completed'}
        updated_task, message = update_task(task.id, 1, update_data)
        self.assertEqual(updated_task['status'], 'Completed')

    def test_delete_task_with_incomplete_subtasks(self):
        """Test deleting a task with incomplete subtasks"""
        from app.service import delete_task
        parent_task = Task(title="Parent", owner_id=1)
        db.session.add(parent_task)
        db.session.commit()
        subtask = Task(title="Subtask", owner_id=1, parent_task_id=parent_task.id, status=TaskStatusEnum.ONGOING)
        db.session.add(subtask)
        db.session.commit()

        success, message = delete_task(parent_task.id, 1)
        self.assertFalse(success)
        self.assertEqual(message, "Cannot delete task. All subtasks must be completed first.")

    def test_add_comment_with_mentions(self):
        """Test adding a comment with mentions"""
        from app.service import add_comment
        task = Task(title="Mention Task", owner_id=1)
        db.session.add(task)
        db.session.commit()

        comment_data = {
            'body': 'Hello @user2',
            'author_id': 1,
            'mention_ids': [2]
        }
        with patch('app.rabbitmq_publisher.publish_mention_alert') as mock_publish:
            add_comment(task.id, comment_data)
            mock_publish.assert_called_once()

    def test_create_project_with_collaborators(self):
        """Test creating a project with collaborators"""
        from app.service import create_project
        project_data = {
            'title': 'New Project with Collaborators',
            'owner_id': 1,
            'collaborator_ids': [2, 3]
        }
        project = create_project(project_data)
        self.assertIsNotNone(project)
        p = Project.query.get(project['id'])
        self.assertEqual(len(p.collaborator_ids()), 3) # Owner + 2 collaborators

    def test_get_project_dashboard_with_filters(self):
        """Test getting a project dashboard with filters"""
        from app.service import get_project_dashboard
        project = Project(title="Dashboard Project", owner_id=1)
        db.session.add(project)
        db.session.commit()
        task1 = Task(title="Ongoing Task", owner_id=1, project_id=project.id, status=TaskStatusEnum.ONGOING)
        task2 = Task(title="Completed Task", owner_id=1, project_id=project.id, status=TaskStatusEnum.COMPLETED)
        db.session.add_all([task1, task2])
        db.session.commit()

        dashboard_data, error = get_project_dashboard(project.id, 1, status_filter='Ongoing')
        self.assertIsNone(error)
        self.assertEqual(len(dashboard_data['tasks']), 1)
        self.assertEqual(dashboard_data['tasks'][0]['title'], 'Ongoing Task')

    def test_get_all_tasks_for_user(self):
        """Test getting all tasks for a user"""
        from app.service import get_all_tasks
        task1 = Task(title="User Task 1", owner_id=1)
        task2 = Task(title="User Task 2", owner_id=1)
        db.session.add_all([task1, task2])
        db.session.commit()

        tasks = get_all_tasks(1)
        self.assertEqual(len(tasks), 2)

    def test_get_task_details(self):
        """Test getting task details"""
        from app.service import get_task_details
        task = Task(title="Details Task", owner_id=1)
        db.session.add(task)
        db.session.commit()

        task_details = get_task_details(task.id)
        self.assertEqual(task_details['title'], 'Details Task')

    def test_delete_comment(self):
        """Test deleting a comment"""
        from app.service import delete_comment
        task = Task(title="Comment Task", owner_id=1)
        db.session.add(task)
        db.session.commit()
        comment = Comment(body="Test Comment", author_id=1, task_id=task.id)
        db.session.add(comment)
        db.session.commit()

        result = delete_comment(comment.id)
        self.assertTrue(result)

    def test_get_task_collaborators(self):
        """Test getting task collaborators"""
        from app.service import get_task_collaborators
        task = Task(title="Collaborator Task", owner_id=1)
        db.session.add(task)
        db.session.commit()
        db.session.execute(task_collaborators.insert().values(task_id=task.id, user_id=2))
        db.session.commit()

        collaborators = get_task_collaborators(task.id)
        self.assertEqual(len(collaborators), 1)

    def test_add_and_remove_task_collaborators(self):
        """Test adding and removing task collaborators"""
        from app.service import add_task_collaborators, remove_task_collaborator
        task = Task(title="Add/Remove Collaborator Task", owner_id=1)
        db.session.add(task)
        db.session.commit()

        add_task_collaborators(task.id, [2, 3], 1)
        collaborators = db.session.execute(task_collaborators.select().where(task_collaborators.c.task_id == task.id)).fetchall()
        self.assertEqual(len(collaborators), 2)

        remove_task_collaborator(task.id, [2], 1)
        collaborators = db.session.execute(task_collaborators.select().where(task_collaborators.c.task_id == task.id)).fetchall()
        self.assertEqual(len(collaborators), 1)

    def test_add_and_get_attachment(self):
        """Test adding and getting an attachment"""
        from app.service import add_attachment, get_attachment_url
        task = Task(title="Attachment Task", owner_id=1)
        db.session.add(task)
        db.session.commit()

        mock_file = MagicMock()
        mock_file.filename = 'test.txt'
        mock_file.content_type = 'text/plain'

        with patch('app.service.current_app.s3_client') as mock_s3_client:
            mock_s3_client.upload_fileobj.return_value = None
            mock_s3_client.generate_presigned_url.return_value = 'http://presigned-url.com'

            attachment = add_attachment(task.id, mock_file, 'test.txt')
            self.assertIsNotNone(attachment)

            url, msg = get_attachment_url(task.id, attachment['id'])
            self.assertEqual(url['url'], 'http://presigned-url.com')

    def test_delete_attachment(self):
        """Test deleting an attachment"""
        from app.service import delete_attachment_url
        task = Task(title="Delete Attachment Task", owner_id=1)
        attachment = Attachment(filename='test.txt', url='test_key', task=task)
        db.session.add_all([task, attachment])
        db.session.commit()

        with patch('app.service.current_app.s3_client') as mock_s3_client:
            mock_s3_client.delete_object.return_value = None
            success, msg = delete_attachment_url(task.id, attachment.id)
            self.assertTrue(success)

    def test_get_user_projects(self):
        """Test getting user projects"""
        from app.service import get_user_projects
        project1 = Project(title="User Project 1", owner_id=1)
        project2 = Project(title="User Project 2", owner_id=2)
        db.session.add_all([project1, project2])
        db.session.commit()
        db.session.execute(project_collaborators.insert().values(project_id=project2.id, user_id=1))
        db.session.commit()

        # user_id=1 owns the project from setUp and project1, and is a collaborator on the setUp project and project2
        projects = get_user_projects(1)
        self.assertEqual(len(projects), 3)

        owned_projects = get_user_projects(1, role_filter='owner')
        self.assertEqual(len(owned_projects), 2)

        collab_projects = get_user_projects(1, role_filter='collaborator')
        self.assertEqual(len(collab_projects), 2)

    def test_update_project(self):
        """Test updating a project"""
        from app.service import update_project
        project = Project(title="Update Project", owner_id=1)
        db.session.add(project)
        db.session.commit()

        update_data = {'title': 'Updated Title', 'description': 'Updated Description'}
        updated_project, msg = update_project(project.id, 1, update_data)
        self.assertEqual(updated_project['title'], 'Updated Title')

    def test_delete_project(self):
        """Test deleting a project"""
        from app.service import delete_project
        project = Project(title="Delete Project", owner_id=1)
        db.session.add(project)
        db.session.commit()

        success, msg = delete_project(project.id, 1)
        self.assertTrue(success)

    def test_add_and_remove_project_collaborator(self):
        """Test adding and removing a project collaborator"""
        from app.service import add_project_collaborator, remove_project_collaborator
        project = Project(title="Project Collaborator Task", owner_id=1)
        db.session.add(project)
        db.session.commit()

        add_project_collaborator(project.id, 1, 2)
        collaborators = db.session.execute(project_collaborators.select().where(project_collaborators.c.project_id == project.id)).fetchall()
        self.assertEqual(len(collaborators), 1)

        remove_project_collaborator(project.id, 1, 2)
        collaborators = db.session.execute(project_collaborators.select().where(project_collaborators.c.project_id == project.id)).fetchall()
        self.assertEqual(len(collaborators), 0)

    def test_get_project_tasks(self):
        """Test getting project tasks"""
        from app.service import get_project_tasks
        project = Project(title="Project Tasks", owner_id=1)
        task = Task(title="Task in Project", project=project, owner_id=1)
        db.session.add_all([project, task])
        db.session.commit()

        tasks, msg = get_project_tasks(project.id)
        self.assertEqual(len(tasks), 1)

    def test_add_existing_task_to_project(self):
        """Test adding an existing task to a project"""
        from app.service import add_existing_task_to_project
        project = Project(title="Add Existing Task Project", owner_id=1)
        task = Task(title="Standalone Task", owner_id=1)
        db.session.add_all([project, task])
        db.session.commit()

        updated_task, msg = add_existing_task_to_project(task.id, project.id, 1)
        self.assertEqual(updated_task['project_id'], project.id)

    def test_remove_task_from_project(self):
        """Test removing a task from a project"""
        from app.service import remove_task_from_project
        project = Project(title="Remove Task Project", owner_id=1)
        task = Task(title="Task to Remove", project=project, owner_id=1)
        db.session.add_all([project, task])
        db.session.commit()

        updated_task, msg = remove_task_from_project(task.id, 1)
        self.assertIsNone(updated_task['project_id'])

    def test_create_task_in_project(self):
        """Test creating a task in a project"""
        from app.service import create_task_in_project
        project = Project(title="Create Task in Project", owner_id=1)
        db.session.add(project)
        db.session.commit()

        task_data = {'title': 'New Task in Project', 'owner_id': 1}
        new_task, msg = create_task_in_project(task_data, project.id, 1)
        self.assertIsNotNone(new_task)
        self.assertEqual(new_task.project_id, project.id)

    def test_get_standalone_tasks_for_user(self):
        """Test getting standalone tasks for a user"""
        from app.service import get_standalone_tasks_for_user
        task = Task(title="My Standalone Task", owner_id=1)
        db.session.add(task)
        db.session.commit()

        tasks = get_standalone_tasks_for_user(1)
        self.assertEqual(len(tasks), 1)



class TestRabbitMQPublisher(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['RABBITMQ_URL'] = 'amqp://test'
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch('app.rabbitmq_publisher.pika')
    def test_publish_to_rabbitmq_success(self, mock_pika):
        """Test successful publishing to RabbitMQ"""
        from app.rabbitmq_publisher import publish_to_rabbitmq

        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_pika.URLParameters.return_value = {}
        mock_pika.BlockingConnection.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel

        with self.app.app_context():
            result = publish_to_rabbitmq('test_queue', {'message': 'hello'})

        self.assertTrue(result)
        mock_channel.queue_declare.assert_called_once_with(queue='test_queue', durable=True)
        mock_channel.basic_publish.assert_called_once()

    @patch('app.rabbitmq_publisher.pika')
    def test_publish_to_rabbitmq_failure(self, mock_pika):
        """Test failure in publishing to RabbitMQ"""
        from app.rabbitmq_publisher import publish_to_rabbitmq

        mock_pika.BlockingConnection.side_effect = Exception("Connection error")

        with self.app.app_context():
            result = publish_to_rabbitmq('test_queue', {'message': 'hello'})

        self.assertFalse(result)

    @patch('app.rabbitmq_publisher.publish_to_rabbitmq')
    def test_publish_status_update(self, mock_publish):
        """Test publishing a status update"""
        from app.rabbitmq_publisher import publish_status_update

        publish_status_update(1, 'old', 'new', 2)

        mock_publish.assert_called_once_with(
            'task_status_updates',
            {
                'task_id': 1,
                'old_status': 'old',
                'new_status': 'new',
                'changed_by_id': 2
            }
        )

    @patch('app.rabbitmq_publisher.publish_to_rabbitmq')
    def test_publish_mention_alert(self, mock_publish):
        """Test publishing a mention alert"""
        from app.rabbitmq_publisher import publish_mention_alert

        publish_mention_alert(1, 2, 3, 4, 'hello')

        mock_publish.assert_called_once_with(
            'mention_alerts',
            {
                'task_id': 1,
                'comment_id': 2,
                'mentioned_user_id': 3,
                'author_id': 4,
                'comment_body': 'hello'
            }
        )


# ==================== UNIT TESTS - REPORT GENERATOR ====================

class TestReportGenerator(TestTaskRoutesIntegration):

    @patch('app.report.generator_service.requests.get')
    def test_fetch_user_details_success(self, mock_requests_get):
        """Test fetching user details successfully"""
        from app.report.generator_service import _fetch_user_details

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 1, 'name': 'Test User'}
        mock_requests_get.return_value = mock_response

        with self.app.app_context():
            user = _fetch_user_details(1)

        self.assertEqual(user['name'], 'Test User')

    @patch('app.report.generator_service.requests.get')
    def test_fetch_user_details_not_found(self, mock_requests_get):
        """Test fetching user details when user not found"""
        from app.report.generator_service import _fetch_user_details

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response

        with self.app.app_context():
            user = _fetch_user_details(1)

        self.assertIn('Not Found', user['name'])

    @patch('app.report.generator_service.requests.get')
    def test_fetch_user_details_service_down(self, mock_requests_get):
        """Test fetching user details when service is down"""
        from app.report.generator_service import _fetch_user_details

        mock_requests_get.side_effect = requests.exceptions.RequestException

        with self.app.app_context():
            user = _fetch_user_details(1)

        self.assertIn('Service Down?', user['name'])

    @patch('app.report.generator_service._fetch_user_details')
    def test_generate_project_pdf_report_success(self, mock_fetch_user):
        """Test generating a project PDF report"""
        from app.report.generator_service import generate_project_pdf_report

        mock_fetch_user.return_value = {'id': 1, 'name': 'Test User'}

        pdf_data = generate_project_pdf_report(project_id=1, user_id=1)

        self.assertIsNotNone(pdf_data)
        self.assertTrue(pdf_data.startswith(b'%PDF-'))

    @patch('app.report.generator_service.service.get_project_by_id')
    def test_generate_project_pdf_report_no_project(self, mock_get_project):
        """Test report generation when project not found"""
        from app.report.generator_service import generate_project_pdf_report

        mock_get_project.return_value = (None, "Project not found")

        pdf_data = generate_project_pdf_report(project_id=999, user_id=1)

        self.assertIsNone(pdf_data)


# ==================== UNIT TESTS - REPORT ROUTES ====================

class TestReportRoutesUnit(TestTaskRoutesUnit):

    @patch('app.report.routes.generator.generate_project_pdf_report')
    def test_get_project_report_success(self, mock_generate_report):
        """Test project report route success"""
        mock_generate_report.return_value = b'pdf_content'

        response = self.client.get('/api/reports/project/1?user_id=1')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'pdf_content')
        self.assertIn('application/pdf', response.headers['Content-Type'])

    def test_get_project_report_missing_user_id(self):
        """Test project report route with missing user_id"""
        response = self.client.get('/api/reports/project/1')

        self.assertEqual(response.status_code, 400)

    @patch('app.report.routes.generator.generate_project_pdf_report')
    def test_get_project_report_not_found(self, mock_generate_report):
        """Test project report route when report not generated"""
        mock_generate_report.return_value = None

        response = self.client.get('/api/reports/project/1?user_id=1')

        self.assertEqual(response.status_code, 404)

    @patch('app.report.routes.generator.generate_project_pdf_report')
    def test_get_project_report_exception(self, mock_generate_report):
        """Test project report route with exception"""
        mock_generate_report.side_effect = Exception("PDF error")

        response = self.client.get('/api/reports/project/1?user_id=1')

        self.assertEqual(response.status_code, 500)


if __name__ == '__main__':
    unittest.main()