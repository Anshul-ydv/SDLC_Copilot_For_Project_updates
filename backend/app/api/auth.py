# Mock auth login for testing purpose, as JWT isnt setup yet
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter()

# Schema for Login
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    role: str
    user_id: str

# Mock Database for Users
MOCK_USERS = {
    "ba@hsbc.com": {"password": "password123", "role": "Business Analyst (BA)", "id": "u1"},
    "fba@hsbc.com": {"password": "password123", "role": "Functional BA (FBA)", "id": "u2"},
    "qa@hsbc.com": {"password": "password123", "role": "QA / Tester", "id": "u3"}
}

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    user = MOCK_USERS.get(request.email)
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # optional In a real app, generate a JWT here
    dummy_jwt = f"mock-jwt-token-for-{user['role']}"
    
    return LoginResponse(
        token=dummy_jwt,
        role=user["role"],
        user_id=user["id"]
    )
