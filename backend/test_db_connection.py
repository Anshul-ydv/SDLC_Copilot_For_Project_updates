#!/usr/bin/env python3
"""
Test database connection and create tables.
"""

import sys
from sqlalchemy import text
from app.database import engine, SessionLocal
from app import models

def test_connection():
    """Test database connection."""
    print("🔍 Testing database connection...")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL!")
            print(f"   Version: {version[:50]}...")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

def create_tables():
    """Create all database tables."""
    print("\n📊 Creating database tables...")
    try:
        models.Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        
        # List created tables
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            
            if tables:
                print("\n📋 Created tables:")
                for table in tables:
                    print(f"   • {table[0]}")
            else:
                print("   No tables found (they may already exist)")
        
        return True
    except Exception as e:
        print(f"❌ Table creation failed: {str(e)}")
        return False

def test_crud():
    """Test basic CRUD operations."""
    print("\n🧪 Testing CRUD operations...")
    db = SessionLocal()
    try:
        # Test: Create a user
        test_user = models.User(
            username="test_user",
            email="test@example.com",
            hashed_password="hashed_password_here",
            role="Business Analyst (BA)"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ Created test user: {test_user.email} (ID: {test_user.id})")
        
        # Test: Read the user
        user = db.query(models.User).filter(models.User.email == "test@example.com").first()
        if user:
            print(f"✅ Read test user: {user.email}")
        
        # Test: Update the user
        user.username = "updated_test_user"
        db.commit()
        print(f"✅ Updated test user: {user.username}")
        
        # Test: Delete the user
        db.delete(user)
        db.commit()
        print(f"✅ Deleted test user")
        
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ CRUD test failed: {str(e)}")
        return False
    finally:
        db.close()

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  PostgreSQL Database Connection Test")
    print("="*60 + "\n")
    
    # Test 1: Connection
    if not test_connection():
        print("\n❌ Database connection failed. Check your DATABASE_URL in .env")
        sys.exit(1)
    
    # Test 2: Create tables
    if not create_tables():
        print("\n❌ Table creation failed.")
        sys.exit(1)
    
    # Test 3: CRUD operations
    if not test_crud():
        print("\n⚠️  CRUD test failed, but connection and tables are OK.")
    
    print("\n" + "="*60)
    print("  ✅ Database is ready to use!")
    print("="*60 + "\n")
    
    print("Next steps:")
    print("  1. Start the server: python -m uvicorn main:app --reload")
    print("  2. Test JWT auth: python test_jwt_auth.py")
    print("  3. Visit Swagger UI: http://localhost:8000/docs\n")

if __name__ == "__main__":
    main()
