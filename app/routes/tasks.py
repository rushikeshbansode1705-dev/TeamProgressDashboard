from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import case
from app import db
from app.models.task import Task
from app.models.user import User
from app.models.comment import Comment
from datetime import datetime, date

tasks_bp = Blueprint('tasks', __name__)

def require_admin():
    """Check if current user is admin"""
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    return None

@tasks_bp.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Get all tasks (filtered by role) with pagination and sorting"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = max(1, min(per_page, 50))  # Clamp to prevent abuse
    sort_by = request.args.get('sort_by', 'created_at')
    sort_dir = request.args.get('sort_dir', 'desc').lower()
    sort_dir = 'desc' if sort_dir not in ('asc', 'desc') else sort_dir

    query = Task.query
    if current_user.role != 'admin':
        query = query.filter_by(assigned_to=current_user.id)
    else:
        assigned_to = request.args.get('assigned_to')
        if assigned_to:
            if assigned_to == 'unassigned':
                query = query.filter(Task.assigned_to.is_(None))
            elif assigned_to.isdigit():
                query = query.filter(Task.assigned_to == int(assigned_to))

    # Sorting logic
    if sort_by == 'due_date':
        nulls_last = Task.due_date.is_(None)
        if sort_dir == 'asc':
            query = query.order_by(nulls_last, Task.due_date.asc())
        else:
            query = query.order_by(nulls_last, Task.due_date.desc())
    elif sort_by == 'status':
        status_order = case(
            (
                (Task.status == 'Pending', 1),
                (Task.status == 'In Progress', 2),
                (Task.status == 'On Hold', 3),
                (Task.status == 'Completed', 4),
            ),
            else_=5
        )
        query = query.order_by(status_order.asc() if sort_dir == 'asc' else status_order.desc(), Task.updated_at.desc())
    else:
        # Default to created_at
        if sort_dir == 'asc':
            query = query.order_by(Task.created_at.asc())
        else:
            query = query.order_by(Task.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    tasks = pagination.items

    return jsonify({
        'success': True,
        'tasks': [task.to_dict() for task in tasks],
        'meta': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_pages': pagination.pages,
            'total_items': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })

@tasks_bp.route('/tasks', methods=['POST'])
@login_required
def create_task():
    """Create a new task (Admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    data = request.get_json()
    
    # Validation
    if not data.get('title'):
        return jsonify({'success': False, 'message': 'Title is required'}), 400
    
    # Parse dates
    start_date = None
    due_date = None
    if data.get('start_date'):
        try:
            start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
        except:
            return jsonify({'success': False, 'message': 'Invalid start_date format'}), 400
    
    if data.get('due_date'):
        try:
            due_date = datetime.strptime(data.get('due_date'), '%Y-%m-%d').date()
        except:
            return jsonify({'success': False, 'message': 'Invalid due_date format'}), 400
    
    # Create task
    task = Task(
        title=data.get('title'),
        description=data.get('description', ''),
        assigned_to=data.get('assigned_to'),
        priority=data.get('priority', 'Medium'),
        status=data.get('status', 'Pending'),
        start_date=start_date,
        due_date=due_date,
        created_by=current_user.id
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Task created successfully',
        'task': task.to_dict()
    }), 201

@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    """Update a task"""
    task = Task.query.get_or_404(task_id)
    
    # Check permissions
    if current_user.role != 'admin' and task.assigned_to != current_user.id:
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    data = request.get_json()
    
    # Update fields
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data.get('description', '')
    if 'assigned_to' in data:
        if current_user.role == 'admin':
            task.assigned_to = data['assigned_to']
        else:
            return jsonify({'success': False, 'message': 'Only admin can reassign tasks'}), 403
    if 'priority' in data:
        task.priority = data['priority']
    if 'status' in data:
        task.status = data['status']
    if 'start_date' in data:
        if data['start_date']:
            try:
                task.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            except:
                return jsonify({'success': False, 'message': 'Invalid start_date format'}), 400
        else:
            task.start_date = None
    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            except:
                return jsonify({'success': False, 'message': 'Invalid due_date format'}), 400
        else:
            task.due_date = None
    
    task.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Task updated successfully',
        'task': task.to_dict()
    })

@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """Delete a task (Admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Task deleted successfully'
    })

@tasks_bp.route('/tasks/<int:task_id>/status', methods=['PUT'])
@login_required
def update_task_status(task_id):
    """Update task status"""
    task = Task.query.get_or_404(task_id)
    
    # Check permissions
    if current_user.role != 'admin' and task.assigned_to != current_user.id:
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'success': False, 'message': 'Status is required'}), 400
    
    valid_statuses = ['Pending', 'In Progress', 'Completed', 'On Hold']
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    
    task.status = new_status
    task.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Status updated successfully',
        'task': task.to_dict()
    })

@tasks_bp.route('/tasks/<int:task_id>/comments', methods=['GET'])
@login_required
def get_comments(task_id):
    """Get comments for a task"""
    task = Task.query.get_or_404(task_id)
    
    # Check permissions
    if current_user.role != 'admin' and task.assigned_to != current_user.id:
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    comments = Comment.query.filter_by(task_id=task_id).order_by(Comment.created_at.asc()).all()
    
    return jsonify({
        'success': True,
        'comments': [comment.to_dict() for comment in comments]
    })

@tasks_bp.route('/tasks/<int:task_id>/comments', methods=['POST'])
@login_required
def add_comment(task_id):
    """Add a comment to a task"""
    task = Task.query.get_or_404(task_id)
    
    # Check permissions
    if current_user.role != 'admin' and task.assigned_to != current_user.id:
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    data = request.get_json()
    comment_text = data.get('comment_text', '').strip()
    
    if not comment_text:
        return jsonify({'success': False, 'message': 'Comment text is required'}), 400
    
    comment = Comment(
        task_id=task_id,
        user_id=current_user.id,
        comment_text=comment_text
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Comment added successfully',
        'comment': comment.to_dict()
    }), 201


@tasks_bp.route('/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """Get dashboard statistics"""
    if current_user.role == 'admin':
        total_tasks = Task.query.count()
        completed_tasks = Task.query.filter_by(status='Completed').count()
        pending_tasks = Task.query.filter_by(status='Pending').count()
        in_progress_tasks = Task.query.filter_by(status='In Progress').count()
        
        # Overdue tasks
        today = date.today()
        overdue_tasks = Task.query.filter(
            Task.due_date < today,
            Task.status != 'Completed'
        ).count()
    else:
        total_tasks = Task.query.filter_by(assigned_to=current_user.id).count()
        completed_tasks = Task.query.filter_by(assigned_to=current_user.id, status='Completed').count()
        pending_tasks = Task.query.filter_by(assigned_to=current_user.id, status='Pending').count()
        in_progress_tasks = Task.query.filter_by(assigned_to=current_user.id, status='In Progress').count()
        
        today = date.today()
        overdue_tasks = Task.query.filter(
            Task.assigned_to == current_user.id,
            Task.due_date < today,
            Task.status != 'Completed'
        ).count()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress_tasks,
            'overdue_tasks': overdue_tasks
        }
    })

