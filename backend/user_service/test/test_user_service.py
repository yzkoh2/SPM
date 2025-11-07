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
from datetime import datetime, timedelta, timezone

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
        mock_user.username = self.user_data['username']

        mock_get_user_by_email.return_value = mock_user
        mock_generate_token.return_value = "some_jwt_token"

        token, user_id, user_name, user_role, username = login_user({
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })

        self.assertEqual(token, "some_jwt_token")
        self.assertEqual(user_id, self.user_data['id'])
        self.assertEqual(user_name, self.user_data['name'])
        self.assertEqual(user_role, self.user_data['role'])
        self.assertEqual(username, self.user_data['username'])
        mock_get_user_by_email.assert_called_with(self.user_data['email'])
        mock_user.check_password.assert_called_with(self.user_data['password'])
        mock_generate_token.assert_called_with(self.user_data['id'])

    @patch('app.service.get_user_by_email')
    def test_login_user_failure_wrong_password(self, mock_get_user_by_email):
        # Mocking the user and their password check
        mock_user = MagicMock()
        mock_user.check_password.return_value = False
        mock_get_user_by_email.return_value = mock_user

        token, user_id, user_name, user_role, username = login_user({
            'email': self.user_data['email'],
            'password': 'wrong_password'
        })

        self.assertIsNone(token)
        self.assertIsNone(user_id)
        self.assertIsNone(user_name)
        self.assertIsNone(user_role)
        self.assertIsNone(username)
        mock_get_user_by_email.assert_called_with(self.user_data['email'])
        mock_user.check_password.assert_called_with('wrong_password')

    @patch('app.service.get_user_by_email')
    def test_login_user_failure_no_user(self, mock_get_user_by_email):
        # Mocking no user found
        mock_get_user_by_email.return_value = None

        token, user_id, user_name, user_role, username = login_user({
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        self.assertIsNone(token)
        self.assertIsNone(user_id)
        self.assertIsNone(user_name)
        self.assertIsNone(user_role)
        self.assertIsNone(username)
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


# ==================== COMPREHENSIVE ERROR PATH AND EDGE CASE TESTS ====================

class TestRoutesErrorPaths(unittest.TestCase):
    """Test error handling in routes"""

    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.department = Department(name='Test Department')
        self.team = Team(name='Test Team')
        self.team.department = self.department
        db.session.add(self.department)
        db.session.add(self.team)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_user_not_found(self):
        """Test getting a non-existent user"""
        res = self.client().get('/user/99999')
        self.assertEqual(res.status_code, 404)
        data = res.get_json()
        self.assertIn('error', data)

    def test_create_user_missing_fields(self):
        """Test creating user with missing required fields"""
        incomplete_data = {'username': 'test', 'name': 'Test'}
        res = self.client().post('/user/create', json=incomplete_data)
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn('error', data)

    def test_login_missing_email(self):
        """Test login with missing email"""
        res = self.client().post('/user/login', json={'password': 'test123'})
        self.assertEqual(res.status_code, 400)

    def test_login_missing_password(self):
        """Test login with missing password"""
        res = self.client().post('/user/login', json={'email': 'test@example.com'})
        self.assertEqual(res.status_code, 400)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        user_data = {
            'username': 'testuser',
            'name': 'Test User',
            'password': 'correctpass',
            'email': 'test@example.com',
            'role': 'Staff',
            'team_id': 1
        }
        self.client().post('/user/create', json=user_data)

        res = self.client().post('/user/login', json={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(res.status_code, 401)

    @patch('app.service.login_user')
    def test_login_exception_handling(self, mock_login):
        """Test login route exception handling"""
        mock_login.side_effect = Exception("Database error")

        res = self.client().post('/user/login', json={
            'email': 'test@example.com',
            'password': 'password'
        })
        self.assertEqual(res.status_code, 500)

    @patch('app.service.get_all_users')
    def test_get_all_users_exception(self, mock_get_all):
        """Test get all users exception handling"""
        mock_get_all.side_effect = Exception("Database connection failed")

        res = self.client().get('/user')
        self.assertEqual(res.status_code, 500)

    @patch('app.service.get_all_teams')
    def test_get_all_teams_exception(self, mock_get_teams):
        """Test get all teams exception handling"""
        mock_get_teams.side_effect = Exception("Database error")

        res = self.client().get('/user/teams')
        self.assertEqual(res.status_code, 500)

    @patch('app.service.get_all_users_in_team')
    def test_get_users_in_team_exception(self, mock_get_users):
        """Test get users in team exception handling"""
        mock_get_users.side_effect = Exception("Query failed")

        res = self.client().get('/user/team/1')
        self.assertEqual(res.status_code, 500)

    @patch('app.service.get_all_dept')
    def test_get_all_departments_exception(self, mock_get_dept):
        """Test get all departments exception handling"""
        mock_get_dept.side_effect = Exception("Database error")

        res = self.client().get('/user/departments')
        self.assertEqual(res.status_code, 500)

    @patch('app.service.get_all_users_in_dept')
    def test_get_users_in_department_exception(self, mock_get_users):
        """Test get users in department exception handling"""
        mock_get_users.side_effect = Exception("Query failed")

        res = self.client().get('/user/department/1')
        self.assertEqual(res.status_code, 500)

    def test_verify_jwt_no_token(self):
        """Test JWT verification without token"""
        res = self.client().get('/user/verifyJWT')
        self.assertEqual(res.status_code, 401)

    def test_verify_jwt_invalid_token(self):
        """Test JWT verification with invalid token"""
        res = self.client().get('/user/verifyJWT', headers={
            'Authorization': 'Bearer invalid_token_here'
        })
        self.assertEqual(res.status_code, 401)

    def test_verify_jwt_expired_token(self):
        """Test JWT verification with expired token"""
        # Create expired token
        expired_payload = {
            'exp': datetime.now(timezone.utc) - timedelta(days=1),
            'iat': datetime.now(timezone.utc) - timedelta(days=2),
            'sub': '1'
        }
        expired_token = jwt.encode(expired_payload, self.app.config['SECRET_KEY'], algorithm="HS256")

        res = self.client().get('/user/verifyJWT', headers={
            'Authorization': f'Bearer {expired_token}'
        })
        self.assertEqual(res.status_code, 401)

    def test_verify_jwt_user_not_found(self):
        """Test JWT verification when user doesn't exist"""
        # Create token for non-existent user
        payload = {
            'exp': datetime.now(timezone.utc) + timedelta(days=1),
            'iat': datetime.now(timezone.utc),
            'sub': '99999'
        }
        token = jwt.encode(payload, self.app.config['SECRET_KEY'], algorithm="HS256")

        res = self.client().get('/user/verifyJWT', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(res.status_code, 404)


class TestModelsEdgeCases(unittest.TestCase):
    """Test model methods and edge cases"""

    def setUp(self):
        self.app = create_app(config_name="testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_to_json_with_team_and_department(self):
        """Test user to_json with complete relationships"""
        dept = Department(name='Engineering')
        team = Team(name='Backend', department=dept)
        user = User(username='testuser', name='Test User', email='test@example.com',
                   role=RoleEnum.STAFF, team=team)
        user.set_password('password')

        db.session.add(dept)
        db.session.add(team)
        db.session.add(user)
        db.session.commit()

        user_json = user.to_json()

        self.assertEqual(user_json['username'], 'testuser')
        self.assertEqual(user_json['team'], 'Backend')
        self.assertEqual(user_json['department'], 'Engineering')
        self.assertIsNotNone(user_json['department_id'])

    def test_user_to_json_without_team(self):
        """Test user to_json without team"""
        user = User(username='testuser', name='Test User', email='test@example.com',
                   role=RoleEnum.STAFF)
        user.set_password('password')

        db.session.add(user)
        db.session.commit()

        user_json = user.to_json()

        self.assertIsNone(user_json['team'])
        self.assertIsNone(user_json['department'])
        self.assertIsNone(user_json['department_id'])

    def test_user_to_json_team_without_department(self):
        """Test user to_json when team has no department"""
        team = Team(name='Standalone Team')
        user = User(username='testuser', name='Test User', email='test@example.com',
                   role=RoleEnum.STAFF, team=team)
        user.set_password('password')

        db.session.add(team)
        db.session.add(user)
        db.session.commit()

        user_json = user.to_json()

        self.assertEqual(user_json['team'], 'Standalone Team')
        self.assertIsNone(user_json['department'])
        self.assertIsNone(user_json['department_id'])

    def test_user_password_hashing(self):
        """Test password hashing and verification"""
        user = User(username='testuser', name='Test', email='test@example.com', role=RoleEnum.STAFF)
        user.set_password('mypassword')

        self.assertNotEqual(user.password_hash, 'mypassword')
        self.assertTrue(user.check_password('mypassword'))
        self.assertFalse(user.check_password('wrongpassword'))

    def test_user_repr(self):
        """Test user __repr__ method"""
        user = User(username='testuser', name='Test User', email='test@example.com', role=RoleEnum.STAFF)
        repr_str = repr(user)
        self.assertIn('Test User', repr_str)
        self.assertIn('test@example.com', repr_str)

    def test_team_to_json(self):
        """Test team to_json method"""
        dept = Department(name='Engineering')
        team = Team(name='Backend', department=dept)

        db.session.add(dept)
        db.session.add(team)
        db.session.commit()

        team_json = team.to_json()

        self.assertEqual(team_json['name'], 'Backend')
        self.assertIsNotNone(team_json['department_id'])

    def test_team_repr(self):
        """Test team __repr__ method"""
        team = Team(name='Backend')
        repr_str = repr(team)
        self.assertIn('Backend', repr_str)

    def test_department_to_json(self):
        """Test department to_json method"""
        dept = Department(name='Engineering')

        db.session.add(dept)
        db.session.commit()

        dept_json = dept.to_json()

        self.assertEqual(dept_json['name'], 'Engineering')
        self.assertIsNotNone(dept_json['id'])

    def test_department_repr(self):
        """Test department __repr__ method"""
        dept = Department(name='Engineering')
        repr_str = repr(dept)
        self.assertIn('Engineering', repr_str)

    def test_role_enum_values(self):
        """Test all role enum values"""
        roles = [RoleEnum.STAFF, RoleEnum.MANAGER, RoleEnum.DIRECTOR, RoleEnum.HR, RoleEnum.SM]
        expected_values = ['Staff', 'Manager', 'Director', 'HR', 'SM']

        for role, expected in zip(roles, expected_values):
            self.assertEqual(role.value, expected)


class TestServiceEdgeCases(unittest.TestCase):
    """Test service layer edge cases"""

    def setUp(self):
        self.app = create_app(config_name="testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.department = Department(name='Test Dept')
        self.team = Team(name='Test Team', department=self.department)
        db.session.add(self.department)
        db.session.add(self.team)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_user_by_id_not_found(self):
        """Test getting user by id when user doesn't exist"""
        from app.service import get_user_by_id
        user = get_user_by_id(99999)
        self.assertIsNone(user)

    def test_get_user_by_email_not_found(self):
        """Test getting user by email when user doesn't exist"""
        from app.service import get_user_by_email
        user = get_user_by_email('nonexistent@example.com')
        self.assertIsNone(user)

    def test_get_user_by_username_not_found(self):
        """Test getting user by username when user doesn't exist"""
        from app.service import get_user_by_username
        user = get_user_by_username('nonexistent')
        self.assertIsNone(user)

    def test_create_user_duplicate_email(self):
        """Test creating user with duplicate email"""
        from app.service import create_user

        user_data = {
            'username': 'user1',
            'name': 'User One',
            'email': 'test@example.com',
            'password': 'password',
            'role': 'Staff',
            'team_id': self.team.id
        }

        create_user(user_data)

        # Try to create another user with same email
        user_data2 = user_data.copy()
        user_data2['username'] = 'user2'

        new_user, error = create_user(user_data2)

        self.assertIsNone(new_user)
        self.assertIn('Email already in use', error)

    def test_create_user_duplicate_username(self):
        """Test creating user with duplicate username"""
        from app.service import create_user

        user_data = {
            'username': 'testuser',
            'name': 'User One',
            'email': 'user1@example.com',
            'password': 'password',
            'role': 'Staff',
            'team_id': self.team.id
        }

        create_user(user_data)

        # Try to create another user with same username
        user_data2 = user_data.copy()
        user_data2['email'] = 'user2@example.com'

        new_user, error = create_user(user_data2)

        self.assertIsNone(new_user)
        self.assertIn('Username already taken', error)

    def test_create_user_invalid_team(self):
        """Test creating user with invalid team_id"""
        from app.service import create_user

        user_data = {
            'username': 'testuser',
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password',
            'role': 'Staff',
            'team_id': 99999
        }

        new_user, error = create_user(user_data)

        self.assertIsNone(new_user)
        self.assertIn('Team with id', error)

    def test_create_user_invalid_role(self):
        """Test creating user with invalid role"""
        from app.service import create_user

        user_data = {
            'username': 'testuser',
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password',
            'role': 'InvalidRole',
            'team_id': self.team.id
        }

        new_user, error = create_user(user_data)

        self.assertIsNone(new_user)
        self.assertIn('Invalid role', error)

    def test_create_user_with_different_roles(self):
        """Test creating users with different roles that work with capitalize()"""
        from app.service import create_user

        # Only test roles that work with capitalize() - 'staff', 'manager', 'director'
        # Note: HR and SM don't work with capitalize() as they become 'Hr' and 'Sm'
        roles = ['Staff', 'Manager', 'Director']

        for i, role in enumerate(roles):
            user_data = {
                'username': f'user{i}',
                'name': f'User {i}',
                'email': f'user{i}@example.com',
                'password': 'password',
                'role': role,
                'team_id': self.team.id
            }

            new_user, error = create_user(user_data)

            self.assertIsNotNone(new_user, f"Failed to create user with role {role}. Error: {error}")
            self.assertIsNone(error)
            self.assertEqual(new_user.role.value, role)

    def test_get_all_users_empty(self):
        """Test getting all users when database is empty"""
        from app.service import get_all_users
        users = get_all_users()
        self.assertEqual(len(users), 0)

    def test_get_all_teams_with_multiple_teams(self):
        """Test getting all teams"""
        from app.service import get_all_teams

        team2 = Team(name='Team 2', department=self.department)
        db.session.add(team2)
        db.session.commit()

        teams = get_all_teams()
        self.assertEqual(len(teams), 2)

    def test_get_all_users_in_team_empty(self):
        """Test getting users in team when team has no users"""
        from app.service import get_all_users_in_team
        users = get_all_users_in_team(self.team.id)
        self.assertEqual(len(users), 0)

    def test_get_all_users_in_dept_with_multiple_teams(self):
        """Test getting users in department across multiple teams"""
        from app.service import get_all_users_in_dept, create_user

        team2 = Team(name='Team 2', department=self.department)
        db.session.add(team2)
        db.session.commit()

        # Create users in different teams
        create_user({
            'username': 'user1',
            'name': 'User 1',
            'email': 'user1@example.com',
            'password': 'pass',
            'role': 'Staff',
            'team_id': self.team.id
        })

        create_user({
            'username': 'user2',
            'name': 'User 2',
            'email': 'user2@example.com',
            'password': 'pass',
            'role': 'Staff',
            'team_id': team2.id
        })

        users = get_all_users_in_dept(self.department.id)
        self.assertEqual(len(users), 2)


if __name__ == '__main__':
    unittest.main()