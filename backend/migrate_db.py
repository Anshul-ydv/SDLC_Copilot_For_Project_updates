"""
Migration script to update the users table schema.
This adds the 'roles' and 'is_admin' columns and migrates data from 'role' column.
"""

import os
from sqlalchemy import text
from app.database import engine

def migrate():
    with engine.connect() as connection:
        # Check if roles column exists
        result = connection.execute(
            text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name='users' AND column_name='roles'
            """)
        )
        
        if result.fetchone():
            print("✅ 'roles' column already exists. Skipping migration.")
            connection.close()
            return
        
        print("🔄 Starting database migration...")
        
        # Add roles column (JSON type)
        print("  - Adding 'roles' column...")
        connection.execute(text("""
            ALTER TABLE users ADD COLUMN roles JSON DEFAULT '["Business Analyst (BA)"]'
        """))
        
        # Add is_admin column
        print("  - Adding 'is_admin' column...")
        connection.execute(text("""
            ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE
        """))
        
        # Add updated_at column if it doesn't exist
        result = connection.execute(
            text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name='users' AND column_name='updated_at'
            """)
        )
        
        if not result.fetchone():
            print("  - Adding 'updated_at' column...")
            connection.execute(text("""
                ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """))
        
        # Migrate data from role to roles (if role column exists)
        result = connection.execute(
            text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name='users' AND column_name='role'
            """)
        )
        
        if result.fetchone():
            print("  - Migrating data from 'role' to 'roles'...")
            connection.execute(text("""
                UPDATE users 
                SET roles = jsonb_build_array(role)
                WHERE role IS NOT NULL
            """))
        
        connection.commit()
        print("✅ Migration completed successfully!")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
