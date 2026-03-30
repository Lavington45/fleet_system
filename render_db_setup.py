#!/usr/bin/env python3
"""
Render Database Setup Script
Run this locally to test database connection and setup
"""

import psycopg2
import os
import sys

def test_connection():
    """Test database connection"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL environment variable not set")
            return False

        print(f"🔗 Connecting to: {database_url.split('@')[1] if '@' in database_url else 'database'}")

        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connected to PostgreSQL: {version[0][:50]}...")

        # Check if tables exist
        cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()

        if tables:
            print(f"📋 Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("⚠️  No tables found. Run schema.sql first!")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def setup_demo_users():
    """Set up demo user passwords"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not set")
            return

        from werkzeug.security import generate_password_hash

        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Update passwords
        demo_users = [
            ('admin', 'admin123'),
            ('driver1', 'driver123'),
            ('driver2', 'driver123')
        ]

        for username, password in demo_users:
            hashed = generate_password_hash(password)
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE username = %s",
                (hashed, username)
            )
            print(f"✅ Updated password for {username}")

        conn.commit()
        cursor.close()
        conn.close()

        print("\n🎯 Demo credentials:")
        print("   Admin: admin / admin123")
        print("   Driver 1: driver1 / driver123")
        print("   Driver 2: driver2 / driver123")

    except Exception as e:
        print(f"❌ Failed to setup users: {e}")

if __name__ == "__main__":
    print("🚀 Render Database Setup Tool")
    print("=" * 40)

    if len(sys.argv) > 1 and sys.argv[1] == "users":
        print("\n👤 Setting up demo users...")
        setup_demo_users()
    else:
        print("\n🔍 Testing database connection...")
        if test_connection():
            print("\n💡 To setup demo users, run: python render_db_setup.py users")
        else:
            print("\n💡 Make sure DATABASE_URL is set correctly")
            print("   Example: export DATABASE_URL='postgresql://user:pass@host:5432/db'")