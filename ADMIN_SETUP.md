# Admin Portal Setup Guide

## Overview

The SDLC Copilot now includes a comprehensive Admin Portal for managing users and their roles. Admins can create new users, edit existing users, assign multiple roles to a single user, and manage user credentials.

## Features

✅ **User Management**
- Create new users with email, username, and password
- Edit existing users (email, username, password)
- Delete users (except admin users)
- View all users in the system

✅ **Role Management**
- Assign multiple roles to a single user
- Available roles:
  - Business Analyst (BA)
  - Functional BA (FBA)
  - QA / Tester
- Users can have any combination of roles

✅ **Admin Authentication**
- Separate admin login with JWT tokens
- Admin-only access control
- Session-based authentication

## Quick Start

### 1. Access the Admin Portal

Navigate to: **http://localhost:3000/admin**

### 2. Login with Admin Credentials

```
Email: admin1@hsbc.com
Password: admin123
```

### 3. Manage Users

Once logged in, you can:
- **Create New User**: Click "Create New User" button
- **Edit User**: Click "Edit" button next to any user
- **Delete User**: Click "Delete" button (not available for admin users)
- **View All Users**: See complete list with roles and creation date

## Admin Portal Features

### Create New User

1. Click **"Create New User"** button
2. Fill in the form:
   - **Email**: User's email address (must be unique)
   - **Username**: User's username (must be unique)
   - **Password**: Initial password for the user
   - **Roles**: Select one or more roles (checkbox selection)
3. Click **"Create User"** to save

### Edit User

1. Click **"Edit"** button next to the user
2. Update any of the following:
   - **Email**: Change user's email
   - **Username**: Change user's username
   - **Password**: Leave blank to keep current password, or enter new password
   - **Roles**: Add or remove roles
3. Click **"Save"** to apply changes

### Delete User

1. Click **"Delete"** button next to the user
2. Confirm the deletion in the popup
3. User will be permanently removed from the system

**Note**: Admin users cannot be deleted through the UI.

## API Endpoints

### Admin Authentication

```bash
POST /api/admin/login
Content-Type: application/json

{
  "email": "admin1@hsbc.com",
  "password": "admin123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user_id": "...",
  "email": "admin1@hsbc.com",
  "is_admin": true,
  "expires_in": 30
}
```

### Create User

```bash
POST /api/admin/users
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "password123",
  "roles": ["Business Analyst (BA)", "Functional BA (FBA)"]
}

Response:
{
  "id": "user-id",
  "email": "user@example.com",
  "username": "john_doe",
  "roles": ["Business Analyst (BA)", "Functional BA (FBA)"],
  "is_admin": false,
  "created_at": "2026-05-01T08:00:00",
  "updated_at": "2026-05-01T08:00:00"
}
```

### List All Users

```bash
GET /api/admin/users
Authorization: Bearer {admin_token}

Response:
[
  {
    "id": "user-id",
    "email": "user@example.com",
    "username": "john_doe",
    "roles": ["Business Analyst (BA)", "Functional BA (FBA)"],
    "is_admin": false,
    "created_at": "2026-05-01T08:00:00",
    "updated_at": "2026-05-01T08:00:00"
  },
  ...
]
```

### Get Specific User

```bash
GET /api/admin/users/{user_id}
Authorization: Bearer {admin_token}

Response:
{
  "id": "user-id",
  "email": "user@example.com",
  "username": "john_doe",
  "roles": ["Business Analyst (BA)", "Functional BA (FBA)"],
  "is_admin": false,
  "created_at": "2026-05-01T08:00:00",
  "updated_at": "2026-05-01T08:00:00"
}
```

### Update User

```bash
PUT /api/admin/users/{user_id}
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "email": "newemail@example.com",
  "username": "new_username",
  "password": "newpassword123",
  "roles": ["Business Analyst (BA)", "QA / Tester"]
}

Response:
{
  "id": "user-id",
  "email": "newemail@example.com",
  "username": "new_username",
  "roles": ["Business Analyst (BA)", "QA / Tester"],
  "is_admin": false,
  "created_at": "2026-05-01T08:00:00",
  "updated_at": "2026-05-01T08:00:00"
}
```

### Delete User

```bash
DELETE /api/admin/users/{user_id}
Authorization: Bearer {admin_token}

Response: 204 No Content
```

### Get Available Roles

```bash
GET /api/admin/roles
Authorization: Bearer {admin_token}

Response:
{
  "roles": [
    "Business Analyst (BA)",
    "Functional BA (FBA)",
    "QA / Tester"
  ]
}
```

## Database Schema

### Users Table

The users table has been updated to support multiple roles:

```sql
CREATE TABLE users (
  id VARCHAR PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  username VARCHAR UNIQUE NOT NULL,
  hashed_password VARCHAR NOT NULL,
  roles JSON NOT NULL DEFAULT '["Business Analyst (BA)"]',
  is_admin BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Changes:**
- `role` (single) → `roles` (JSON array) - supports multiple roles
- Added `is_admin` column for admin flag
- Added `updated_at` column for tracking modifications

## Migration Scripts

The following migration scripts were used to update the database:

1. **migrate_db.py** - Adds new columns and migrates data
2. **drop_role_column.py** - Removes the old `role` column
3. **seed_admin_direct.py** - Creates the initial admin user

To run migrations manually:

```bash
cd backend
source ../.venv/bin/activate

# Run migration
python migrate_db.py

# Drop old role column
python drop_role_column.py

# Seed admin user
python seed_admin_direct.py
```

## User Login with Multiple Roles

When a user with multiple roles logs in, they receive all their roles in the JWT token:

```json
{
  "sub": "user-id",
  "email": "user@example.com",
  "roles": ["Business Analyst (BA)", "Functional BA (FBA)"],
  "is_admin": false,
  "exp": 1234567890
}
```

The frontend can use these roles to:
- Display role-specific UI elements
- Control access to role-specific features
- Show all available roles for the user

## Security Considerations

✅ **Password Security**
- Passwords are hashed using bcrypt
- Passwords are never stored in plain text
- Passwords are never returned in API responses

✅ **Admin Access Control**
- Only users with `is_admin=true` can access admin endpoints
- Admin endpoints require valid JWT token
- All admin actions are logged (can be extended)

✅ **Data Validation**
- Email validation (must be valid email format)
- Username uniqueness validation
- Role validation (only allowed roles accepted)
- Email uniqueness validation

## Troubleshooting

### "Admin access required" error
- Ensure you're logged in with an admin account
- Check that the token is valid and not expired
- Verify the Authorization header is correctly formatted: `Bearer {token}`

### "User with this email already exists"
- Email must be unique in the system
- Try a different email address

### "Invalid role" error
- Only these roles are allowed:
  - Business Analyst (BA)
  - Functional BA (FBA)
  - QA / Tester
- Check spelling and capitalization

### Cannot delete admin user
- Admin users cannot be deleted through the UI
- This is a security feature to prevent accidental deletion of all admins

## Future Enhancements

- [ ] Bulk user import (CSV)
- [ ] User activity logs
- [ ] Role-based permissions customization
- [ ] User deactivation (soft delete)
- [ ] Password reset functionality
- [ ] Two-factor authentication for admin accounts
- [ ] Audit trail for all admin actions
- [ ] User groups/teams management

## Support

For issues or questions about the Admin Portal, please refer to:
- API Documentation: http://localhost:8000/docs
- Main README: README.md
- Backend Admin API: backend/app/api/admin.py
- Frontend Admin Page: frontend/src/app/admin/page.tsx
