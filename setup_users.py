from werkzeug.security import generate_password_hash
import mysql.connector
import os

# Connect to database
try:
    conn = mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', ''),
        database=os.environ.get('DB_NAME', 'fleet_system'),
        autocommit=False
    )
    cursor = conn.cursor(dictionary=True)

    # Update demo users with hashed passwords
    demo_users = [
        ('admin', 'admin123'),
        ('driver1', 'driver123'),
        ('driver2', 'driver123')
    ]

    for username, password in demo_users:
        cursor.execute(
            "UPDATE users SET password_hash=%s WHERE username=%s",
            (generate_password_hash(password), username)
        )

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Users updated successfully!")
    print("Credentials:")
    print("  Admin: admin / admin123")
    print("  Driver 1: driver1 / driver123")
    print("  Driver 2: driver2 / driver123")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nMake sure PostgreSQL is running and environment variables are set:")
    print("  DB_HOST (default: localhost)")
    print("  DB_USER (default: postgres)")
    print("  DB_PASSWORD")
    print("  DB_NAME (default: fleet_system)")