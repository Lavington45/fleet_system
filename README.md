# 🚗 FleetGuard - Fleet Management System

A comprehensive, secure vehicle tracking system built with Flask, MySQL, and real-time GPS tracking. Designed for fleet administrators and drivers with offline data buffering, emergency alerts, and historical playback.

## 📋 Features

### Driver Features
- ✅ **Secure Login** - Password-hashed authentication
- ✅ **GPS Tracking** - Real-time location display with accuracy metrics
- ✅ **Trip Management** - Start/End trips with automatic logging
- ✅ **Speed Monitoring** - Real-time speed display
- ✅ **Network Status** - Connectivity status indicator
- ✅ **Emergency SOS** - One-click emergency alert to admin
- ✅ **Incident Reporting** - Report breakdowns, accidents, traffic issues
- ✅ **Offline Support** - Automatic data buffering when connectivity is lost
- ✅ **Notifications** - Real-time alerts and incident updates

### Admin Features
- ✅ **Live Map** - Real-time vehicle tracking on interactive map
- ✅ **Vehicle Status** - Online/offline status with color-coded markers
- ✅ **Fleet Analytics** - Statistics on online/offline vehicles, incidents, alerts
- ✅ **Incident Management** - View all reported incidents with severity levels
- ✅ **Emergency Alerts** - Monitor and acknowledge critical SOS alerts
- ✅ **Trip History** - View historical trip data for all vehicles
- ✅ **Trip Playback** - Replay vehicle routes for verification
- ✅ **Reports** - Generate daily, weekly, or monthly reports
- ✅ **Vehicle Management** - Assign drivers to vehicles

### System Features
- ✅ **Data Encryption** - Secure data transmission
- ✅ **Intelligent Buffering** - Store-and-forward mechanism for offline data
- ✅ **Auto-sync** - Automatic synchronization when connectivity restored
- ✅ **Role-based Access** - Admin and Driver roles with specific permissions
- ✅ **Comprehensive Logging** - Full audit trail of system activities
- ✅ **SQL Injection Prevention** - Parameterized queries throughout
- ✅ **Input Validation** - Sanitization and validation of all inputs

## 🛠 Tech Stack

- **Backend**: Python Flask
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript (ES6)
- **Maps**: Leaflet.js + OpenStreetMap
- **Simulator**: Python with realistic GPS movement

## 📦 Installation

### Prerequisites
- Python 3.8+
- MySQL Server
- Git (optional)

### 1. Clone or Extract the Project

```bash
cd fleet_system
```

### 2. Create Python Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup MySQL Database

```bash
# Start MySQL service
# Windows: net start MySQL80
# Linux: sudo service mysql start
# Mac: brew services start mysql

# Connect to MySQL
mysql -u root -p

# Create database (paste the contents of database_schema.sql)
SOURCE database_schema.sql;
```

Or run the schema directly:

```bash
mysql -u root -p fleet_system < database_schema.sql
```

### 5. Hash Demo Passwords (Optional but Recommended)

```bash
python
>>> from werkzeug.security import generate_password_hash
>>> print(generate_password_hash('admin123'))
>>> print(generate_password_hash('driver123'))
# Copy the hashed values and update the database
```

Then update the database with the hashed passwords:

```sql
UPDATE users SET password_hash='[hashed_password]' WHERE username='admin';
UPDATE users SET password_hash='[hashed_password]' WHERE username='driver1';
```

### 6. Update Configuration

Edit `app.py` and change the secret key:

```python
app.secret_key = "change-this-to-a-random-string"
```

## 🚀 Running the System

### 1. Start Backend Server

```bash
# Activate venv if not already
python app.py
# Server runs at http://127.0.0.1:5000
```

### 2. Start Vehicle Simulator (in another terminal)

```bash
# Navigate to project directory
# Activate venv
python simulator.py
```

The simulator will:
- Generate realistic GPS data for 20 vehicles
- Automatically buffer data if server is unavailable
- Sync buffered data when connectivity is restored
- Log all activities to `fleet_simulator.log`

### 3. Access the Web Interface

- **Admin Dashboard**: http://127.0.0.1:5000/admin
  - Username: `admin`
  - Password: `admin123`

- **Driver Dashboard**: http://127.0.0.1:5000/driver
  - Username: `driver1`
  - Password: `driver123`

- **Login**: http://127.0.0.1:5000

## 📊 Database Schema

### Core Tables

- **users** - System users (admin, drivers)
- **vehicles** - Fleet vehicles with current status
- **assignments** - Driver-to-vehicle assignments
- **trips** - Trip records with start/end times
- **vehicle_history** - GPS tracking points
- **incidents** - Reported incidents/breakdowns
- **emergency_alerts** - SOS alerts from drivers
- **data_buffer** - Offline data queue
- **reports** - Generated reports metadata
- **notifications** - User notifications

## 🔐 Security Features

