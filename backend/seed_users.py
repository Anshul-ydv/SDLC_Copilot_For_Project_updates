"""
Seed script to create mock users in the database.
Run this once to populate the users table with test accounts.
"""
from app.database import SessionLocal
from app.models import User
from app.utils.auth_utils import get_password_hash

def seed_users():
    db = SessionLocal()
    
    # Check if users already exist
    existing_users = db.query(User).filter(User.id.in_(["u1", "u2", "u3"])).all()
    if existing_users:
        print(f"✓ Found {len(existing_users)} existing users. Skipping seed.")
        db.close()
        return
    
    # Mock users from auth.py
    mock_users = [
        {
            "id": "u1",
            "username": "ba_user",
            "email": "ba@xyz.com",
            "password": "password123",
            "role": "Business Analyst (BA)"
        },
        {
            "id": "u2",
            "username": "fba_user",
            "email": "fba@xyz.com",
            "password": "password123",
            "role": "Functional BA (FBA)"
        },
        {
            "id": "u3",
            "username": "qa_user",
            "email": "qa@xyz.com",
            "password": "password123",
            "role": "QA / Tester"
        }
    ]
    
    try:
        for user_data in mock_users:
            user = User(
                id=user_data["id"],
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"]
            )
            db.add(user)
        
        db.commit()
        print("✓ Successfully seeded 3 mock users:")
        print("  - ba@xyz.com (Business Analyst)")
        print("  - fba@xyz.com (Functional BA)")
        print("  - qa@xyz.com (QA / Tester)")
        print("\nPassword for all: password123")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error seeding users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Seeding database with mock users...")
    seed_users()
