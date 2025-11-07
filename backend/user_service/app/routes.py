# app/routes.py
from flask import Blueprint, request, jsonify, current_app
from . import service
import jwt
from functools import wraps
from flask import current_app

user_bp = Blueprint('user_bp', __name__)

# --- Decorator for protected routes ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1].strip() # Bearer <token>
        
        if not token:
            return jsonify({'error': 'Token is missing!'}), 401

        try:
            # Decode the token using the app's SECRET_KEY
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = service.get_user_by_id(int(data['sub']))
            if not current_user:
                return jsonify({'error': 'User not found'}), 404
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

# --- Public Routes ---
@user_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = service.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_json()), 200

@user_bp.route('/user/create', methods=['POST'])
def create_user():
    data = request.get_json()
    if not all(key in data for key in ['username', 'name', 'email', 'password', 'role', 'team_id']):
        return jsonify({'error': 'Missing username, name, email, password, role, or team_id'}), 400

    # The service function now returns a user and an error message
    new_user, error_msg = service.create_user(data)

    if error_msg:
        # Return a 409 Conflict error if the user already exists
        return jsonify({'error': error_msg}), 409
    
    return jsonify(new_user.to_json()), 201

@user_bp.route('/user/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing email or password'}), 400

        token, id, name, role, username = service.login_user(data)

        if not token:
            return jsonify({'error': 'Invalid Login Credentials'}), 401

        return jsonify({'token': token, 'userID': id, 'name': name, 'role': role, 'username': username}), 200
    except Exception as e:
        print(f"An error has occured: {e}")
        return jsonify({'error': 'An unexpected error has occured. Please try again later.'}), 500

@user_bp.route('/user', methods=['GET'])
def get_all_users():
    """Get all users"""
    try:
        users = service.get_all_users()
        return jsonify([user.to_json() for user in users]), 200
    except Exception as e:
        print(f"Error getting all users: {e}")
        return jsonify({'error': str(e)}), 500

@user_bp.route('/user/teams', methods=['GET'])
def get_all_teams():
    """Get all teams"""
    try:
        teams = service.get_all_teams()
        return jsonify([team.to_json() for team in teams]), 200
    except Exception as e:
        print(f"Error getting all teams: {e}")
        return jsonify({'error': str(e)}), 500

@user_bp.route('/user/team/<int:team_id>', methods=['GET'])
def get_all_users_in_team(team_id):
    """Get all users in a specific team"""
    try:
        users = service.get_all_users_in_team(team_id)
        return jsonify([user.to_json() for user in users]), 200
    except Exception as e:
        print(f"Error getting users in team {team_id}: {e}")
        return jsonify({'error': str(e)}), 500

@user_bp.route('/user/departments', methods=['GET'])
def get_all_dept():
    """Get all departments"""
    try:
        depts = service.get_all_dept()
        return jsonify([dept.to_json() for dept in depts]), 200
    except Exception as e:
        print(f"Error getting all departments: {e}")
        return jsonify({'error': str(e)}), 500

@user_bp.route('/user/department/<int:dept_id>', methods=['GET'])
def get_all_users_in_dept(dept_id):
    """Get all users in a specific department"""
    try:
        users = service.get_all_users_in_dept(dept_id)
        return jsonify([user.to_json() for user in users]), 200
    except Exception as e:
        print(f"Error getting users in department {dept_id}: {e}")
        return jsonify({'error': str(e)}), 500

# --- Protected Routes ---
@user_bp.route('/user/verifyJWT', methods=['GET'])
@token_required
def verify_user(current_user):
    # The current_user is passed from the token_required decorator
    return jsonify(current_user.to_json())