-- FleetGuard MySQL Database Schema
-- Run this file to create all tables for the fleet management system

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    role ENUM('admin', 'driver') NOT NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create vehicles table
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_name VARCHAR(100) UNIQUE NOT NULL,
    registration_number VARCHAR(50) UNIQUE NOT NULL,
    lat DECIMAL(10, 8) DEFAULT 0,
    lon DECIMAL(11, 8) DEFAULT 0,
    speed INT DEFAULT 0,
    connectivity_status ENUM('online', 'offline') DEFAULT 'offline',
    status ENUM('active', 'inactive') DEFAULT 'active',
    last_update TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create assignments table
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    driver_user_id INT NOT NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
    FOREIGN KEY (driver_user_id) REFERENCES users(user_id),
    UNIQUE KEY unique_active_assignment (vehicle_id, driver_user_id, status)
);

-- Create trips table
CREATE TABLE IF NOT EXISTS trips (
    trip_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    driver_user_id INT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    start_lat DECIMAL(10, 8),
    start_lon DECIMAL(11, 8),
    end_lat DECIMAL(10, 8),
    end_lon DECIMAL(11, 8),
    status ENUM('ongoing', 'completed', 'cancelled') NOT NULL DEFAULT 'ongoing',
    distance_traveled DECIMAL(10, 2),
    avg_speed DECIMAL(6, 2),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
    FOREIGN KEY (driver_user_id) REFERENCES users(user_id)
);

-- Create vehicle_history table (for GPS tracking data)
CREATE TABLE IF NOT EXISTS vehicle_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    trip_id INT,
    lat DECIMAL(10, 8),
    lon DECIMAL(11, 8),
    speed INT,
    accuracy INT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE SET NULL
);

-- Create incidents table
CREATE TABLE IF NOT EXISTS incidents (
    incident_id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT,
    vehicle_id INT NOT NULL,
    driver_user_id INT NOT NULL,
    incident_type ENUM('breakdown', 'accident', 'traffic', 'other') NOT NULL,
    description TEXT,
    lat DECIMAL(10, 8),
    lon DECIMAL(11, 8),
    severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    status ENUM('open', 'acknowledged', 'resolved') DEFAULT 'open',
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE SET NULL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
    FOREIGN KEY (driver_user_id) REFERENCES users(user_id)
);

-- Create emergency_alerts table (SOS)
CREATE TABLE IF NOT EXISTS emergency_alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT,
    vehicle_id INT NOT NULL,
    driver_user_id INT NOT NULL,
    message TEXT,
    lat DECIMAL(10, 8),
    lon DECIMAL(11, 8),
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'critical',
    status ENUM('active', 'acknowledged', 'resolved') DEFAULT 'active',
    alert_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP NULL,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE SET NULL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
    FOREIGN KEY (driver_user_id) REFERENCES users(user_id)
);

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255),
    message TEXT,
    notification_type ENUM('incident', 'alert', 'assignment', 'system'),
    is_read BOOLEAN DEFAULT FALSE,
    reference_id INT,
    reference_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Create reports table
CREATE TABLE IF NOT EXISTS reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    created_by INT NOT NULL,
    report_type ENUM('daily', 'weekly', 'monthly', 'custom') NOT NULL,
    start_date DATE,
    end_date DATE,
    vehicle_id INT,
    status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE SET NULL
);

-- Create indexes for better query performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);

CREATE INDEX idx_vehicles_name ON vehicles(vehicle_name);
CREATE INDEX idx_vehicles_status ON vehicles(status);
CREATE INDEX idx_vehicles_connectivity ON vehicles(connectivity_status);

CREATE INDEX idx_assignments_vehicle ON assignments(vehicle_id);
CREATE INDEX idx_assignments_driver ON assignments(driver_user_id);
CREATE INDEX idx_assignments_status ON assignments(status);

CREATE INDEX idx_trips_vehicle ON trips(vehicle_id);
CREATE INDEX idx_trips_driver ON trips(driver_user_id);
CREATE INDEX idx_trips_status ON trips(status);
CREATE INDEX idx_trips_start_time ON trips(start_time);

CREATE INDEX idx_vehicle_history_vehicle ON vehicle_history(vehicle_id);
CREATE INDEX idx_vehicle_history_trip ON vehicle_history(trip_id);
CREATE INDEX idx_vehicle_history_time ON vehicle_history(recorded_at);

CREATE INDEX idx_incidents_vehicle ON incidents(vehicle_id);
CREATE INDEX idx_incidents_driver ON incidents(driver_user_id);
CREATE INDEX idx_incidents_type ON incidents(incident_type);
CREATE INDEX idx_incidents_status ON incidents(status);

