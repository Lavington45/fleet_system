# 🗄️ PostgreSQL Local Database Setup Guide

## Prerequisites
- PostgreSQL installed locally (https://www.postgresql.org/download/)
- pgAdmin (optional, for GUI management) or command line
- Your Flask app converted to PostgreSQL ✅ (already done)

---

## Step 1: Install PostgreSQL Locally

### Windows
1. Download from https://www.postgresql.org/download/windows/
2. Run the installer
3. Remember the password you set for the `postgres` superuser
4. Default port is 5432
5. Install pgAdmin (recommended for easier database management)

### Mac
```bash
brew install postgresql@15
brew services start postgresql@15
```

### Linux (Ubuntu)
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

---

## Step 2: Create the Database

### Option A: Using Command Line (psql)

**Windows Command Prompt or PowerShell:**
```bash
# Connect to PostgreSQL
psql -U postgres

# You'll be prompted for the password you set during installation
# Then run these commands:

CREATE DATABASE fleet_system;
\c fleet_system
```

**Mac/Linux Terminal:**
```bash
# Connect as postgres user
sudo -u postgres psql

# Then run:
CREATE DATABASE fleet_system;
\c fleet_system
```

### Option B: Using pgAdmin GUI
1. Open pgAdmin 4
2. Right-click "Databases" → "Create" → "Database"
3. Name: `fleet_system`
4. Click "Save"

---

## Step 3: Create Tables from schema.sql

### Windows PowerShell
```powershell
# Navigate to your project directory
cd C:\Users\user\OneDrive\Desktop\fleet_system

# Run the schema file
psql -U postgres -d fleet_system -f schema.sql
```

### Mac/Linux Terminal
```bash
cd ~/Desktop/fleet_system

# Run the schema file
sudo -u postgres psql -d fleet_system -f schema.sql
```

**Expected output:**
```
CREATE TABLE
CREATE TABLE
...
Database schema created successfully!
Demo data has been inserted.
```

---

## Step 4: Verify Database Created

```bash
# Connect to the database
psql -U postgres -d fleet_system

# List all tables
\dt

# You should see:
# - users
# - vehicles
# - assignments
# - trips
# - vehicle_history
# - incidents
# - emergency_alerts
# - notifications
# - reports
```

---

## Step 5: Set Up User Passwords

The schema.sql file creates demo users with placeholder passwords. Set them properly:

```bash
# From project directory in Python terminal
python setup_users.py
```

Set these environment variables before running:
```bash
# Windows (PowerShell)
$env:DB_HOST = "localhost"
$env:DB_USER = "postgres"
$env:DB_PASSWORD = "your_postgres_password"
$env:DB_NAME = "fleet_system"

python setup_users.py
```

```bash
# Mac/Linux
export DB_HOST=localhost
export DB_USER=postgres
export DB_PASSWORD=your_postgres_password
export DB_NAME=fleet_system

python setup_users.py
```

**Expected output:**
```
✅ Users updated successfully!
Admin: admin / admin123
Driver: driver1 / driver123
Driver: driver2 / driver123
```

---

## Step 6: Test Local Database Connection

In your project directory, create a test script `test_db.py`:

```python
import psycopg2
import os

try:
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'your_password'),
        dbname=os.environ.get('DB_NAME', 'fleet_system')
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users;")
    count = cursor.fetchone()[0]
    print(f"✅ Connection successful! Found {count} users.")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Run it:
```bash
python test_db.py
```

---

## Step 7: Set Environment Variables for Local Development

### Windows (PowerShell - Permanent)
Create a file called `set_env.ps1`:
```powershell
$env:DB_HOST = "localhost"
$env:DB_USER = "postgres"
$env:DB_PASSWORD = "your_postgres_password"
$env:DB_NAME = "fleet_system"
$env:SECRET_KEY = "your_dev_secret_key_change_later"
```

Run it before starting your app:
```powershell
.\set_env.ps1
python app.py
```

### Mac/Linux (Terminal)
Create a `.env` file in your project root:
```
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_NAME=fleet_system
SECRET_KEY=your_dev_secret_key_change_later
```

Then install python-dotenv support:
```bash
pip install python-dotenv
```

Update your `app.py` to load `.env`:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Step 8: Run Your Flask App

```bash
# Set environment variables (if not using .env)
# Windows:
$env:DB_HOST = "localhost"
$env:DB_USER = "postgres"
$env:DB_PASSWORD = "your_postgres_password"
$env:DB_NAME = "fleet_system"

# Start the app
python app.py
```

Visit: http://localhost:5000

Login with:
- **Admin**: admin / admin123
- **Driver**: driver1 / driver123

---

## Troubleshooting

### ❌ "Connection refused" error
- Verify PostgreSQL is running: `pg_isrunning` or check Services
- Verify port 5432 is accessible
- Check DB_HOST, DB_USER, DB_PASSWORD environment variables

### ❌ "Database fleet_system does not exist"
```bash
psql -U postgres
CREATE DATABASE fleet_system;
\c fleet_system
# Then re-run schema.sql
```

### ❌ "relation users does not exist"
- Tables weren't created. Re-run: `psql -U postgres -d fleet_system -f schema.sql`

### ❌ "permission denied for schema public"
```bash
psql -U postgres -d fleet_system
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;
```

---

## 🚀 Next Steps

After local testing works:

1. **Deploy to Render** (production):
   - Create PostgreSQL database on Render
   - Set `DATABASE_URL` environment variable
   - Deploy your Flask app

2. **Initialize Render database**:
   - Use Render's PostgreSQL shell or pgAdmin
   - Run the schema.sql file
   - Update passwords

3. **Set Render environment variables**:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/fleet_system
   SECRET_KEY=your_production_secret_key
   ```

---

## Useful PostgreSQL Commands

```bash
# Connect to database
psql -U postgres -d fleet_system

# List all tables
\dt

# Describe a table
\d users

# View data
SELECT * FROM users;
SELECT * FROM vehicles;

# Exit
\q

# Backup database
pg_dump -U postgres fleet_system > backup.sql

# Restore database
psql -U postgres fleet_system < backup.sql
```

---

**You're all set!** Your local PostgreSQL database is ready for FleetGuard. 🎉
