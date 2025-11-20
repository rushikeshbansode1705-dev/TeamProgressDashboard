from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
import re

users_bp = Blueprint('users', __name__)

def require_admin():
    """Check if current user is admin"""
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    return None

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@users_bp.route('/users', methods=['GET'])
@login_required
def get_all_users():
    """Get all users (Admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({
        'success': True,
        'users': [user.to_dict() for user in users]
    })

@users_bp.route('/users', methods=['POST'])
@login_required
def create_user():
    """Create a new user (Admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    data = request.get_json()
    
    # Validation
    if not data.get('name') or not data.get('name').strip():
        return jsonify({'success': False, 'message': 'Name is required'}), 400
    
    if not data.get('email') or not data.get('email').strip():
        return jsonify({'success': False, 'message': 'Email is required'}), 400
    
    if not validate_email(data.get('email')):
        return jsonify({'success': False, 'message': 'Invalid email format'}), 400
    
    if not data.get('password') or len(data.get('password', '')) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
    
    role = data.get('role', 'developer').lower()
    if role not in ['admin', 'developer']:
        return jsonify({'success': False, 'message': 'Invalid role. Must be admin or developer'}), 400
    
    # Check if email already exists
    existing_user = User.query.filter_by(email=data.get('email').strip().lower()).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'Email already exists'}), 400
    
    # Create user
    user = User(
        name=data.get('name').strip(),
        email=data.get('email').strip().lower(),
        role=role
    )
    user.set_password(data.get('password'))
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'User created successfully',
        'user': user.to_dict()
    }), 201

@users_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """Update a user (Admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # Prevent admin from deleting the last admin
    if user.role == 'admin' and data.get('role') == 'developer':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            return jsonify({'success': False, 'message': 'Cannot change role. At least one admin is required'}), 400
    
    # Update fields
    if 'name' in data and data['name'].strip():
        user.name = data['name'].strip()
    
    if 'email' in data:
        new_email = data['email'].strip().lower()
        if not validate_email(new_email):
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
        
        # Check if email is already taken by another user
        existing_user = User.query.filter_by(email=new_email).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'success': False, 'message': 'Email already exists'}), 400
        
        user.email = new_email
    
    if 'role' in data:
        new_role = data['role'].lower()
        if new_role not in ['admin', 'developer']:
            return jsonify({'success': False, 'message': 'Invalid role'}), 400
        
        # Prevent removing last admin
        if user.role == 'admin' and new_role == 'developer':
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                return jsonify({'success': False, 'message': 'Cannot change role. At least one admin is required'}), 400
        
        user.role = new_role
    
    if 'password' in data and data.get('password'):
        if len(data['password']) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'User updated successfully',
        'user': user.to_dict()
    })

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    """Delete a user (Admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == current_user.id: 
        return jsonify({'success': False, 'message': 'Cannot delete your own account'}), 400
    
    # Prevent deleting the last admin
    if user.role == 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            return jsonify({'success': False, 'message': 'Cannot delete the last admin'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'User deleted successfully'
    })
