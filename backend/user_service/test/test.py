# To run the test, navigate to the user_service directory and run 'python3 -m unittest discover test'
# to run coverage:
# docker-compose exec user_service pip install coverage
# docker-compose exec user_service coverage run -m unittest test.test
# docker-compose exec user_service coverage report

import unittest
from unittest.mock import patch, MagicMock, ANY
import os
import sys
import jwt
from datetime import datetime, timedelta

# Add the parent directory to the sys.path to allow for absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.service import (
    login_user, generate_token, get_user_by_id, get_user_by_email,
    get_user_by_username, get_all_users, get_all_teams, get_all_users_in_team,
    get_all_dept, get_all_users_in_dept, create_user
)
from app.models import User, Team, Department, RoleEnum, db

class TestUserService(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config_name="testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        # Setup mock data
        self.user_data = {
            'id': 1,
            'username': 'testuser',
            'name': 'Test User',
            'password': 'password123',
            'email': 'test@example.com',
            'role': RoleEnum.STAFF.value,
            'team_id': 1
        }
        self.team_data = {
            'id': 1,
            'name': 'Test Team',
            'department_id': 1
        }
        self.department_data = {
            'id': 1,
            'name': 'Test Department'
        }

    def tearDown(self):
        self.app_context.pop()

    @patch('app.service.get_user_by_email')
    @patch('app.service.generate_token')
    def test_login_user_success(self, mock_generate_token, mock_get_user_by_email):
        # Mocking the user and their password check
        mock_user = MagicMock()
        mock_user.check_password.return_value = True
        mock_user.id = self.user_data['id']
        mock_user.name = self.user_data['name']
        mock_user.role.value = self.user_data['role']
        
        mock_get_user_by_email.return_value = mock_user
        mock_generate_token.return_value = "some_jwt_token"

        token, user_id, user_name, user_role = login_user({
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })

        self.assertEqual(token, "some_jwt_token")
        self.assertEqual(user_id, self.user_data['id'])
        self.assertEqual(user_name, self.user_data['name'])
        self.assertEqual(user_role, self.user_data['role'])
        mock_get_user_by_email.assert_called_with(self.user_data['email'])
        mock_user.check_password.assert_called_with(self.user_data['password'])
        mock_generate_token.assert_called_with(self.user_data['id'])

    @patch('app.service.get_user_by_email')
    def test_login_user_failure_wrong_password(self, mock_get_user_by_email):
        # Mocking the user and their password check
        mock_user = MagicMock()
        mock_user.check_password.return_value = False
        mock_get_user_by_email.return_value = mock_user

        token, user_id, user_name, user_role = login_user({
            'email': self.user_data['email'],
            'password': 'wrong_password'
        })

        self.assertIsNone(token)
        self.assertIsNone(user_id)
        self.assertIsNone(user_name)
        self.assertIsNone(user_role)
        mock_get_user_by_email.assert_called_with(self.user_data['email'])
        mock_user.check_password.assert_called_with('wrong_password')

    @patch('app.service.get_user_by_email')
    def test_login_user_failure_no_user(self, mock_get_user_by_email):
        # Mocking no user found
        mock_get_user_by_email.return_value = None

        token, user_id, user_name, user_role = login_user({
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        self.assertIsNone(token)
        self.assertIsNone(user_id)
        self.assertIsNone(user_name)
        self.assertIsNone(user_role)
        mock_get_user_by_email.assert_called_with(self.user_data['email'])

    def test_generate_token(self):
        user_id = 1
        token = generate_token(user_id)
        
        self.assertIsInstance(token, str)
        decoded_payload = jwt.decode(token, self.app.config['SECRET_KEY'], algorithms=["HS256"])
        self.assertEqual(decoded_payload['sub'], str(user_id))
        self.assertTrue('exp' in decoded_payload)
        self.assertTrue('iat' in decoded_payload)

    @patch('app.models.User.query')
    def test_get_user_by_id(self, mock_query):
        mock_user = MagicMock()
        mock_query.get.return_value = mock_user
        
        user = get_user_by_id(1)
        
        self.assertEqual(user, mock_user)
        mock_query.get.assert_called_with(1)

    @patch('app.models.User.query')
    def test_get_user_by_email(self, mock_query):
        mock_user = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_user
        
        user = get_user_by_email('test@example.com')
        
        self.assertEqual(user, mock_user)
        mock_query.filter_by.assert_called_with(email='test@example.com')

    @patch('app.models.User.query')
    def test_get_user_by_username(self, mock_query):
        mock_user = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_user
        
        user = get_user_by_username('testuser')
        
        self.assertEqual(user, mock_user)
        mock_query.filter_by.assert_called_with(username='testuser')

    @patch('app.models.User.query')
    def test_get_all_users(self, mock_query):
        mock_users = [MagicMock(), MagicMock()]
        mock_query.all.return_value = mock_users
        
        users = get_all_users()
        
        self.assertEqual(users, mock_users)
        mock_query.all.assert_called_once()

    @patch('app.models.Team.query')
    def test_get_all_teams(self, mock_query):
        mock_teams = [MagicMock(), MagicMock()]
        mock_query.all.return_value = mock_teams
        
        teams = get_all_teams()
        
        self.assertEqual(teams, mock_teams)
        mock_query.all.assert_called_once()

    @patch('app.models.User.query')
    def test_get_all_users_in_team(self, mock_query):
        mock_users = [MagicMock(), MagicMock()]
        mock_query.filter_by.return_value.all.return_value = mock_users
        
        users = get_all_users_in_team(1)
        
        self.assertEqual(users, mock_users)
        mock_query.filter_by.assert_called_with(team_id=1)

    @patch('app.models.Department.query')
    def test_get_all_dept(self, mock_query):
        mock_depts = [MagicMock(), MagicMock()]
        mock_query.all.return_value = mock_depts
        
        depts = get_all_dept()
        
        self.assertEqual(depts, mock_depts)
        mock_query.all.assert_called_once()

    @patch('app.models.User.query')
    def test_get_all_users_in_dept(self, mock_query):
        mock_users = [MagicMock(), MagicMock()]
        mock_join = mock_query.join.return_value
        mock_filter = mock_join.filter.return_value
        mock_filter.all.return_value = mock_users

        users = get_all_users_in_dept(1)

        self.assertEqual(users, mock_users)
        mock_query.join.assert_called_with(Team)
        mock_join.filter.assert_called_with(ANY)
        mock_filter.all.assert_called_once()

    @patch('app.service.get_user_by_email')
    @patch('app.service.get_user_by_username')
    @patch('app.models.Team.query')
    @patch('app.models.db.session')
    def test_create_user_success(self, mock_session, mock_team_query, mock_get_user_by_username, mock_get_user_by_email):
        mock_get_user_by_email.return_value = None
        mock_get_user_by_username.return_value = None
        mock_team_query.get.return_value = MagicMock()

        new_user, error_msg = create_user(self.user_data)
        
        self.assertIsNone(error_msg)
        self.assertIsInstance(new_user, User)
        self.assertEqual(new_user.username, self.user_data['username'])
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch('app.service.get_user_by_email')
    def test_create_user_email_exists(self, mock_get_user_by_email):
        mock_get_user_by_email.return_value = MagicMock()

        new_user, error_msg = create_user(self.user_data)

        self.assertIsNone(new_user)
        self.assertEqual(error_msg, "Email already in use.")

    @patch('app.service.get_user_by_email')
    @patch('app.service.get_user_by_username')
    def test_create_user_username_exists(self, mock_get_user_by_username, mock_get_user_by_email):
        mock_get_user_by_email.return_value = None
        mock_get_user_by_username.return_value = MagicMock()

        new_user, error_msg = create_user(self.user_data)

        self.assertIsNone(new_user)
        self.assertEqual(error_msg, "Username already taken.")

    @patch('app.service.get_user_by_email')
    @patch('app.service.get_user_by_username')
    @patch('app.models.Team.query')
    def test_create_user_team_not_found(self, mock_team_query, mock_get_user_by_username, mock_get_user_by_email):
        mock_get_user_by_email.return_value = None
        mock_get_user_by_username.return_value = None
        mock_team_query.get.return_value = None

        new_user, error_msg = create_user(self.user_data)

        self.assertIsNone(new_user)
        self.assertEqual(error_msg, f"Team with id {self.user_data['team_id']} not found.")
        
    @patch('app.service.get_user_by_email')
    @patch('app.service.get_user_by_username')
    @patch('app.models.Team.query')
    def test_create_user_invalid_role(self, mock_team_query, mock_get_user_by_username, mock_get_user_by_email):
        mock_get_user_by_email.return_value = None
        mock_get_user_by_username.return_value = None
        mock_team_query.get.return_value = MagicMock()

        invalid_role_data = self.user_data.copy()
        invalid_role_data['role'] = 'InvalidRole'

        new_user, error_msg = create_user(invalid_role_data)
        
        self.assertIsNone(new_user)
        self.assertIn("Invalid role: InvalidRole", error_msg)

class TestUserServiceRoutes(unittest.TestCase):
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # sample data
        self.user_data = {
            'username': 'testuser',
            'name': 'Test User',
            'password': 'testpassword',
            'email': 'test@example.com',
            'role': 'Staff',
            'team_id': 1
        }
        self.team = Team(name='Test Team')
        self.department = Department(name='Test Department')
        self.team.department = self.department
        db.session.add(self.department)
        db.session.add(self.team)
        db.session.commit()

    def tearDown(self):
        """teardown all initialized variables."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        """Test API can create a user (POST request)"""
        res = self.client().post('/user/create', json=self.user_data)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data['username'], self.user_data['username'])

    def test_get_user_by_id(self):
        """Test API can get a single user by id."""
        # Create a user first
        res_create = self.client().post('/user/create', json=self.user_data)
        user_id = res_create.get_json()['id']
        # Retrieve the user
        res_get = self.client().get(f'/user/{user_id}')
        self.assertEqual(res_get.status_code, 200)
        data = res_get.get_json()
        self.assertEqual(data['id'], user_id)

    def test_user_login(self):
        """Test user can login (POST request)"""
        # Create a user first
        self.client().post('/user/create', json=self.user_data)
        # Login
        res = self.client().post('/user/login', json={
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['token'])

    def test_get_all_users(self):
        """Test API can get all users."""
        self.client().post('/user/create', json=self.user_data)
        res = self.client().get('/user')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data), 1)

    def test_get_all_teams(self):
        """Test API can get all teams."""
        res = self.client().get('/user/teams')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data), 1)

    def test_get_all_users_in_team(self):
        """Test API can get all users in a team."""
        self.client().post('/user/create', json=self.user_data)
        res = self.client().get(f'/user/team/1')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data), 1)

    def test_get_all_departments(self):
        """Test API can get all departments."""
        res = self.client().get('/user/departments')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data), 1)

    def test_get_all_users_in_department(self):
        """Test API can get all users in a department."""
        self.client().post('/user/create', json=self.user_data)
        res = self.client().get(f'/user/department/1')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data), 1)

    def test_verify_jwt(self):
        """Test JWT verification."""
        self.client().post('/user/create', json=self.user_data)
        res_login = self.client().post('/user/login', json={
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        token = res_login.get_json()['token']
        res_verify = self.client().get('/user/verifyJWT', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(res_verify.status_code, 200)

if __name__ == '__main__':
    unittest.main()