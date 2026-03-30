from flask import Flask, render_template, request, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras
import json
import re
import logging
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
def get_db_connection():
    try:
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            conn = psycopg2.connect(database_url)
        else:
            conn = psycopg2.connect(
                host=os.environ.get('DB_HOST', 'localhost'),
                user=os.environ.get('DB_USER', 'postgres'),
                password=os.environ.get('DB_PASSWORD', ''),
                dbname=os.environ.get('DB_NAME', 'fleet_system')
            )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        print(f"Database connection failed: {e}")  # Add print for debugging
        return None


def init_db():
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed. Tables not created.")
        return
    cursor = conn.cursor()

    # Create vehicles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            status VARCHAR(50)
        )
    """)

    # Create users table (example)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50),
            email VARCHAR(100)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tables created or verified successfully.")

# Validation functions
def validate_username(username):
    if not username or len(username) < 3 or len(username) > 50:
        return False
    return re.match("^[a-zA-Z0-9_-]+$", username) is not None

def validate_password(password):
    if not password or len(password) < 6:
        return False
    return True

def sanitize_input(value):
    if isinstance(value, str):
        return value.strip()[:255]
    return value

# Decorators
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user" not in session:
                return redirect("/")
            if role and session.get("role") != role:
                return redirect("/")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user" not in session:
                return jsonify({"error": "Unauthorized"}), 401
            if role and session.get("role") != role:
                return jsonify({"error": "Forbidden"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ============== AUTHENTICATION ==============
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = sanitize_input(request.form.get("username", ""))
        password = request.form.get("password", "")
        
        if not validate_username(username):
            return render_template("login.html", error="Invalid username format")
        
        if not validate_password(password):
            return render_template("login.html", error="Invalid password")
        
        conn = get_db_connection()
        if not conn:
            return render_template("login.html", error="Database error"), 500
        
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(
                "SELECT user_id, username, password_hash, role, status FROM users WHERE username=%s",
                (username,)
            )
            user = cursor.fetchone()
            cursor.close()
            
            if user and user["status"] == "active" and check_password_hash(user["password_hash"], password):
                session.permanent = True
                session["user_id"] = user["user_id"]
                session["user"] = user["username"]
                session["role"] = user["role"]
                logger.info(f"User {username} logged in successfully")
                return redirect("/admin" if user["role"] == "admin" else "/driver")
            else:
                logger.warning(f"Failed login attempt for user {username}")
                return render_template("login.html", error="Invalid credentials or account inactive")
        except Exception as e:
            logger.error(f"Login error: {e}")
            return render_template("login.html", error="Authentication error"), 500
        finally:
            conn.close()
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ============== DASHBOARDS ==============
@app.route("/admin")
@login_required(role="admin")
def admin():
    return render_template("admin.html")

@app.route("/driver")
@login_required(role="driver")
def driver():
    return render_template("driver.html")

# ============== API: USER MANAGEMENT ==============
@app.route("/api/users")
@api_login_required(role="admin")
def get_users():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "SELECT user_id, username, full_name, role, status FROM users ORDER BY role, username"
        )
        users = cursor.fetchall()
        cursor.close()
        return jsonify(users)
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return jsonify({"error": "Failed to fetch users"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/user/create", methods=["POST"])
@api_login_required(role="admin")
def create_user():
    data = request.get_json()
    
    if not data or "username" not in data or "password" not in data or "full_name" not in data or "role" not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    username = sanitize_input(data.get("username", ""))
    password = data.get("password", "")
    full_name = sanitize_input(data.get("full_name", ""))
    role = data.get("role", "")
    
    if not validate_username(username):
        return jsonify({"error": "Invalid username format"}), 400
    
    if not validate_password(password):
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    
    if role not in ["admin", "driver"]:
        return jsonify({"error": "Invalid role"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Check if username already exists
        cursor.execute("SELECT user_id FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            return jsonify({"error": "Username already exists"}), 409
        
        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, full_name, role, status) VALUES (%s, %s, %s, %s, 'active')",
            (username, password_hash, full_name, role)
        )
        conn.commit()
        logger.info(f"User {username} created with role {role}")
        return jsonify({"message": "User created successfully"}), 201
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error creating user: {e}")
        return jsonify({"error": "Failed to create user"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/user/<int:user_id>/delete", methods=["POST"])
@api_login_required(role="admin")
def delete_user(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Check if user exists
        cursor.execute("SELECT user_id, username FROM users WHERE user_id=%s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Prevent deleting admin user if they're the only one
        if user["user_id"] == session.get("user_id"):
            cursor.execute("SELECT COUNT(*) as admin_count FROM users WHERE role='admin' AND status='active'")
            result = cursor.fetchone()
            if result["admin_count"] <= 1:
                return jsonify({"error": "Cannot delete the last active admin"}), 400
        
        # Delete user
        cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
        conn.commit()
        logger.info(f"User {user['username']} deleted")
        return jsonify({"message": "User deleted successfully"}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error deleting user: {e}")
        return jsonify({"error": "Failed to delete user"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/user/<int:user_id>/status", methods=["POST"])
@api_login_required(role="admin")
def update_user_status(user_id):
    data = request.get_json()
    
    if not data or "status" not in data:
        return jsonify({"error": "Missing status field"}), 400
    
    status = data.get("status")
    if status not in ["active", "inactive"]:
        return jsonify({"error": "Invalid status"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Check if user exists
        cursor.execute("SELECT user_id, username FROM users WHERE user_id=%s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Update user status
        cursor.execute(
            "UPDATE users SET status=%s WHERE user_id=%s",
            (status, user_id)
        )
        conn.commit()
        logger.info(f"User {user['username']} status updated to {status}")
        return jsonify({"message": f"User status updated to {status}"}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error updating user status: {e}")
        return jsonify({"error": "Failed to update user status"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ============== API: VEHICLES ==============
@app.route("/api/vehicles")
@api_login_required()
def vehicles():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT vehicle_id, vehicle_name, registration_number, lat, lon, speed,
                   connectivity_status, status, last_update
            FROM vehicles
            ORDER BY vehicle_name
        """)
        vehicles_list = cursor.fetchall()
        cursor.close()
        
        # Format timestamps
        for v in vehicles_list:
            if v["last_update"]:
                v["last_update"] = v["last_update"].isoformat()
        
        return jsonify(vehicles_list)
    except Exception as e:
        logger.error(f"Error fetching vehicles: {e}")
        return jsonify({"error": "Failed to fetch vehicles"}), 500
    finally:
        conn.close()

