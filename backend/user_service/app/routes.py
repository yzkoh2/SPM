# app/routes.py
from flask import Blueprint, request, jsonify
from . import service

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = service.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_json()), 200

@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or not 'username' in data or not 'email' in data:
        return jsonify({'error': 'Missing data'}), 400
    
    new_user = service.create_user(data)
    return jsonify(new_user.to_json()), 201