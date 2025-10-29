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

if __name__ == '__main__':
    unittest.main()