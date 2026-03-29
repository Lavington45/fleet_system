# 📥 Installation & Setup Guide

## System Requirements
- Windows 10+ / Mac / Linux
- Python 3.8 or higher
- MySQL 5.7 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection

---

## Step-by-Step Installation

### STEP 1️⃣: Install Python & MySQL

**Windows:**
1. Download Python from https://www.python.org/downloads/
2. Run installer and CHECK "Add Python to PATH"
3. Download MySQL from https://dev.mysql.com/downloads/mysql/
4. Run installer and complete MySQL setup

**Mac:**
```bash
brew install python3
brew install mysql
```

**Linux (Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip mysql-server
```

---

### STEP 2️⃣: Extract Project Files

Extract the `fleet_system.zip` to a folder:
```
C:\Users\YourName\Desktop\fleet_system\
```

Or via terminal:
```bash
cd Desktop
unzip fleet_system.zip
cd fleet_system
```

---

### STEP 3️⃣: Setup Python Environment

**Windows:**
```bash
# Navigate to project folder
cd fleet_system

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) in your terminal
```

**Mac/Linux:**
```bash
cd fleet_system
python3 -m venv venv
source venv/bin/activate
# You should see (venv) in your terminal
```

---

### STEP 4️⃣: Install Python Packages

```bash
# Make sure you're in the project folder with (venv) active
pip install -r requirements.txt

# You should see packages being installed:
# - Flask
# - mysql-connector-python
# - Werkzeug
# - cryptography
# - requests
```

---

### STEP 5️⃣: Setup MySQL Database

#### Option A: Using Command Line (Recommended)

**Windows:**
```bash
# Open Command Prompt as
Administrator
mysql -u root -p fleet_system < database_schema.sql

# It will ask for your MySQL password (if you set one)
# Press Enter if you didn't set a password
```

**Mac/Linux:**
```bash
mysql -u root -p fleet_system < database_schema.sql
# Enter your MySQL root password when prompted
```

#### Option B: Using MySQL GUI

1. Open MySQL Workbench
2. File → New Query Tab
3. Copy contents of `database_schema.sql`
4. Paste and click ⚡ Execute
5. Should show: "Schema created successfully"

---

### STEP 6️⃣: Update Database Password (If Set)

If your MySQL has a password, edit `app.py`:

```python
# Find this section (around line 28):
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",          # ← Add your password here
    database="fleet_system"
)
```

Change `password=""` to `password="your_mysql_password"`

---

### STEP 7️⃣: Verify Installation

```bash
# Test Python packages
python -c "import flask; print('✓ Flask installed')"
python -c "import mysql; print('✓ MySQL driver installed')"

# Test MySQL connection
mysql -u root -p -e "USE fleet_system; SHOW TABLES;"
# Should show: 11 tables
```

---

## 🚀 Running the System

### Terminal Setup (Windows)

Open **3 separate Command Prompt windows** in the fleet_system folder:

**Window 1: Activate venv**
```bash
venv\Scripts\activate
```

**Window 2: Activate venv**
```bash
venv\Scripts\activate
```

**Window 3: Activate venv**
```bash
venv\Scripts\activate
```

---

### START THE APPLICATION

**Window 1 - Start Backend Server:**
```bash
(venv) C:\...\fleet_system> python app.py
# Should show: * Running on http://127.0.0.1:5000
```

**Window 2 - Start Vehicle Simulator:**
```bash
(venv) C:\...\fleet_system> python simulator.py
# Should show: Starting fleet simulator with 20 vehicles
```

**Window 3 - Keep for commands** (optional)

---

## 🌐 Accessing the Application

Open your web browser and go to:

### **Admin Dashboard**
```
http://127.0.0.1:5000/admin
Username: admin
Password: admin123
```

### **Driver Dashboard**
```
http://127.0.0.1:5000/driver
Username: driver1
Password: driver123
```

### **Login Page**
```
http://127.0.0.1:5000
```

---

## ✅ Verification Checklist

After startup, verify:

- [ ] Backend server shows "Running on http://127.0.0.1:5000"
- [ ] Simulator shows "Starting fleet simulator"
- [ ] Can access http://127.0.0.1:5000 in browser
- [ ] Login page loads with gradient background
- [ ] Can login as admin/driver
- [ ] Admin dashboard shows live map
- [ ] Driver dashboard shows GPS location
- [ ] No error messages in terminal

---

## 🐛 Common Issues & Solutions

### ERROR: "Module not found"
**Solution:**
```bash
# Make sure (venv) is activated, then reinstall
pip install -r requirements.txt
```

### ERROR: "Can't connect to MySQL"
**Solution:**
```bash
# Start MySQL service
# Windows: net start mysql80
# Mac: brew services start mysql
# Linux: sudo service mysql start