CREATE INDEX idx_alerts_vehicle ON emergency_alerts(vehicle_id);
CREATE INDEX idx_alerts_driver ON emergency_alerts(driver_user_id);
CREATE INDEX idx_alerts_status ON emergency_alerts(status);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(is_read);

-- Insert demo/initial data
-- Admin user (password will be set via setup_users.py)
INSERT INTO users (username, password_hash, full_name, email, role, status)
VALUES ('admin', '', 'Administrator', 'admin@fleet.local', 'admin', 'active')
ON DUPLICATE KEY UPDATE username=username;

-- Driver users (password will be set via setup_users.py)
INSERT INTO users (username, password_hash, full_name, email, role, status)
VALUES ('driver1', '', 'John Driver', 'driver1@fleet.local', 'driver', 'active')
ON DUPLICATE KEY UPDATE username=username;

INSERT INTO users (username, password_hash, full_name, email, role, status)
VALUES ('driver2', '', 'Jane Driver', 'driver2@fleet.local', 'driver', 'active')
ON DUPLICATE KEY UPDATE username=username;

-- Demo vehicles
INSERT INTO vehicles (vehicle_name, registration_number, lat, lon, status)
VALUES
('Vehicle1', 'REG001', -1.286389, 36.816667, 'active'),
('Vehicle2', 'REG002', -1.290000, 36.820000, 'active'),
('Vehicle3', 'REG003', -1.280000, 36.810000, 'active'),
('Vehicle4', 'REG004', -1.295000, 36.825000, 'active'),
('Vehicle5', 'REG005', -1.285000, 36.815000, 'active')
ON DUPLICATE KEY UPDATE vehicle_name=vehicle_name;

-- Demo assignments (assign 2 vehicles to drivers)
INSERT INTO assignments (vehicle_id, driver_user_id, status)
VALUES
(1, 2, 'active'),
(2, 3, 'active')
ON DUPLICATE KEY UPDATE vehicle_id=vehicle_id;

COMMIT;
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for users table
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create vehicles table
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id SERIAL PRIMARY KEY,
    vehicle_name VARCHAR(100) UNIQUE NOT NULL,
    registration_number VARCHAR(50) UNIQUE NOT NULL,
    lat DECIMAL(10, 8) DEFAULT 0,
    lon DECIMAL(11, 8) DEFAULT 0,
    speed INT DEFAULT 0,
    connectivity_status VARCHAR(10) DEFAULT 'offline' CHECK (connectivity_status IN ('online', 'offline')),
    status VARCHAR(10) DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    last_update TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create assignments table
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id SERIAL PRIMARY KEY,
    vehicle_id INT NOT NULL,
    driver_user_id INT NOT NULL,
    status VARCHAR(10) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
    FOREIGN KEY (driver_user_id) REFERENCES users(user_id),
    UNIQUE (vehicle_id, driver_user_id, status)
);

-- Create trips table
CREATE TABLE IF NOT EXISTS trips (
    trip_id SERIAL PRIMARY KEY,
    vehicle_id INT NOT NULL,
    driver_user_id INT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    start_lat DECIMAL(10, 8),
    start_lon DECIMAL(11, 8),
    end_lat DECIMAL(10, 8),
    end_lon DECIMAL(11, 8),
    status VARCHAR(10) NOT NULL DEFAULT 'ongoing' CHECK (status IN ('ongoing', 'completed', 'cancelled')),
    distance_traveled DECIMAL(10, 2),
    avg_speed DECIMAL(6, 2),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
    FOREIGN KEY (driver_user_id) REFERENCES users(user_id)
);

-- Create vehicle_history table (for GPS tracking data)
CREATE TABLE IF NOT EXISTS vehicle_history (
    history_id SERIAL PRIMARY KEY,
    vehicle_id INT NOT NULL,
    trip_id INT,
    lat DECIMAL(10, 8),
    lon DECIMAL(11, 8),
    speed INT,
    accuracy INT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE SET NULL
);

-- Create incidents table
CREATE TABLE IF NOT EXISTS incidents (
    incident_id SERIAL PRIMARY KEY,
    trip_id INT,
    vehicle_id INT NOT NULL,
    driver_user_id INT NOT NULL,
    incident_type VARCHAR(20) NOT NULL CHECK (incident_type IN ('breakdown', 'accident', 'traffic', 'other')),
    description TEXT,
    lat DECIMAL(10, 8),
    lon DECIMAL(11, 8),
    severity VARCHAR(10) DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    status VARCHAR(15) DEFAULT 'open' CHECK (status IN ('open', 'acknowledged', 'resolved')),
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE SET NULL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
    FOREIGN KEY (driver_user_id) REFERENCES users(user_id)
);

