# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager
# from flask_migrate import Migrate
# from config import Config
# import os

# db = SQLAlchemy()
# login_manager = LoginManager()
# migrate = Migrate()

# def create_app(config_class=Config):
#     app = Flask(__name__)
#     app.config.from_object(config_class)
    
#     # Initialize extensions
#     db.init_app(app)
#     login_manager.init_app(app)
#     migrate.init_app(app, db)
    
#     # Configure Flask-Login
#     login_manager.login_view = 'auth.login'
#     login_manager.login_message = 'Please log in to access this page.'
#     login_manager.login_message_category = 'info'
    
#     @login_manager.user_loader
#     def load_user(user_id):
#         from app.models.user import User
#         return User.query.get(int(user_id))
    
#     # Register blueprints
#     from app.routes.auth import auth_bp
#     from app.routes.tasks import tasks_bp
#     from app.routes.dashboard import dashboard_bp
    
#     app.register_blueprint(auth_bp, url_prefix='/')
#     app.register_blueprint(tasks_bp, url_prefix='/api')
#     app.register_blueprint(dashboard_bp, url_prefix='/')
    
#     # Create tables
#     with app.app_context():
#         db.create_all()
    
#     return app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # -----------------------------
    # Initialize Extensions
    # -----------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # -----------------------------
    # Configure Login Manager
    # -----------------------------
    login_manager.login_view = 'auth.login'          # login page route
    login_manager.login_message = 'Please log in.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        """Load logged-in user from DB."""
        from app.models.user import User
        return User.query.get(int(user_id))

    # -----------------------------
    # Register Blueprints
    # -----------------------------
    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.users import users_bp

    app.register_blueprint(auth_bp)                     # /login, /register...
    app.register_blueprint(tasks_bp, url_prefix='/api') # /api/tasks/...
    app.register_blueprint(dashboard_bp)                # /dashboard...
    app.register_blueprint(users_bp, url_prefix='/api') # /api/users/...

    # -----------------------------
    # Create Database Tables
    # (ONLY for first time — after that use flask db migrate)
    # -----------------------------
    with app.app_context():
        if app.config.get("CREATE_TABLES", True):
            db.create_all()

    return app
