"""
Script to seed the database with an admin user.
Run this once to create the admin account.
"""

from app.database import SessionLocal
from app.models import User
from app.utils.auth_utils import get_password_hash

def seed_admin():
    db = SessionLocal()
    
    # Check if admin already exists
    admin = db.query(User).filter(User.email == "admin1@hsbc.com").first()
    if admin:
        print("Admin user already exists!")
        db.close()
        return
    
    # Create admin user
    admin_user = User(
        email="admin1@hsbc.com",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        roles=["Business Analyst (BA)", "Functional BA (FBA)", "QA / Tester"],
        is_admin=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    print(f"✅ Admin user created successfully!")
    print(f"Email: admin1@hsbc.com")
    print(f"Password: admin123")
    print(f"User ID: {admin_user.id}")
    
    db.close()

if __name__ == "__main__":
    seed_admin()
