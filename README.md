# WorkFlow Manager

A complete Work Allocation Dashboard system built with Python Flask and MySQL. This application allows administrators to manage tasks and assign them to developers, while developers can view their assigned tasks, update status, and add comments.

## 🚀 Features

### Admin Features

- Create and manage developer accounts
- Add, edit, and delete tasks
- Assign/reassign tasks to developers
- Change task status
- View comprehensive dashboard analytics
- Manage all tasks across the system

### Developer Features

- View assigned tasks
- Update task status
- Add comments to tasks
- View deadlines and task details
- Track overdue tasks

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **Database**: MySQL
- **Frontend**: HTML + TailwindCSS + Vanilla JavaScript
- **Templates**: Jinja2
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Migrations**: Flask-Migrate

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- MySQL Server 5.7 or higher
- pip (Python package manager)
- virtualenv (recommended)

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd TeamProgessDashBord
```

### 2. Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Database

1. Create a MySQL database:

```sql
CREATE DATABASE workflow_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Copy the environment file:

```bash
# On Windows
copy .env.example .env

# On Linux/Mac
cp .env.example .env
```

3. Edit `.env` file with your database credentials:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=workflow_manager

SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=mysql+pymysql://root:your_password_here@localhost/workflow_manager
```

### 5. Initialize Database

```bash
# Initialize Flask-Migrate
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### 6. Seed Sample Data (Optional)

To populate the database with sample data for testing:

```bash
python seed_data.py
```

This will create:

- 1 admin user: `admin@workflow.com` / `admin123`
- 4 developer users: `dev1@workflow.com` through `dev4@workflow.com` / `dev123`
- 10 sample tasks with various statuses
- Sample comments

## 🚀 Running the Application

### Development Mode

```bash
python run.py
```

The application will be available at `http://localhost:5000`

### Production Mode

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## 📁 Project Structure

```
TeamProgessDashBord/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/              # Database models
│   │   ├── user.py
│   │   ├── task.py
│   │   └── comment.py
│   ├── routes/              # Route handlers
│   │   ├── auth.py
│   │   ├── tasks.py
│   │   └── dashboard.py
│   ├── static/              # Static files
│   │   ├── css/
│   │   └── js/
│   │       └── dashboard.js
│   └── templates/           # HTML templates
│       ├── login.html
│       └── dashboard.html
├── migrations/              # Database migrations
├── config.py               # Configuration
├── run.py                  # Application entry point
├── seed_data.py            # Seed data script
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🔌 API Endpoints

### Authentication

- `POST /login` - User login
- `GET /api/logout` - User logout

### Tasks

- `GET /api/tasks` - Get all tasks (filtered by role)
- `POST /api/tasks` - Create new task (Admin only)
- `PUT /api/tasks/<id>` - Update task
- `DELETE /api/tasks/<id>` - Delete task (Admin only)
- `PUT /api/tasks/<id>/status` - Update task status

### Comments

- `GET /api/tasks/<id>/comments` - Get task comments
- `POST /api/tasks/<id>/comments` - Add comment to task

### Dashboard

- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/users` - Get all developers (Admin only)

All API endpoints return JSON responses.

## 🎨 UI Features

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Updates**: Tasks and stats update automatically
- **Color-coded Priorities**: Visual indicators for task priority (Low/Medium/High)
- **Status Badges**: Color-coded status indicators
- **Pagination & Sorting**: Sort by due date or status, paginate task list
- **Developer Filter**: Admins can filter tasks by assigned developer or unassigned
- **Overdue Highlighting**: Overdue tasks are highlighted in red
- **Modal Dialogs**: Edit tasks in a popup modal
- **Dropdown Menus**: Easy status and assignment changes

## 🔐 Security Features

- Password hashing using Werkzeug
- Session-based authentication with Flask-Login
- Role-based access control
- SQL injection protection via SQLAlchemy ORM
- CSRF protection (can be added with Flask-WTF)

## 🧪 Testing

### Manual Testing

1. Login as admin and create tasks
2. Assign tasks to developers
3. Login as developer and update task status
4. Add comments to tasks
5. Test overdue task highlighting

### Sample Credentials

After running `seed_data.py`:

**Admin:**

- Email: `admin@workflow.com`
- Password: `admin123`

**Developers:**

- Email: `dev1@workflow.com` through `dev4@workflow.com`
- Password: `dev123`

## 🐛 Troubleshooting

### Database Connection Issues

- Ensure MySQL server is running
- Verify database credentials in `.env` file
- Check if database exists: `SHOW DATABASES;`
- Verify user has proper permissions

### Migration Issues

```bash
# Reset migrations (WARNING: This will delete all data)
flask db downgrade base
flask db upgrade
```

### Port Already in Use

Change the port in `run.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

## 📝 Database Schema

### Users Table

- `id` (Primary Key)
- `name`
- `email` (Unique)
- `password_hash`
- `role` (admin/developer)
- `created_at`

### Tasks Table

- `id` (Primary Key)
- `title`
- `description`
- `assigned_to` (Foreign Key → users.id)
- `priority` (Low/Medium/High)
- `status` (Pending/In Progress/Completed/On Hold)
- `start_date`
- `due_date`
- `created_by` (Foreign Key → users.id)
- `created_at`
- `updated_at`

### Comments Table

- `id` (Primary Key)
- `task_id` (Foreign Key → tasks.id)
- `user_id` (Foreign Key → users.id)
- `comment_text`
- `created_at`

## 🔄 Database Migrations

When you modify models, create a new migration:

```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

## 📄 License

This project is open source and available under the MIT License.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on the repository.

---

**Built with ❤️ using Flask and MySQL**
