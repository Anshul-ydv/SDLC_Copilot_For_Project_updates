"""
Script to drop the old 'role' column from users table.
"""

from sqlalchemy import text
from app.database import engine

def drop_role_column():
    with engine.connect() as connection:
        # Check if role column exists
        result = connection.execute(
            text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name='users' AND column_name='role'
            """)
        )
        
        if not result.fetchone():
            print("✅ 'role' column doesn't exist. Nothing to drop.")
            connection.close()
            return
        
        print("🔄 Dropping 'role' column...")
        connection.execute(text("ALTER TABLE users DROP COLUMN role"))
        connection.commit()
        print("✅ 'role' column dropped successfully!")

if __name__ == "__main__":
    try:
        drop_role_column()
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
