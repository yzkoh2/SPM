# app/routes.py
from flask import Blueprint, request, jsonify
from . import service

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = service.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_json()), 200

@user_bp.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    # Updated validation to be more specific
    if not all(key in data for key in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing username, email, or password'}), 400
    
    new_user = service.create_user(data)
    return jsonify(new_user.to_json()), 201

# --- ADDED LOGIN ROUTE ---
@user_bp.route('/user/login', methods=['POST'])
def login():
    """
    Authenticates a user and returns a JWT token upon success.
    """
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
    
    # 1. Ask the service to verify the user's credentials
    user = service.login_user(data)

    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # 2. If credentials are valid, generate a token for that user
    token = service.generate_token(user.id)
    
    return jsonify({
        'message': 'Login successful!',
        'token': token
    }), 200

