# JWT Authentication Implementation

## Overview
This project now uses **JWT (JSON Web Token)** authentication for secure API access. The implementation uses mock users for development/testing purposes.

## Features
- ✅ JWT token generation with 30-minute expiration
- ✅ Secure token validation and verification
- ✅ Role-based access control (RBAC) support
- ✅ Protected endpoints with Bearer token authentication
- ✅ Mock user database for testing

---

## Configuration

### Environment Variables
Add these to your `.env` file:

```env
JWT_SECRET_KEY=8e47e73bdc74debfab72428f1560ba92afeffa6e1b18c8649ca8997f3690f3fe
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Important:** Change `JWT_SECRET_KEY` in production! Generate a new one with:
```bash
openssl rand -hex 32
```

---

## Mock Users

For testing, use these credentials:

| Email | Password | Role |
|-------|----------|------|
| `ba@hsbc.com` | `password123` | Business Analyst (BA) |
| `fba@hsbc.com` | `password123` | Functional BA (FBA) |
| `qa@hsbc.com` | `password123` | QA / Tester |

---

## API Endpoints

### 1. Login (Get JWT Token)
**POST** `/api/auth/login`

**Request:**
```json
{
  "email": "ba@hsbc.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "Business Analyst (BA)",
  "user_id": "u1",
  "email": "ba@hsbc.com",
  "expires_in": 30
}
```

### 2. Get Current User Info
**GET** `/api/auth/me`

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Response:**
```json
{
  "user_id": "u1",
  "email": "ba@hsbc.com",
  "role": "Business Analyst (BA)"
}
```

### 3. Verify Token
**POST** `/api/auth/verify-token`

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Response:**
```json
{
  "valid": true,
  "user_id": "u1",
  "email": "ba@hsbc.com",
  "role": "Business Analyst (BA)"
}
```

---

## Usage Examples

### Using cURL

#### Login:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "ba@hsbc.com", "password": "password123"}'
```

#### Get User Info:
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### Using Python Requests

```python
import requests

# 1. Login
login_response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"email": "ba@hsbc.com", "password": "password123"}
)
token = login_response.json()["access_token"]

# 2. Use token for authenticated requests
headers = {"Authorization": f"Bearer {token}"}
user_info = requests.get(
    "http://localhost:8000/api/auth/me",
    headers=headers
)
print(user_info.json())
```

### Using JavaScript/Fetch

```javascript
// 1. Login
const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'ba@hsbc.com',
    password: 'password123'
  })
});
const { access_token } = await loginResponse.json();

// 2. Use token for authenticated requests
const userInfo = await fetch('http://localhost:8000/api/auth/me', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const user = await userInfo.json();
console.log(user);
```

---

## Protecting Your Endpoints

### Basic Protection (Any Authenticated User)

```python
from fastapi import Depends
from app.utils.auth_utils import get_current_user

@router.get("/protected-endpoint")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {
        "message": "This is protected",
        "user": current_user
    }
```

### Role-Based Protection

```python
from fastapi import Depends
from app.utils.auth_utils import require_role

@router.post("/admin-only")
async def admin_route(
    current_user: dict = Depends(require_role(["Business Analyst (BA)"]))
):
    return {"message": "Only BAs can access this"}

@router.post("/qa-or-fba")
async def qa_fba_route(
    current_user: dict = Depends(require_role(["QA / Tester", "Functional BA (FBA)"]))
):
    return {"message": "QA or FBA access"}
```

---

## Token Structure

The JWT token contains these claims:

```json
{
  "sub": "u1",                          // User ID
  "email": "ba@hsbc.com",               // User email
  "role": "Business Analyst (BA)",      // User role
  "exp": 1234567890                     // Expiration timestamp
}
```

---

## Error Responses

### 401 Unauthorized (Invalid Credentials)
```json
{
  "detail": "Invalid email or password"
}
```

### 401 Unauthorized (Invalid/Expired Token)
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden (Insufficient Permissions)
```json
{
  "detail": "Access denied. Required roles: Business Analyst (BA)"
}
```

---

## Security Best Practices

1. **Never commit `.env` file** - It contains your secret key
2. **Use HTTPS in production** - Tokens should never be sent over HTTP
3. **Store tokens securely** - Use httpOnly cookies or secure storage in frontend
4. **Rotate secret keys** - Change JWT_SECRET_KEY periodically
5. **Implement token refresh** - For long-lived sessions (future enhancement)
6. **Add rate limiting** - Prevent brute force attacks on login endpoint

---

## Database Setup

You're using PostgreSQL from Neon. The connection is already configured in your `.env`:

```env
DATABASE_URL=postgresql://neondb_owner:npg_aOjMwVit7G6T@ep-nameless-field-anrs6wqz-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

The database tables will be created automatically when you start the server.

---

## Testing

### Run the server:
```bash
cd backend
python -m uvicorn main:app --reload
```

### Test with Swagger UI:
1. Open http://localhost:8000/docs
2. Click on `/api/auth/login` endpoint
3. Click "Try it out"
4. Enter credentials and execute
5. Copy the `access_token` from response
6. Click "Authorize" button at top
7. Enter: `Bearer <your_token>`
8. Now you can test protected endpoints!

---

## Migration to Real Database Users

When ready to move from mock users to database users:

1. Create user registration endpoint
2. Hash passwords using `get_password_hash()` from `auth_utils.py`
3. Store users in the `users` table
4. Update login endpoint to query database instead of MOCK_USERS
5. Verify password using `verify_password()` from `auth_utils.py`

Example:
```python
from app.utils.auth_utils import verify_password, get_password_hash

# Registration
hashed_password = get_password_hash(plain_password)
# Store in database

# Login
user = db.query(User).filter(User.email == email).first()
if not user or not verify_password(plain_password, user.hashed_password):
    raise HTTPException(status_code=401, detail="Invalid credentials")
```

---

## Troubleshooting

### "Could not validate credentials"
- Token expired (30 min default)
- Token malformed
- Wrong JWT_SECRET_KEY in .env

### "Invalid email or password"
- Check credentials match mock users
- Email is case-sensitive

### CORS errors in frontend
- Ensure frontend origin is in CORS allowed origins (already configured for localhost:3000)

---

## Next Steps

- [ ] Implement refresh tokens for extended sessions
- [ ] Add user registration endpoint
- [ ] Migrate from mock users to database users
- [ ] Add password reset functionality
- [ ] Implement rate limiting on login endpoint
- [ ] Add audit logging for authentication events
