import unittest
from unittest.mock import patch, MagicMock, Mock
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from app.routes import task_bp
from app.models import Task, TaskStatusEnum, Project
import json
from datetime import datetime


class TestTaskRoutes(unittest.TestCase):
    """Base test class for task routes"""
    
    def setUp(self):
        """Set up test client and mock data"""
        self.app = Flask(__name__)
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


# ==================== GET /tasks TESTS ====================

class TestGetAllTasks(TestTaskRoutes):
    """Test cases for GET /tasks route"""
    
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
        mock_get_all_tasks.return_value = None
        
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
    def test_get_all_tasks_with_status_filter(self, mock_get_all_tasks):
        """Test get all tasks with status filter (parameter ignored in current implementation)"""
        mock_get_all_tasks.return_value = [self.mock_task1]
        
        response = self.client.get('/api/tasks?owner_id=1&status=Ongoing')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        mock_get_all_tasks.assert_called_once_with(1)
    
    @patch('app.routes.service.get_all_tasks')
    def test_get_all_tasks_invalid_owner_id(self, mock_get_all_tasks):
        """Test get all tasks with invalid owner_id type"""
        mock_get_all_tasks.return_value = []
        
        response = self.client.get('/api/tasks?owner_id=invalid')
        
        # Flask will handle type conversion, invalid string becomes None
        self.assertEqual(response.status_code, 400)
    
    @patch('app.routes.service.get_all_tasks')
    def test_get_all_tasks_zero_owner_id(self, mock_get_all_tasks):
        """Test get all tasks with owner_id=0"""
        mock_get_all_tasks.return_value = []
        
        response = self.client.get('/api/tasks?owner_id=0')
        
        self.assertEqual(response.status_code, 200)
        mock_get_all_tasks.assert_called_once_with(0)
    
    @patch('app.routes.service.get_all_tasks')
    def test_get_all_tasks_negative_owner_id(self, mock_get_all_tasks):
        """Test get all tasks with negative owner_id"""
        mock_get_all_tasks.return_value = []
        
        response = self.client.get('/api/tasks?owner_id=-1')
        
        self.assertEqual(response.status_code, 200)
        mock_get_all_tasks.assert_called_once_with(-1)
    
    @patch('app.routes.service.get_all_tasks')
    def test_get_all_tasks_service_exception(self, mock_get_all_tasks):
        """Test get all tasks when service raises exception"""
        mock_get_all_tasks.side_effect = Exception("Database error")
        
        response = self.client.get('/api/tasks?owner_id=1')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Database error')


# ==================== GET /projects/<int:project_id>/tasks TESTS ====================

class TestGetProjectTasks(TestTaskRoutes):
    """Test cases for GET /projects/<int:project_id>/tasks route"""
    
    @patch('app.routes.service.get_project_tasks')
    def test_get_project_tasks_success(self, mock_get_project_tasks):
        """Test successfully retrieving all tasks for a project"""
        mock_get_project_tasks.return_value = ([self.mock_task3], None)
        
        response = self.client.get('/api/projects/1/tasks')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Project Task 1')
        self.assertEqual(data[0]['project_id'], 1)
        mock_get_project_tasks.assert_called_once_with(1)
    
    @patch('app.routes.service.get_project_tasks')
    def test_get_project_tasks_empty_project(self, mock_get_project_tasks):
        """Test get project tasks when project has no tasks"""
        mock_get_project_tasks.return_value = ([], None)
        
        response = self.client.get('/api/projects/1/tasks')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)
    
    @patch('app.routes.service.get_project_tasks')
    def test_get_project_tasks_multiple_tasks(self, mock_get_project_tasks):
        """Test get project tasks with multiple tasks"""
        task4 = self._create_mock_task(
            id=5,
            title="Project Task 2",
            description="Another project task",
            owner_id=2,
            status=TaskStatusEnum.UNDER_REVIEW,
            project_id=1
        )
        mock_get_project_tasks.return_value = ([self.mock_task3, task4], None)
        
        response = self.client.get('/api/projects/1/tasks')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['project_id'], 1)
        self.assertEqual(data[1]['project_id'], 1)
    
    @patch('app.routes.service.get_project_tasks')
    def test_get_project_tasks_not_found(self, mock_get_project_tasks):
        """Test get project tasks when project doesn't exist"""
        mock_get_project_tasks.return_value = (None, "Project not found")
        
        response = self.client.get('/api/projects/999/tasks')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Project not found')
    
    @patch('app.routes.service.get_project_tasks')
    def test_get_project_tasks_forbidden(self, mock_get_project_tasks):
        """Test get project tasks when user doesn't have access"""
        mock_get_project_tasks.return_value = (None, "Forbidden: Access denied")
        
        response = self.client.get('/api/projects/1/tasks')
        
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Forbidden', data['error'])
    
    @patch('app.routes.service.get_project_tasks')
    def test_get_project_tasks_zero_id(self, mock_get_project_tasks):
        """Test get project tasks with project_id=0"""
        mock_get_project_tasks.return_value = (None, "Project not found")
        
        response = self.client.get('/api/projects/0/tasks')
        
        self.assertEqual(response.status_code, 404)
    
    @patch('app.routes.service.get_project_tasks')
    def test_get_project_tasks_negative_id(self, mock_get_project_tasks):
        """Test get project tasks with negative project_id"""
        mock_get_project_tasks.return_value = (None, "Project not found")
        
        response = self.client.get('/api/projects/-1/tasks')
        
        self.assertEqual(response.status_code, 404)
    
    @patch('app.routes.service.get_project_tasks')
    def test_get_project_tasks_service_exception(self, mock_get_project_tasks):
        """Test get project tasks when service raises exception"""
        mock_get_project_tasks.side_effect = Exception("Database connection failed")
        
        response = self.client.get('/api/projects/1/tasks')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Database connection failed')
    
    @patch('app.routes.service.get_project_tasks')
    def test_get_project_tasks_very_large_id(self, mock_get_project_tasks):
        """Test get project tasks with very large project_id"""
        mock_get_project_tasks.return_value = (None, "Project not found")
        
        response = self.client.get('/api/projects/999999999/tasks')
        
        self.assertEqual(response.status_code, 404)
        mock_get_project_tasks.assert_called_once_with(999999999)


