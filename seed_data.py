"""
Seed data script for development.
Run this script to populate the database with sample data.
Usage: python seed_data.py
"""

from app import create_app, db
from app.models.user import User
from app.models.task import Task
from app.models.comment import Comment
from datetime import datetime, date, timedelta

def seed_data():
    app = create_app()
    
    with app.app_context():
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("Clearing existing data...")
        Comment.query.delete()
        Task.query.delete()
        User.query.delete()
        db.session.commit()
        
        # Create Admin User
        print("Creating admin user...")
        admin = User(
            name='Admin User',
            email='admin@workflow.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print(f"Admin created: {admin.email} / admin123")
        
        # Create Developer Users
        print("Creating developer users...")
        developers = []
        dev_names = ['Shubham Khale', 'Khushi', 'Tanya Singh', 'Shubham Chaudari', 'Pratik P']
        for i, name in enumerate(dev_names):
            dev = User(
                name=name,
                email=f'{name.replace(" ", "").lower()}@workflow.com',
                role='developer'
            )
            dev.set_password(f'{name.replace(" ", "").lower()}dev123')
            developers.append(dev)
            db.session.add(dev)
            print(f"Developer created: {dev.email} / {name.replace(" ", "").lower()}dev123")
        
        db.session.commit()
        
        # Create Tasks
        print("Creating tasks...")
        today = date.today()
        
        tasks_data = [
            {
                'title': 'Implement User Authentication',
                'description': 'Set up login and registration system with JWT tokens',
                'assigned_to': developers[0].id,
                'priority': 'High',
                'status': 'In Progress',
                'start_date': today - timedelta(days=5),
                'due_date': today + timedelta(days=5),
                'created_by': admin.id
            },
            {
                'title': 'Design Dashboard UI',
                'description': 'Create responsive dashboard with task management interface',
                'assigned_to': developers[1].id,
                'priority': 'High',
                'status': 'Completed',
                'start_date': today - timedelta(days=10),
                'due_date': today - timedelta(days=2),
                'created_by': admin.id
            },
            # {
            #     'title': 'Database Schema Design',
            #     'description': 'Design and implement database tables for users, tasks, and comments',
            #     'assigned_to': developers[0].id,
            #     'priority': 'Medium',
            #     'status': 'Completed',
            #     'start_date': today - timedelta(days=15),
            #     'due_date': today - timedelta(days=5),
            #     'created_by': admin.id
            # },
            # {
            #     'title': 'API Endpoint Development',
            #     'description': 'Create RESTful API endpoints for task management',
            #     'assigned_to': developers[2].id,
            #     'priority': 'High',
            #     'status': 'In Progress',
            #     'start_date': today - timedelta(days=3),
            #     'due_date': today + timedelta(days=7),
            #     'created_by': admin.id
            # },
            # {
            #     'title': 'Write Unit Tests',
            #     'description': 'Create comprehensive unit tests for all modules',
            #     'assigned_to': developers[3].id,
            #     'priority': 'Medium',
            #     'status': 'Pending',
            #     'start_date': today,
            #     'due_date': today + timedelta(days=14),
            #     'created_by': admin.id
            # },
            # {
            #     'title': 'Code Review and Refactoring',
            #     'description': 'Review codebase and refactor for better performance',
            #     'assigned_to': developers[1].id,
            #     'priority': 'Low',
            #     'status': 'Pending',
            #     'start_date': today + timedelta(days=2),
            #     'due_date': today + timedelta(days=10),
            #     'created_by': admin.id
            # },
            # {
            #     'title': 'Documentation Update',
            #     'description': 'Update project documentation and API docs',
            #     'assigned_to': developers[2].id,
            #     'priority': 'Low',
            #     'status': 'On Hold',
            #     'start_date': today - timedelta(days=1),
            #     'due_date': today + timedelta(days=5),
            #     'created_by': admin.id
            # },
            # {
            #     'title': 'Bug Fix: Login Issue',
            #     'description': 'Fix authentication bug reported by users',
            #     'assigned_to': developers[0].id,
            #     'priority': 'High',
            #     'status': 'In Progress',
            #     'start_date': today - timedelta(days=2),
            #     'due_date': today + timedelta(days=1),
            #     'created_by': admin.id
            # },
            # {
            #     'title': 'Performance Optimization',
            #     'description': 'Optimize database queries and improve page load times',
            #     'assigned_to': developers[3].id,
            #     'priority': 'Medium',
            #     'status': 'Pending',
            #     'start_date': today + timedelta(days=5),
            #     'due_date': today + timedelta(days=20),
            #     'created_by': admin.id
            # },
            # {
            #     'title': 'Overdue Task Example',
            #     'description': 'This task is overdue to demonstrate the overdue feature',
            #     'assigned_to': developers[1].id,
            #     'priority': 'High',
            #     'status': 'Pending',
            #     'start_date': today - timedelta(days=10),
            #     'due_date': today - timedelta(days=2),
            #     'created_by': admin.id
            # }
        ]
        
        for task_data in tasks_data:
            task = Task(**task_data)
            db.session.add(task)
        
        db.session.commit()
        print(f"Created {len(tasks_data)} tasks")
        
        # Create Comments
        print("Creating comments...")
        tasks = Task.query.all()
        
        if tasks:
            comments_data = [
                {
                    'task_id': tasks[0].id,
                    'user_id': developers[0].id,
                    'comment_text': 'Started working on authentication module. Making good progress.'
                },
                {
                    'task_id': tasks[0].id,
                    'user_id': admin.id,
                    'comment_text': 'Great! Let me know if you need any help.'
                },
                {
                    'task_id': tasks[1].id,
                    'user_id': developers[1].id,
                    'comment_text': 'Dashboard UI completed and tested. Ready for review.'
                }
                # ,{
                #     'task_id': tasks[3].id,
                #     'user_id': developers[2].id,
                #     'comment_text': 'API endpoints are working. Need to add error handling.'
                # }
            ]
            
            for comment_data in comments_data:
                comment = Comment(**comment_data)
                db.session.add(comment)
            
            db.session.commit()
            print(f"Created {len(comments_data)} comments")
        
        print("\n" + "="*50)
        print("Seed data created successfully!")
        print("="*50)
        print("\nLogin Credentials:")
        print("Admin: admin@workflow.com / admin123")
        print("Developers: dev1@workflow.com / dev123")
        print("            dev2@workflow.com / dev123")
        print("            dev3@workflow.com / dev123")
        print("            dev4@workflow.com / dev123")
        print("="*50)

if __name__ == '__main__':
    seed_data()

