"""
Reset database schema to match updated models without foreign key constraints.
This will drop all tables and recreate them.
"""
from app.database import engine, Base
from app import models
from sqlalchemy import text

def reset_database():
    print("⚠️  WARNING: This will drop all existing tables and data!")
    print("Dropping all tables with CASCADE...")
    
    try:
        # Drop all tables with CASCADE to handle dependencies
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS document_feedback CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS documents CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS chat_messages CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS chat_sessions CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
            conn.commit()
        
        print("✓ All tables dropped successfully")
        
        # Recreate all tables with new schema (no foreign keys)
        Base.metadata.create_all(bind=engine)
        print("✓ All tables recreated successfully")
        
        print("\n✅ Database reset complete!")
        print("\nNew schema (NO FOREIGN KEY CONSTRAINTS):")
        print("  - users")
        print("  - chat_sessions (no FK to users)")
        print("  - chat_messages (no FK to chat_sessions)")
        print("  - documents (no FK to users or chat_sessions)")
        print("  - document_feedback (no FK to documents or users)")
        
    except Exception as e:
        print(f"✗ Error resetting database: {e}")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE RESET SCRIPT")
    print("=" * 60)
    reset_database()