# ============== API: DRIVER VEHICLE ==============
@app.route("/api/my_vehicle")
@api_login_required(role="driver")
def my_vehicle():
    user_id = session.get("user_id")
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT v.vehicle_id, v.vehicle_name, v.registration_number, a.driver_user_id
            FROM assignments a
            JOIN vehicles v ON a.vehicle_id = v.vehicle_id
            WHERE a.driver_user_id=%s AND a.status='active'
            LIMIT 1
        """, (user_id,))
        vehicle = cursor.fetchone()
        cursor.close()
        
        if vehicle:
            return jsonify(vehicle)
        else:
            return jsonify({"error": "No vehicle assigned"}), 404
    except Exception as e:
        logger.error(f"Error fetching driver vehicle: {e}")
        return jsonify({"error": "Failed to fetch vehicle"}), 500
    finally:
        conn.close()

# ============== API: TRIPS ==============
@app.route("/api/trip/start", methods=["POST"])
@api_login_required(role="driver")
def start_trip():
    user_id = session.get("user_id")
    data = request.get_json()
    
    if not data or "vehicle_id" not in data or "lat" not in data or "lon" not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    vehicle_id = int(data.get("vehicle_id"))
    lat = float(data.get("lat"))
    lon = float(data.get("lon"))
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Verify driver owns this assignment
        cursor.execute(
            "SELECT * FROM assignments WHERE driver_user_id=%s AND vehicle_id=%s AND status='active'",
            (user_id, vehicle_id)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Unauthorized"}), 403
        
        # Create trip
        cursor.execute("""
            INSERT INTO trips (vehicle_id, driver_user_id, start_time, start_lat, start_lon, status)
            VALUES (%s, %s, NOW(), %s, %s, 'ongoing')
        """, (vehicle_id, user_id, lat, lon))
        
        trip_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        
        logger.info(f"Trip {trip_id} started for driver {user_id}")
        return jsonify({"trip_id": trip_id, "message": "Trip started"}), 201
    except Exception as e:
        conn.rollback()
        logger.error(f"Error starting trip: {e}")
        return jsonify({"error": "Failed to start trip"}), 500
    finally:
        conn.close()

@app.route("/api/trip/end", methods=["POST"])
@api_login_required(role="driver")
def end_trip():
    user_id = session.get("user_id")
    data = request.get_json()
    
    if not data or "trip_id" not in data or "lat" not in data or "lon" not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    trip_id = int(data.get("trip_id"))
    lat = float(data.get("lat"))
    lon = float(data.get("lon"))
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Verify trip ownership
        cursor.execute(
            "SELECT * FROM trips WHERE trip_id=%s AND driver_user_id=%s AND status='ongoing'",
            (trip_id, user_id)
        )
        trip = cursor.fetchone()
        if not trip:
            return jsonify({"error": "Trip not found"}), 404
        
        # Update trip
        cursor.execute("""
            UPDATE trips
            SET end_time=NOW(), end_lat=%s, end_lon=%s, status='completed'
            WHERE trip_id=%s
        """, (lat, lon, trip_id))
        
        conn.commit()
        cursor.close()
        
        logger.info(f"Trip {trip_id} ended for driver {user_id}")
        return jsonify({"message": "Trip ended"}), 200
    except Exception as e:
        conn.rollback()
        logger.error(f"Error ending trip: {e}")
        return jsonify({"error": "Failed to end trip"}), 500
    finally:
        conn.close()

# ============== API: UPDATE VEHICLE LOCATION ==============
@app.route("/api/update_vehicle", methods=["POST"])
def update_vehicle():
    data = request.get_json()
    
    if not data or not all(k in data for k in ["vehicle", "lat", "lon", "speed"]):
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = None
    cursor = None
    try:
        vehicle_name = sanitize_input(data.get("vehicle"))
        lat = float(data.get("lat"))
        lon = float(data.get("lon"))
        speed = int(data.get("speed"))
        trip_id = data.get("trip_id")
        
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database error"}), 500
        
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get vehicle ID from name
        cursor.execute("SELECT vehicle_id FROM vehicles WHERE vehicle_name=%s", (vehicle_name,))
        vehicle = cursor.fetchone()
        if not vehicle:
            return jsonify({"error": "Vehicle not found"}), 404
        
        vehicle_id = vehicle["vehicle_id"]
        
        # Update vehicle status
        cursor.execute("""
            UPDATE vehicles
            SET lat=%s, lon=%s, speed=%s, connectivity_status='online', last_update=NOW()
            WHERE vehicle_id=%s
        """, (lat, lon, speed, vehicle_id))
        
        # Validate trip_id if provided
        if trip_id:
            cursor.execute("SELECT trip_id FROM trips WHERE trip_id=%s", (trip_id,))
            if not cursor.fetchone():
                # Invalid trip_id, set to None instead of failing
                trip_id = None
        
        # Store in history (only with valid trip_id)
        cursor.execute("""
            INSERT INTO vehicle_history (vehicle_id, trip_id, lat, lon, speed)
            VALUES (%s, %s, %s, %s, %s)
        """, (vehicle_id, trip_id, lat, lon, speed))
        
        conn.commit()
        return jsonify({"message": "Vehicle updated"}), 200
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error updating vehicle: {e}")
        return jsonify({"error": "Failed to update vehicle"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ============== API: INCIDENTS ==============
@app.route("/api/incident/report", methods=["POST"])
@api_login_required(role="driver")
def report_incident():
    user_id = session.get("user_id")
    data = request.get_json()
    
    required_fields = ["vehicle_id", "incident_type", "lat", "lon"]
    if not data or not all(k in data for k in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        vehicle_id = int(data.get("vehicle_id"))
        incident_type = data.get("incident_type")
        lat = float(data.get("lat"))
        lon = float(data.get("lon"))
        description = sanitize_input(data.get("description", ""))
        trip_id = data.get("trip_id")
        severity = data.get("severity", "medium")
        
        if incident_type not in ["breakdown", "accident", "traffic", "other"]:
            return jsonify({"error": "Invalid incident type"}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database error"}), 500
        
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO incidents (trip_id, vehicle_id, driver_user_id, incident_type, description, lat, lon, severity)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (trip_id, vehicle_id, user_id, incident_type, description, lat, lon, severity))
        
        incident_id = cursor.lastrowid
        
        # Create notification for admin
        cursor.execute("""
            INSERT INTO notifications (user_id, title, message, notification_type, reference_id, reference_type)
            SELECT user_id, %s, %s, 'incident', %s, 'incident'
            FROM users WHERE role='admin'
        """, (f"Incident: {incident_type}", f"Driver reported {incident_type} at ({lat}, {lon})", incident_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Incident {incident_id} reported by driver {user_id}")
        return jsonify({"incident_id": incident_id, "message": "Incident reported"}), 201
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error reporting incident: {e}")
        return jsonify({"error": "Failed to report incident"}), 500
    finally:
        if conn:
            conn.close()

@app.route("/api/incidents")
@api_login_required(role="admin")
def get_incidents():
    print("get_incidents called")  # Add debug print
    conn = get_db_connection()
    if not conn:
        print("Database connection failed")  # Add debug print
        return jsonify({"error": "Database error"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT i.incident_id, i.vehicle_id, i.driver_user_id, i.incident_type, 
                   i.description, i.lat, i.lon, i.severity, i.status, i.reported_at,
                   v.vehicle_name, u.full_name
            FROM incidents i
            JOIN vehicles v ON i.vehicle_id = v.vehicle_id
            JOIN users u ON i.driver_user_id = u.user_id
            ORDER BY i.reported_at DESC
            LIMIT 100
        """)
        incidents = cursor.fetchall()
        print(f"Found {len(incidents)} incidents")  # Add debug print
        
        for inc in incidents:
            if inc["reported_at"]:
                inc["reported_at"] = inc["reported_at"].isoformat()
        
        return jsonify(incidents)
    except Exception as e:
        logger.exception("Error fetching incidents")
        print(f"Error fetching incidents: {e}")  # Add debug print
        return jsonify({"error": "Failed to fetch incidents", "details": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ============== API: EMERGENCY ALERTS (SOS) ==============
@app.route("/api/sos", methods=["POST"])
@api_login_required(role="driver")
def emergency_sos():
    user_id = session.get("user_id")
    data = request.get_json()
    
    required_fields = ["vehicle_id", "lat", "lon"]
    if not data or not all(k in data for k in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        vehicle_id = int(data.get("vehicle_id"))
        lat = float(data.get("lat"))
        lon = float(data.get("lon"))
        message = sanitize_input(data.get("message", "Emergency SOS"))
        trip_id = data.get("trip_id")
        
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database error"}), 500
        
        cursor = conn.cursor()
        
        # Save emergency alert
        cursor.execute("""
            INSERT INTO emergency_alerts (trip_id, vehicle_id, driver_user_id, message, lat, lon, priority, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'critical', 'active')
        """, (trip_id, vehicle_id, user_id, message, lat, lon))
        
        alert_id = cursor.lastrowid
        
        # Create critical notifications for all admins
        cursor.execute("""
            INSERT INTO notifications (user_id, title, message, notification_type, reference_id, reference_type)
            SELECT user_id, %s, %s, 'alert', %s, 'emergency_alert'
            FROM users WHERE role='admin'
        """, (f"🚨 EMERGENCY SOS", f"Critical: {message} at ({lat}, {lon})", alert_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.critical(f"SOS ALERT {alert_id} from driver {user_id}: ({lat}, {lon})")
        return jsonify({"alert_id": alert_id, "message": "SOS sent to admin"}), 201
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error processing SOS: {e}")
        return jsonify({"error": "Failed to send SOS"}), 500
    finally:
        if conn:
            conn.close()

@app.route("/api/emergency_alerts")
@api_login_required(role="admin")
def get_emergency_alerts():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT ea.alert_id, ea.vehicle_id, ea.driver_user_id, ea.message,
                   ea.lat, ea.lon, ea.priority, ea.status, ea.alert_time,
                   v.vehicle_name, u.full_name
            FROM emergency_alerts ea
            JOIN vehicles v ON ea.vehicle_id = v.vehicle_id
            JOIN users u ON ea.driver_user_id = u.user_id
            WHERE ea.status IN ('active', 'acknowledged')
            ORDER BY ea.priority DESC, ea.alert_time DESC
            LIMIT 50
        """)
        alerts = cursor.fetchall()
        
        for alert in alerts:
            if alert["alert_time"]:
                alert["alert_time"] = alert["alert_time"].isoformat()
        
        return jsonify(alerts)
    except Exception as e:
        logger.exception("Error fetching emergency alerts")
        return jsonify({"error": "Failed to fetch alerts", "details": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/alert/<int:alert_id>/acknowledge", methods=["POST"])
@api_login_required(role="admin")
def acknowledge_alert(alert_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE emergency_alerts
            SET status='acknowledged', acknowledged_at=NOW()
            WHERE alert_id=%s
        """, (alert_id,))
        conn.commit()
        cursor.close()
        
        logger.info(f"Alert {alert_id} acknowledged")
        return jsonify({"message": "Alert acknowledged"}), 200
    except Exception as e:
        conn.rollback()
        logger.error(f"Error acknowledging alert: {e}")
        return jsonify({"error": "Failed to acknowledge alert"}), 500
    finally:
        conn.close()

# ============== API: TRIP HISTORY ==============
@app.route("/api/trip_history")
@api_login_required()
def trip_history():
    vehicle_id = request.args.get("vehicle_id")
    limit = int(request.args.get("limit", 100))
    
    if not vehicle_id:
        return jsonify({"error": "vehicle_id required"}), 400
    
    try:
        vehicle_id = int(vehicle_id)
    except:
        return jsonify({"error": "Invalid vehicle_id"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT trip_id, vehicle_id, driver_user_id, start_time, end_time,
                   start_lat, start_lon, end_lat, end_lon, status, distance_traveled, avg_speed
            FROM trips
            WHERE vehicle_id=%s
            ORDER BY start_time DESC
            LIMIT %s
        """, (vehicle_id, limit))
        trips = cursor.fetchall()
        cursor.close()
        
        for trip in trips:
            if trip["start_time"]:
                trip["start_time"] = trip["start_time"].isoformat()
            if trip["end_time"]:
                trip["end_time"] = trip["end_time"].isoformat()
        
        return jsonify(trips)
    except Exception as e:
        logger.error(f"Error fetching trip history: {e}")
        return jsonify({"error": "Failed to fetch trip history"}), 500
    finally:
        conn.close()

@app.route("/api/trip/<int:trip_id>/replay")
@api_login_required(role="admin")
def replay_trip(trip_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT history_id, lat, lon, speed, accuracy, recorded_at
            FROM vehicle_history
            WHERE trip_id=%s
            ORDER BY recorded_at ASC
        """, (trip_id,))
        history = cursor.fetchall()
        cursor.close()
        
        for h in history:
            if h["recorded_at"]:
                h["recorded_at"] = h["recorded_at"].isoformat()
        
        return jsonify({"trajectory": history})
    except Exception as e:
        logger.error(f"Error replaying trip: {e}")
        return jsonify({"error": "Failed to replay trip"}), 500
    finally:
        conn.close()

# ============== API: REPORTS ==============
@app.route("/api/reports")
@api_login_required(role="admin")
def get_reports():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT r.report_id, r.report_type, r.start_date, r.end_date,
                   r.vehicle_id, r.status, r.created_at,
                   v.vehicle_name
            FROM reports r
            LEFT JOIN vehicles v ON r.vehicle_id = v.vehicle_id
            ORDER BY r.created_at DESC
            LIMIT 50
        """)
        reports = cursor.fetchall()
        cursor.close()
        
        for rep in reports:
            if rep["created_at"]:
                rep["created_at"] = rep["created_at"].isoformat()
        
        return jsonify(reports)
    except Exception as e:
        logger.error(f"Error fetching reports: {e}")
        return jsonify({"error": "Failed to fetch reports"}), 500
    finally:
        conn.close()

@app.route("/api/report/generate", methods=["POST"])
@api_login_required(role="admin")
def generate_report():
    user_id = session.get("user_id")
    data = request.get_json()
    
    if not data or "report_type" not in data:
        return jsonify({"error": "Missing report_type"}), 400
    
    report_type = data.get("report_type")
    vehicle_id = data.get("vehicle_id")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reports (created_by, report_type, start_date, end_date, vehicle_id, status)
            VALUES (%s, %s, %s, %s, %s, 'pending')
        """, (user_id, report_type, start_date, end_date, vehicle_id))
        
        report_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        
        logger.info(f"Report {report_id} generation queued by admin {user_id}")
        return jsonify({"report_id": report_id, "message": "Report generation started"}), 201
    except Exception as e:
        conn.rollback()
        logger.error(f"Error generating report: {e}")
        return jsonify({"error": "Failed to generate report"}), 500
    finally:
        conn.close()

# ============== API: NOTIFICATIONS ==============
@app.route("/api/notifications")
@api_login_required()
def get_notifications():
    user_id = session.get("user_id")
    limit = int(request.args.get("limit", 20))
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT notification_id, title, message, notification_type, is_read, created_at
            FROM notifications
            WHERE user_id=%s
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit))
        notifications = cursor.fetchall()
        cursor.close()
        
        for notif in notifications:
            if notif["created_at"]:
                notif["created_at"] = notif["created_at"].isoformat()
        
        return jsonify(notifications)
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        return jsonify({"error": "Failed to fetch notifications"}), 500
    finally:
        conn.close()

@app.route("/api/notification/<int:notif_id>/read", methods=["POST"])
@api_login_required()
def mark_notification_read(notif_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE notifications
            SET is_read=TRUE
            WHERE notification_id=%s AND user_id=%s
        """, (notif_id, session.get("user_id")))
        conn.commit()
        cursor.close()
        
        return jsonify({"message": "Marked as read"}), 200
    except Exception as e:
        conn.rollback()
        logger.error(f"Error marking notification: {e}")
        return jsonify({"error": "Failed to mark notification"}), 500
    finally:
        conn.close()

# ============== API: VEHICLE ASSIGNMENTS ==============
@app.route("/api/drivers")
@api_login_required(role="admin")
def get_drivers():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "SELECT user_id, username, full_name FROM users WHERE role='driver' AND status='active'"
        )
        drivers = cursor.fetchall()
        return jsonify(drivers)
    except Exception as e:
        logger.error(f"Error fetching drivers: {e}")
        return jsonify({"error": "Failed to fetch drivers"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/assignment/create", methods=["POST"])
@api_login_required(role="admin")
def create_assignment():
    data = request.get_json()
    
    if not data or "vehicle_id" not in data or "driver_user_id" not in data:
        return jsonify({"error": "Missing vehicle_id and driver_user_id"}), 400
    
    try:
        vehicle_id = int(data.get("vehicle_id"))
        driver_user_id = int(data.get("driver_user_id"))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid vehicle_id or driver_user_id format"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Check if vehicle exists and is available
        cursor.execute("SELECT vehicle_id, vehicle_name FROM vehicles WHERE vehicle_id=%s", (vehicle_id,))
        vehicle = cursor.fetchone()
        if not vehicle:
            return jsonify({"error": f"Vehicle {vehicle_id} not found"}), 404
        
        # Check if driver exists and is active
        cursor.execute("SELECT user_id, full_name FROM users WHERE user_id=%s AND role='driver' AND status='active'", (driver_user_id,))
        driver = cursor.fetchone()
        if not driver:
            return jsonify({"error": f"Driver {driver_user_id} not found or inactive"}), 404
        
        # Deactivate any existing assignments for this vehicle
        cursor.execute(
            "UPDATE assignments SET status='inactive' WHERE vehicle_id=%s AND status='active'",
            (vehicle_id,)
        )
        
        # Create new assignment
        cursor.execute(
            """INSERT INTO assignments (vehicle_id, driver_user_id, status) 
               VALUES (%s, %s, 'active')""",
            (vehicle_id, driver_user_id)
        )
        
        conn.commit()
        logger.info(f"Vehicle {vehicle['vehicle_name']} ({vehicle_id}) assigned to driver {driver['full_name']} ({driver_user_id})")
        return jsonify({"message": "Vehicle assigned successfully", "vehicle_id": vehicle_id, "driver_id": driver_user_id}), 201
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error creating assignment: {e}", exc_info=True)
        return jsonify({"error": f"Failed to create assignment: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/assignments")
@api_login_required(role="admin")
def get_assignments():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            """SELECT a.assignment_id, a.vehicle_id, a.driver_user_id, a.status,
                      v.vehicle_name, v.registration_number, u.full_name, u.username
               FROM assignments a
               JOIN vehicles v ON a.vehicle_id = v.vehicle_id
               JOIN users u ON a.driver_user_id = u.user_id
               WHERE a.status = 'active'
               ORDER BY a.assignment_id DESC"""
        )
        assignments = cursor.fetchall()
        return jsonify(assignments)
    except Exception as e:
        logger.error(f"Error fetching assignments: {e}")
        return jsonify({"error": "Failed to fetch assignments"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/assignment/<int:assignment_id>/revoke", methods=["POST"])
@api_login_required(role="admin")
def revoke_assignment(assignment_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Check if assignment exists
        cursor.execute("SELECT * FROM assignments WHERE assignment_id=%s", (assignment_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Assignment not found"}), 404
        
        # Deactivate assignment
        cursor.execute(
            "UPDATE assignments SET status='inactive' WHERE assignment_id=%s",
            (assignment_id,)
        )
        
        conn.commit()
        logger.info(f"Assignment {assignment_id} revoked")
        return jsonify({"message": "Assignment revoked successfully"}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error revoking assignment: {e}")
        return jsonify({"error": "Failed to revoke assignment"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
    
if __name__ == "__main__":
    init_db()  # Initialize tables on first run
    app.run()