# ==================== POST /tasks TESTS ====================

class TestCreateTask(TestTaskRoutes):
    """Test cases for POST /tasks route"""
    
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
    def test_create_task_empty_json(self, mock_create_task):
        """Test create task with empty JSON"""
        response = self.client.post('/api/tasks',
                                   data=json.dumps({}),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
    
    
    @patch('app.routes.service.create_task')
    def test_create_task_with_all_fields(self, mock_create_task):
        """Test create task with all optional fields"""
        task_data = {
            'title': 'Complete Task',
            'description': 'Full description',
            'owner_id': 1,
            'status': 'Ongoing',
            'deadline': '2025-12-31T23:59:59',
            'priority': 1,
            'project_id': 1,
            'parent_task_id': None
        }
        mock_create_task.return_value = task_data
        
        response = self.client.post('/api/tasks',
                                   data=json.dumps(task_data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
    
    @patch('app.routes.service.create_task')
    def test_create_task_service_exception(self, mock_create_task):
        """Test create task when service raises exception"""
        task_data = {
            'title': 'New Task',
            'owner_id': 1
        }
        mock_create_task.side_effect = Exception("Failed to create task")
        
        response = self.client.post('/api/tasks',
                                   data=json.dumps(task_data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)


# ==================== GET /tasks/<int:task_id> TESTS ====================

class TestGetTaskById(TestTaskRoutes):
    """Test cases for GET /tasks/<int:task_id> route"""
    
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
    def test_get_task_with_subtasks(self, mock_get_task_details):
        """Test get task that has subtasks"""
        task_with_subtasks = self.mock_task1.to_json()
        task_with_subtasks['subtasks'] = [self.mock_subtask.to_json()]
        task_with_subtasks['subtask_count'] = 1
        mock_get_task_details.return_value = task_with_subtasks
        
        response = self.client.get('/api/tasks/1')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['subtasks']), 1)
        self.assertEqual(data['subtask_count'], 1)
    
    @patch('app.routes.service.get_task_details')
    def test_get_task_zero_id(self, mock_get_task_details):
        """Test get task with ID 0"""
        mock_get_task_details.return_value = None
        
        response = self.client.get('/api/tasks/0')
        
        self.assertEqual(response.status_code, 404)
    
    @patch('app.routes.service.get_task_details')
    def test_get_task_negative_id(self, mock_get_task_details):
        """Test get task with negative ID"""
        mock_get_task_details.return_value = None
        
        response = self.client.get('/api/tasks/-1')
        
        self.assertEqual(response.status_code, 404)
    
    @patch('app.routes.service.get_task_details')
    def test_get_task_service_exception(self, mock_get_task_details):
        """Test get task when service raises exception"""
        mock_get_task_details.side_effect = Exception("Database error")
        
        response = self.client.get('/api/tasks/1')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)


# ==================== PUT /tasks/<int:task_id> TESTS ====================

class TestUpdateTask(TestTaskRoutes):
    """Test cases for PUT /tasks/<int:task_id> route"""
    
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
    def test_update_task_status_only(self, mock_update_task):
        """Test collaborator updating only task status"""
        update_data = {'status': 'Completed', 'user_id': 2}
        mock_update_task.return_value = (
            {'id': 1, 'status': 'Completed'},
            "Task updated successfully"
        )
        
        response = self.client.put('/api/tasks/1',
                                  data=json.dumps(update_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
    
    @patch('app.routes.service.update_task')
    def test_update_task_invalid_status(self, mock_update_task):
        """Test update task with invalid status"""
        update_data = {'status': 'InvalidStatus', 'user_id': 1}
        mock_update_task.return_value = (None, "Invalid status value")
        
        response = self.client.put('/api/tasks/1',
                                  data=json.dumps(update_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)


# ==================== DELETE /tasks/<int:task_id> TESTS ====================

class TestDeleteTask(TestTaskRoutes):
    """Test cases for DELETE /tasks/<int:task_id> route"""
    
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
        """Test delete task that has subtasks"""
        mock_delete_task.return_value = (
            False,
            "Cannot delete a task that has subtasks"
        )
        
        response = self.client.delete('/api/tasks/1',
                                     data=json.dumps({'user_id': 1}),
                                     content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('subtasks', data['error'])
    
    @patch('app.routes.service.delete_task')
    def test_delete_task_no_user_id(self, mock_delete_task):
        """Test delete task without user_id"""
        mock_delete_task.return_value = (True, "Task deleted successfully")
        
        response = self.client.delete('/api/tasks/1',
                                     data=json.dumps({}),
                                     content_type='application/json')
        
        self.assertEqual(response.status_code, 200)


# ==================== GET /tasks/<int:task_id>/collaborators TESTS ====================

class TestGetTaskCollaborators(TestTaskRoutes):
    """Test cases for GET /tasks/<int:task_id>/collaborators route"""
    
    @patch('app.routes.service.get_task_collaborators')
    def test_get_task_collaborators_success(self, mock_get_collaborators):
        """Test successfully retrieving task collaborators"""
        mock_collaborators = [
            {'user_id': 2, 'name': 'John Doe', 'email': 'john@example.com'},
            {'user_id': 3, 'name': 'Jane Smith', 'email': 'jane@example.com'}
        ]
        mock_get_collaborators.return_value = mock_collaborators
        
        response = self.client.get('/api/tasks/1/collaborators')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['user_id'], 2)
        self.assertEqual(data[1]['user_id'], 3)
        mock_get_collaborators.assert_called_once_with(1)
    
    @patch('app.routes.service.get_task_collaborators')
    def test_get_task_collaborators_empty_list(self, mock_get_collaborators):
        """Test get collaborators when task has no collaborators"""
        mock_get_collaborators.return_value = []
        
        response = self.client.get('/api/tasks/1/collaborators')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)
    
    @patch('app.routes.service.get_task_collaborators')
    def test_get_task_collaborators_single_collaborator(self, mock_get_collaborators):
        """Test get collaborators with a single collaborator"""
        mock_collaborators = [
            {'user_id': 2, 'name': 'John Doe', 'email': 'john@example.com'}
        ]
        mock_get_collaborators.return_value = mock_collaborators
        
        response = self.client.get('/api/tasks/1/collaborators')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['user_id'], 2)
    
    @patch('app.routes.service.get_task_collaborators')
    def test_get_task_collaborators_negative_task_id(self, mock_get_collaborators):
        """Test get collaborators with negative task_id"""
        mock_get_collaborators.return_value = None
        
        response = self.client.get('/api/tasks/-1/collaborators')
        
        self.assertEqual(response.status_code, 404)
    
    @patch('app.routes.service.get_task_collaborators')
    def test_get_task_collaborators_service_exception(self, mock_get_collaborators):
        """Test get collaborators when service raises exception"""
        mock_get_collaborators.side_effect = Exception("Database error")
        
        response = self.client.get('/api/tasks/1/collaborators')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Database error')
    
    @patch('app.routes.service.get_task_collaborators')
    def test_get_task_collaborators_multiple_collaborators(self, mock_get_collaborators):
        """Test get collaborators with multiple collaborators"""
        mock_collaborators = [
            {'user_id': 2, 'name': 'John Doe', 'email': 'john@example.com'},
            {'user_id': 3, 'name': 'Jane Smith', 'email': 'jane@example.com'},
            {'user_id': 4, 'name': 'Bob Johnson', 'email': 'bob@example.com'}
        ]
        mock_get_collaborators.return_value = mock_collaborators
        
        response = self.client.get('/api/tasks/1/collaborators')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['name'], 'John Doe')
        self.assertEqual(data[1]['name'], 'Jane Smith')
        self.assertEqual(data[2]['name'], 'Bob Johnson')


# ==================== RUN TESTS ====================

if __name__ == '__main__':
    unittest.main()