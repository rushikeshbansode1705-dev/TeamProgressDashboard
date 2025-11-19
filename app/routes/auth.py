from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and API endpoint"""
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return render_template('login.html')
    
    # POST request - API login
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        login_user(user, remember=True)
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict(),
            'redirect': url_for('dashboard.index')
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """Logout endpoint"""
    logout_user()
    if request.is_json:
        return jsonify({'success': True, 'message': 'Logged out successfully'})
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/api/logout')
@login_required
def api_logout():
    """API logout endpoint"""
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

