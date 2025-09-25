import unittest
import os
import sys
from unittest import mock
import jwt

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, User
from app.service import hash_password

class UserServiceTestCase(unittest.TestCase):
    """This class represents the user service test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client

        # sample data
        self.user_data = {
            'username': 'testuser',
            'name': 'Test User',
            'password': 'testpassword',
            'email': 'test@example.com',
            'role': 'staff'
        }
        self.user_data_2 = {
            'username': 'testuser2',
            'name': 'Test User 2',
            'password': 'testpassword2',
            'email': 'test2@example.com',
            'role': 'admin'
        }

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

    def test_user_creation(self):
        """Test API can create a user (POST request)"""
        with self.app.app_context():
            res = self.client().post('/user/create', json=self.user_data)
            self.assertEqual(res.status_code, 201)
            data = res.get_json()
            self.assertEqual(data['username'], self.user_data['username'])

    def test_user_creation_with_existing_email(self):
        """Test API cannot create a user with an existing email"""
        with self.app.app_context():
            # Create a user first
            self.client().post('/user/create', json=self.user_data)
            # Try to create another user with the same email
            res = self.client().post('/user/create', json={
                'username': 'newuser',
                'name': 'New User',
                'password': 'newpassword',
                'email': self.user_data['email']
            })
            self.assertEqual(res.status_code, 409)
            data = res.get_json()
            self.assertEqual(data['error'], 'Email already in use.')

    def test_user_creation_with_existing_username(self):
        """Test API cannot create a user with an existing username"""
        with self.app.app_context():
            # Create a user first
            self.client().post('/user/create', json=self.user_data)
            # Try to create another user with the same username
            res = self.client().post('/user/create', json={
                'username': self.user_data['username'],
                'name': 'Another User',
                'password': 'anotherpassword',
                'email': 'another@example.com'
            })
            self.assertEqual(res.status_code, 409)
            data = res.get_json()
            self.assertEqual(data['error'], 'Username already taken.')

    def test_user_creation_with_missing_fields(self):
        """Test API cannot create a user with missing fields"""
        with self.app.app_context():
            res = self.client().post('/user/create', json={
                'username': 'testuser'
                # Missing name, email, password
            })
            self.assertEqual(res.status_code, 400)
            data = res.get_json()
            self.assertEqual(data['error'], 'Missing username, name, email, or password')

    def test_get_user_by_id(self):
        """Test API can get a single user by id."""
        with self.app.app_context():
            # Create a user first
            res_create = self.client().post('/user/create', json=self.user_data)
            user_id = res_create.get_json()['id']
            # Retrieve the user
            res_get = self.client().get(f'/user/{user_id}')
            self.assertEqual(res_get.status_code, 200)
            data = res_get.get_json()
            self.assertEqual(data['id'], user_id)

    def test_get_user_by_id_not_found(self):
        """Test API returns 404 for a non-existent user."""
        with self.app.app_context():
            res = self.client().get('/user/999')
            self.assertEqual(res.status_code, 404)
            data = res.get_json()
            self.assertEqual(data['error'], 'User not found')

    def test_password_hashing(self):
        """Test password hashing and checking."""
        with self.app.app_context():
            from app.service import hash_password, check_password
            hashed_password = hash_password('password123')
            self.assertTrue(check_password('password123', hashed_password.decode('utf-8')))
            self.assertFalse(check_password('wrongpassword', hashed_password.decode('utf-8')))

    def test_user_login(self):
        """Test user can login (POST request)"""
        with self.app.app_context():
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

    def test_user_login_with_wrong_password(self):
        """Test user cannot login with a wrong password"""
        with self.app.app_context():
            # Create a user first
            self.client().post('/user/create', json=self.user_data)
            # Attempt to login with the wrong password
            res = self.client().post('/user/login', json={
                'email': self.user_data['email'],
                'password': 'wrongpassword'
            })
            self.assertEqual(res.status_code, 401)
            data = res.get_json()
            self.assertEqual(data['error'], 'Invalid Login Credentials')

    def test_user_login_nonexistent_user(self):
        """Test login for a non-existent user"""
        with self.app.app_context():
            res = self.client().post('/user/login', json={
                'email': 'nonexistent@example.com',
                'password': 'password'
            })
            self.assertEqual(res.status_code, 401)
            data = res.get_json()
            self.assertEqual(data['error'], 'Invalid Login Credentials')

    def test_user_login_with_missing_fields(self):
        """Test user login with missing email or password"""
        with self.app.app_context():
            res = self.client().post('/user/login', json={'email': 'test@example.com'})
            self.assertEqual(res.status_code, 400)
            data = res.get_json()
            self.assertEqual(data['error'], 'Missing email or password')

    def test_user_login_unexpected_error(self):
        """Test user login with an unexpected error."""
        with self.app.app_context():
            # Mock the service function to raise an exception
            with unittest.mock.patch('app.routes.service.login_user', side_effect=Exception("Unexpected error")):
                res = self.client().post('/user/login', json={
                    'email': 'test@example.com',
                    'password': 'password'
                })
                self.assertEqual(res.status_code, 500)
                data = res.get_json()
                self.assertEqual(data['error'], 'An unexpected error has occured. Please try again later.')

    def test_jwt_generation_and_verification(self):
        """Test JWT generation and verification."""
        with self.app.app_context():
            # Create a user and get their ID
            res_create = self.client().post('/user/create', json=self.user_data)
            user_id = res_create.get_json()['id']

            # Log in to get a token
            res_login = self.client().post('/user/login', json={
                'email': self.user_data['email'],
                'password': self.user_data['password']
            })
            token = res_login.get_json()['token']

            # Verify the token
            res_verify = self.client().get('/user/verifyJWT', headers={
                'Authorization': f'Bearer {token}'
            })
            self.assertEqual(res_verify.status_code, 200)
            data = res_verify.get_json()
            self.assertEqual(data['id'], user_id)

    def test_verify_jwt_with_missing_token(self):
        """Test verifying JWT with a missing token."""
        with self.app.app_context():
            res = self.client().get('/user/verifyJWT')
            self.assertEqual(res.status_code, 401)
            data = res.get_json()
            self.assertEqual(data['error'], 'Token is missing!')

    def test_verify_jwt_with_expired_token(self):
        """Test verifying JWT with an expired token."""
        with self.app.app_context():
            # Generate an expired token
            from app.service import generate_token
            expired_token = generate_token(1)  # Assuming user ID 1
            # To make it expired, we need to manipulate the time.
            # Since we can't do that easily, we'll mock the jwt.decode function.
            # For simplicity, we'll assume the token has a very short lifespan
            # and just wait for it to expire.
            # A better approach would be to mock the datetime.datetime.utcnow function
            # when generating the token.
            # For this test, we will assume the token is expired.
            # We will patch the `jwt.decode` to raise `ExpiredSignatureError`.
            with unittest.mock.patch('jwt.decode', side_effect=jwt.ExpiredSignatureError):
                res = self.client().get('/user/verifyJWT', headers={
                    'Authorization': f'Bearer {expired_token}'
                })
                self.assertEqual(res.status_code, 401)
                data = res.get_json()
                self.assertEqual(data['error'], 'Token has expired!')

    def test_verify_jwt_with_invalid_token(self):
        """Test verifying JWT with an invalid token."""
        with self.app.app_context():
            res = self.client().get('/user/verifyJWT', headers={
                'Authorization': 'Bearer invalidtoken'
            })
            self.assertEqual(res.status_code, 401)
            data = res.get_json()
            self.assertEqual(data['error'], 'Token is invalid!')

    def test_verify_jwt_with_nonexistent_user(self):
        """Test verifying JWT with a token for a nonexistent user."""
        with self.app.app_context():
            from app.service import generate_token
            # Generate a token for a user ID that doesn't exist
            token = generate_token(999)
            res = self.client().get('/user/verifyJWT', headers={
                'Authorization': f'Bearer {token}'
            })
            self.assertEqual(res.status_code, 404)
            data = res.get_json()
            self.assertEqual(data['error'], 'User not found')

if __name__ == "__main__":
    unittest.main()