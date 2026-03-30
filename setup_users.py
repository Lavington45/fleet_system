from werkzeug.security import generate_password_hash
import psycopg2
import os

# Connect to database
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