# Then verify MySQL
mysql -u root -p -e "SELECT 1"
```

### ERROR: "Port 5000 already in use"
**Solution:**
```bash
# Windows: 
netstat -ano | findstr :5000
taskkill /PID [number] /F

# Mac/Linux:
lsof -i :5000
kill -9 [PID]
```

### ERROR: "Database not found"
**Solution:**
```bash
# Recreate database
mysql -u root -p fleet_system < database_schema.sql
```

### Frontend shows no data
**Solution:**
```bash
# Make sure simulator is running
# Check simulator output for errors
# Try accessing http://127.0.0.1:5000/api/vehicles in browser
```

---

## 🎯 Test the System

### Test 1: Admin Dashboard
1. Go to http://127.0.0.1:5000/admin
2. Login as admin
3. You should see:
   - Live map with vehicle markers
   - Statistics showing online/offline vehicles
   - Vehicle list updating in real-time

### Test 2: Driver Dashboard  
1. Go to http://127.0.0.1:5000/driver
2. Login as driver1
3. You should see:
   - Your assigned vehicle
   - GPS location on map
   - Start Trip button

### Test 3: Start a Trip
1. In driver dashboard, click "START TRIP"
2. Back in admin dashboard, trip should show as "Active"
3. Location updates should appear in history

### Test 4: Emergency SOS
1. In driver dashboard, click "🚨 SOS EMERGENCY"
2. Confirm the action
3. In admin dashboard, go to "SOS Alerts" tab
4. You should see the emergency alert

---

## 📁 Project Structure

```
fleet_system/
├── app.py                      # Main Flask app
├── simulator.py                # Vehicle simulator
├── database_schema.sql         # Database setup
├── requirements.txt            # Python packages
├── README.md                   # Full documentation
├── QUICK_START.md             # Quick reference
├── INSTALL.md                 # This file
├── buffer.json                # Offline data buffer (auto-generated)
├── static/
│   └── style.css              # CSS styles
└── templates/
    ├── login.html             # Login page
    ├── admin.html             # Admin dashboard
    ├── driver.html            # Driver dashboard
    └── reports.html           # Reports page
```

---

## 🔧 Configuration Files

### app.py
Main Flask application with routes and API endpoints.
**Important**: Change `app.secret_key` before production

### simulator.py
Vehicle GPS simulator that sends realistic data.
Automatically buffers data if server is unavailable.

### database_schema.sql
MySQL database structure with 11 tables.
Includes sample data for testing.

### requirements.txt
All Python package dependencies.

---

## 📊 Database Connection

The app connects to MySQL with these defaults:
```python
host: localhost
user: root
password: (empty)
database: fleet_system
```

If you set a MySQL password during installation:
Edit `app.py` line 28 and add your password:
```python
password="your_password_here"
```

---

## 🛑 Stopping the Application

### To stop gracefully:

1. **Simulator** (Terminal 2):
   - Press `Ctrl+C`
   - Wait for "Simulator stopped by user" message

2. **Backend Server** (Terminal 1):
   - Press `Ctrl+C`
   - Should show "Shutdown signal received"

3. **Deactivate Python environment**:
   ```bash
   deactivate
   ```

---

## 🆘 Get Help

### If you get stuck:

1. **Check logs**:
   - Look at terminal output for error messages
   - Check `fleet_simulator.log` for simulator errors

2. **Verify database**:
   ```bash
   mysql -u root -p fleet_system
   SHOW TABLES;
   SELECT COUNT(*) FROM vehicles;
   EXIT;
   ```

3. **Test connection**:
   - Visit http://127.0.0.1:5000/api/vehicles
   - Should return JSON with vehicle data

---

## 🎓 What Each Component Does

| Component | Purpose | Terminal |
|-----------|---------|----------|
| app.py | Web server & API | Terminal 1 |
| simulator.py | Generates GPS data | Terminal 2 |
| database_schema.sql | Database setup | One-time |
| requirements.txt | Python packages | One-time |

---

## ✨ You're All Set! 🎉

Your Fleet Management System is ready to use!

**Next Steps:**
1. ✅ Create admin users
2. ✅ Add drivers and vehicles
3. ✅ Assign drivers to vehicles
4. ✅ Train users on the dashboard

---

**Last Updated**: March 24, 2026  
**Version**: 1.0.0  
**Support**: Refer to README.md for detailed documentation
