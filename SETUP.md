# Quick Setup Guide

## Step-by-Step Installation

### 1. Install Python Dependencies

```bash
# Activate virtual environment first
pip install -r requirements.txt
```

### 2. Create MySQL Database

```sql
CREATE DATABASE workflow_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Configure Environment

```bash
# Copy the template
copy env_template.txt .env    # Windows
cp env_template.txt .env      # Linux/Mac

# Edit .env and update:
# - DB_PASSWORD (your MySQL password)
# - SECRET_KEY (generate a random string)
# - DATABASE_URL (update with your password)
```

### 4. Initialize Database

```bash
# Create migrations folder
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### 5. Seed Sample Data

```bash
python seed_data.py
```

### 6. Run Application

```bash
python run.py
```

Visit: http://localhost:5000

## Default Login Credentials

After running `seed_data.py`:

- **Admin**: admin@workflow.com / admin123
- **Developer 1**: dev1@workflow.com / dev123
- **Developer 2**: dev2@workflow.com / dev123
- **Developer 3**: dev3@workflow.com / dev123
- **Developer 4**: dev4@workflow.com / dev123

## Troubleshooting

### MySQL Connection Error

- Ensure MySQL is running: `mysql -u root -p`
- Check database exists: `SHOW DATABASES;`
- Verify credentials in `.env` file

### Module Not Found

- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Port Already in Use

- Change port in `run.py`: `app.run(debug=True, port=5001)`
