"""
Script to seed the database with an admin user using direct SQL.
"""

import uuid
from sqlalchemy import text
from app.database import engine
from app.utils.auth_utils import get_password_hash

def seed_admin():
    with engine.connect() as connection:
        # Check if admin already exists
        result = connection.execute(
            text("SELECT id FROM users WHERE email = 'admin1@hsbc.com'")
        )
        
        if result.fetchone():
            print("✅ Admin user already exists!")
            connection.close()
            return
        
        # Create admin user
        admin_id = str(uuid.uuid4())
        hashed_pwd = get_password_hash("admin123")
        
        connection.execute(text("""
            INSERT INTO users (id, email, username, hashed_password, roles, is_admin, created_at, updated_at)
            VALUES (:id, :email, :username, :password, :roles, :is_admin, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """), {
            "id": admin_id,
            "email": "admin1@hsbc.com",
            "username": "admin",
            "password": hashed_pwd,
            "roles": '["Business Analyst (BA)", "Functional BA (FBA)", "QA / Tester"]',
            "is_admin": True
        })
        
        connection.commit()
        
        print(f"✅ Admin user created successfully!")
        print(f"Email: admin1@hsbc.com")
        print(f"Password: admin123")
        print(f"User ID: {admin_id}")

if __name__ == "__main__":
    try:
        seed_admin()
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