1. **Password Hashing**: Using Werkzeug's secure hashing
2. **SQL Injection Prevention**: All queries use parameterized statements
3. **Input Validation**: Username, password, and form inputs validated
4. **Session Security**: Secure cookies with HTTPOnly and SameSite flags
5. **Role-based Access Control**: Routes protected with decorators
6. **Logging**: All authentication attempts and critical operations logged

## 📱 API Endpoints

### Authentication
- `POST /routes/` - Login
- `GET /logout` - Logout

### Vehicles
- `GET /api/vehicles` - Get all vehicles
- `GET /api/my_vehicle` - Get driver's assigned vehicle

### Trips
- `POST /api/trip/start` - Start a trip
- `POST /api/trip/end` - End a trip
- `GET /api/trip_history` - Get trip history
- `GET /api/trip/<id>/replay` - Get trip trajectory for replay

### Tracking
- `POST /api/update_vehicle` - Update vehicle location (from simulator)

### Incidents
- `POST /api/incident/report` - Report an incident
- `GET /api/incidents` - Get all incidents

### Alerts
- `POST /api/sos` - Send emergency SOS
- `GET /api/emergency_alerts` - Get active SOS alerts
- `POST /api/alert/<id>/acknowledge` - Acknowledge alert

### Reports
- `GET /api/reports` - Get generated reports
- `POST /api/report/generate` - Generate new report

### Notifications
- `GET /api/notifications` - Get user notifications
- `POST /api/notification/<id>/read` - Mark notification as read

## 🔧 Configuration

### app.py Configuration
```python
app.secret_key = "your-secret-key"  # Change this
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
```

### Database Connection
```python
host="localhost"
user="root"
password=""  # Set your MySQL password
database="fleet_system"
```

### Simulator Configuration
```python
UPDATE_INTERVAL = 5  # Seconds between updates
BASE_LAT = -1.286389  # Nairobi latitude
BASE_LON = 36.816667  # Nairobi longitude
BUFFER_FILE = "buffer.json"  # Buffered data location
```

## 📝 Demo Walkthrough

### As Admin:
1. Login with admin credentials
2. View live vehicle tracking on the map
3. Monitor online/offline vehicles
4. View pending incidents and SOS alerts
5. Generate and view reports
6. Acknowledge emergency alerts

### As Driver:
1. Login with driver credentials
2. View assigned vehicle
3. Check GPS location and speed
4. Start and end trips
5. Report incidents
6. Send emergency SOS if needed

## 🐛 Troubleshooting

### Database Connection Error
```
Solution: Ensure MySQL is running and credentials in app.py are correct
mysql -u root -p
SHOW DATABASES;
```

### Port 5000 Already in Use
```bash
# Windows: Find and kill the process
netstat -ano | findstr :5000
taskkill /PID [PID] /F

# Linux/Mac:
lsof -i :5000
kill -9 [PID]
```

### Simulator Not Buffering Data
```
Check buffer.json file permissions and ensure disk space is available
Check fleet_simulator.log for detailed error messages
```

### Geolocation Not Permission
```
Enable location services in browser
Allow HTTPS (in production) for geolocation to work
```

## 📈 Performance Optimization

1. **Database Indexes**: Already added on frequently queried columns
2. **Connection Pooling**: Using persistent connections
3. **Batch Buffer Sync**: Syncs 5 records per cycle to avoid overload
4. **Map Marker Updates**: Only updates markers that have moved

## 🔄 Backup & Recovery

### Backup Database
```bash
mysqldump -u root -p fleet_system > backup_fleet_system.sql
```

### Restore Database
```bash
mysql -u root -p fleet_system < backup_fleet_system.sql
```

## 🚀 Production Deployment

Before deploying to production:

1. **Change Secret Keys**
   - Update `app.secret_key` to a strong random string
   - Update `ENCRYPTION_KEY` in simulator.py

2. **Enable HTTPS**
   - Use gunicorn with SSL certificates
   - Update browser geolocation settings

3. **Database Security**
   - Create dedicated MySQL user with limited permissions
   - Use strong passwords
   - Enable MySQL SSL

4. **Environment Variables**
   - Move sensitive config to `.env` file
   - Use `python-dotenv` to load configuration

5. **Monitoring & Logging**
   - Setup centralized logging
   - Monitor server metrics
   - Setup automated backups

## 📞 Support & Maintenance

### Log Files
- `fleet_simulator.log` - Simulator activities
- Flask development logs - Server activities

### Common Maintenance Tasks
- Clean old vehicle_history records monthly
- Archive completed reports quarterly
- Backup database weekly
- Monitor buffer.json size

## 📄 License

This project is for educational and fleet management purposes.

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Leaflet.js Documentation](https://leafletjs.com/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [OpenStreetMap](https://www.openstreetmap.org/)

---

**Version**: 1.0.0  
**Last Updated**: March 24, 2026  
**Status**: Production Ready ✅
