# Database Setup Guide - Step by Step

## 📍 Step 4: Configure Database

### Where to Make Changes

You need to create a `.env` file in the **root directory** of your project (same folder as `run.py`).

### Step 4.1: Create the .env File

**On Windows:**

```bash
copy env_template.txt .env
```

**On Linux/Mac:**

```bash
cp env_template.txt .env
```

### Step 4.2: Edit the .env File

Open the `.env` file (it should be in the root directory: `C:\TeamProgessDashBord\.env`)

**Update these values:**

```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=root                    # ← Change this to YOUR MySQL password
DB_NAME=workflow_manager

# Flask Configuration
SECRET_KEY=your-secret-key-change-in-production    # ← You can keep this or change it
DATABASE_URL=mysql+pymysql://root:root@localhost/workflow_manager    # ← Change password here too
```

**Important:**

- Replace `root` in `DB_PASSWORD` with your actual MySQL password
- Replace `root` in `DATABASE_URL` with the same password
- Both passwords must match!

**Example if your MySQL password is "mypassword123":**

```env
DB_PASSWORD=mypassword123
DATABASE_URL=mysql+pymysql://root:mypassword123@localhost/workflow_manager
```

### Step 4.3: Create MySQL Database

Open MySQL command line or MySQL Workbench and run:

```sql
CREATE DATABASE workflow_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**Or using MySQL command line:**

```bash
mysql -u root -p
# Enter your password when prompted
CREATE DATABASE workflow_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

---

## 📍 Step 5: Initialize Database (Flask Migrations)

### Where to Run Commands

Open **PowerShell** or **Command Prompt** in your project root directory:

```
C:\TeamProgessDashBord>
```

Make sure your virtual environment is activated:

```bash
venv\Scripts\activate
```

### Step 5.1: Initialize Flask-Migrate

```bash
flask db init
```

**What this does:**

- Creates a `migrations/` folder in your project
- Sets up Flask-Migrate for database version control

**Expected output:**

```
Creating directory C:\TeamProgessDashBord\migrations ... done
Creating directory C:\TeamProgessDashBord\migrations\versions ... done
Generating C:\TeamProgessDashBord\migrations\alembic.ini ... done
...
```

### Step 5.2: Create Initial Migration

```bash
flask db migrate -m "Initial migration"
```

**What this does:**

- Scans your models (User, Task, Comment)
- Creates a migration file with SQL to create all tables

**Expected output:**

```
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'users'
INFO  [alembic.autogenerate.compare] Detected added table 'tasks'
INFO  [alembic.autogenerate.compare] Detected added table 'comments'
Generating C:\TeamProgessDashBord\migrations\versions\xxxx_initial_migration.py ... done
```

### Step 5.3: Apply Migration to Database

```bash
flask db upgrade
```

**What this does:**

- Executes the migration SQL on your MySQL database
- Creates all tables (users, tasks, comments) in the `workflow_manager` database

**Expected output:**

```
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> xxxx, Initial migration
```

**Verify it worked:**

```sql
USE workflow_manager;
SHOW TABLES;
```

You should see:

```
+---------------------------+
| Tables_in_workflow_manager |
+---------------------------+
| alembic_version           |
| comments                  |
| tasks                     |
| users                     |
+---------------------------+
```

---

## 📍 Step 6: Seed Sample Data (Optional)

### Where to Run

Same PowerShell/Command Prompt in project root with virtual environment activated.

### Run the Script

```bash
python seed_data.py
```

**What this does:**

- Creates 1 admin user and 4 developer users
- Creates 10 sample tasks
- Creates sample comments

**Expected output:**

```
Clearing existing data...
Creating admin user...
Admin created: admin@workflow.com / admin123
Creating developer users...
Developer created: dev1@workflow.com / dev123
...
Created 10 tasks
Created 4 comments

==================================================
Seed data created successfully!
==================================================
```

---

## 📍 Step 7: Run the Application

### Where to Run

Same PowerShell/Command Prompt in project root with virtual environment activated.

### Start the Server

```bash
python run.py
```

**Expected output:**

```
 * Serving Flask app 'run'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

### Access the Application

Open your browser and go to:

```
http://localhost:5000
```

You should see the login page!

---

## 🔧 Troubleshooting

### Error: "Can't connect to MySQL server"

**Problem:** MySQL is not running or wrong credentials

**Solution:**

1. Make sure MySQL service is running
2. Check your `.env` file has correct password
3. Test connection: `mysql -u root -p`

### Error: "Unknown database 'workflow_manager'"

**Problem:** Database doesn't exist

**Solution:**

```sql
CREATE DATABASE workflow_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Error: "No module named 'flask'"

**Problem:** Virtual environment not activated or dependencies not installed

**Solution:**

```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### Error: "Target database is not up to date"

**Problem:** Migration not applied

**Solution:**

```bash
flask db upgrade
```

### Error: "Alembic is not installed"

**Problem:** Flask-Migrate not installed

**Solution:**

```bash
pip install Flask-Migrate
```

---

## 📋 Quick Checklist

- [ ] Created `.env` file from `env_template.txt`
- [ ] Updated `DB_PASSWORD` in `.env` file
- [ ] Updated `DATABASE_URL` password in `.env` file
- [ ] Created MySQL database `workflow_manager`
- [ ] Ran `flask db init`
- [ ] Ran `flask db migrate -m "Initial migration"`
- [ ] Ran `flask db upgrade`
- [ ] Verified tables exist in MySQL
- [ ] Ran `python seed_data.py` (optional)
- [ ] Started application with `python run.py`
- [ ] Opened http://localhost:5000 in browser

---

## 🎯 Summary: Where to Make Changes

1. **`.env` file** (root directory) - Update database password
2. **MySQL** - Create database
3. **Command Line** (project root) - Run Flask commands
4. **Browser** - Access application at http://localhost:5000

All database-related changes happen in the `.env` file in the root directory!