-- Create emergency_alerts table (SOS)
CREATE TABLE IF NOT EXISTS emergency_alerts (
    alert_id SERIAL PRIMARY KEY,
    trip_id INT,
    vehicle_id INT NOT NULL,
    driver_user_id INT NOT NULL,
    message TEXT,
    lat DECIMAL(10, 8),
    lon DECIMAL(11, 8),
    priority VARCHAR(10) DEFAULT 'critical' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    status VARCHAR(15) DEFAULT 'active' CHECK (status IN ('active', 'acknowledged', 'resolved')),
    alert_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP NULL,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE SET NULL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
    FOREIGN KEY (driver_user_id) REFERENCES users(user_id)
);

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255),
    message TEXT,
    notification_type VARCHAR(20) CHECK (notification_type IN ('incident', 'alert', 'assignment', 'system')),
    is_read BOOLEAN DEFAULT FALSE,
    reference_id INT,
    reference_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Create reports table
CREATE TABLE IF NOT EXISTS reports (
    report_id SERIAL PRIMARY KEY,
    created_by INT NOT NULL,
    report_type VARCHAR(10) NOT NULL CHECK (report_type IN ('daily', 'weekly', 'monthly', 'custom')),
    start_date DATE,
    end_date DATE,
    vehicle_id INT,
    status VARCHAR(10) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE SET NULL
);

-- Create indexes for better query performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);

CREATE INDEX idx_vehicles_name ON vehicles(vehicle_name);
CREATE INDEX idx_vehicles_status ON vehicles(status);
CREATE INDEX idx_vehicles_connectivity ON vehicles(connectivity_status);

CREATE INDEX idx_assignments_vehicle ON assignments(vehicle_id);
CREATE INDEX idx_assignments_driver ON assignments(driver_user_id);
CREATE INDEX idx_assignments_status ON assignments(status);

CREATE INDEX idx_trips_vehicle ON trips(vehicle_id);
CREATE INDEX idx_trips_driver ON trips(driver_user_id);
CREATE INDEX idx_trips_status ON trips(status);
CREATE INDEX idx_trips_start_time ON trips(start_time);

CREATE INDEX idx_vehicle_history_vehicle ON vehicle_history(vehicle_id);
CREATE INDEX idx_vehicle_history_trip ON vehicle_history(trip_id);
CREATE INDEX idx_vehicle_history_time ON vehicle_history(recorded_at);

CREATE INDEX idx_incidents_vehicle ON incidents(vehicle_id);
CREATE INDEX idx_incidents_driver ON incidents(driver_user_id);
CREATE INDEX idx_incidents_type ON incidents(incident_type);
CREATE INDEX idx_incidents_status ON incidents(status);

CREATE INDEX idx_alerts_vehicle ON emergency_alerts(vehicle_id);
CREATE INDEX idx_alerts_driver ON emergency_alerts(driver_user_id);
CREATE INDEX idx_alerts_status ON emergency_alerts(status);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(is_read);

-- Insert demo/initial data
-- Admin user (password will be set via setup_users.py)
INSERT INTO users (username, password_hash, full_name, email, role, status)
VALUES ('admin', '', 'Administrator', 'admin@fleet.local', 'admin', 'active')
ON CONFLICT (username) DO NOTHING;

-- Driver users (password will be set via setup_users.py)
INSERT INTO users (username, password_hash, full_name, email, role, status)
VALUES ('driver1', '', 'John Driver', 'driver1@fleet.local', 'driver', 'active')
ON CONFLICT (username) DO NOTHING;

INSERT INTO users (username, password_hash, full_name, email, role, status)
VALUES ('driver2', '', 'Jane Driver', 'driver2@fleet.local', 'driver', 'active')
ON CONFLICT (username) DO NOTHING;

-- Demo vehicles
INSERT INTO vehicles (vehicle_name, registration_number, lat, lon, status)
VALUES
('Vehicle1', 'REG001', -1.286389, 36.816667, 'active'),
('Vehicle2', 'REG002', -1.290000, 36.820000, 'active'),
('Vehicle3', 'REG003', -1.280000, 36.810000, 'active'),
('Vehicle4', 'REG004', -1.295000, 36.825000, 'active'),
('Vehicle5', 'REG005', -1.285000, 36.815000, 'active')
ON CONFLICT (vehicle_name) DO NOTHING;

-- Demo assignments (assign 2 vehicles to drivers)
INSERT INTO assignments (vehicle_id, driver_user_id, status)
VALUES
(1, 2, 'active'),
(2, 3, 'active')
ON CONFLICT (vehicle_id, driver_user_id, status) DO NOTHING;

COMMIT;
