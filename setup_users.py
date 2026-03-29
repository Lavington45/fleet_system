from werkzeug.security import generate_password_hash
import mysql.connector

# Connect to database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="fleet_system"
)
cursor = conn.cursor()

# Update demo users with hashed passwords
cursor.execute(
    "UPDATE users SET password_hash=%s WHERE username='admin'",
    (generate_password_hash('admin123'),)
)
cursor.execute(
    "UPDATE users SET password_hash=%s WHERE username='driver1'",
    (generate_password_hash('driver123'),)
)

conn.commit()
cursor.close()
conn.close()

print("✅ Users updated successfully!")
print("Admin: admin / admin123")
print("Driver: driver1 / driver123")