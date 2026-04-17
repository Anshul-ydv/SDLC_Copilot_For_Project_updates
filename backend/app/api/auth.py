from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from ..utils.auth_utils import (
    create_access_token,
    get_current_user,
    require_role,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: str
    email: str
    expires_in: int


class UserInfoResponse(BaseModel):
    user_id: str
    email: str
    role: str


MOCK_USERS = {
    "ba@hsbc.com": {
        "password": "password123",
        "role": "Business Analyst (BA)",
        "id": "u1"
    },
    "fba@hsbc.com": {
        "password": "password123",
        "role": "Functional BA (FBA)",
        "id": "u2"
    },
    "qa@hsbc.com": {
        "password": "password123",
        "role": "QA / Tester",
        "id": "u3"
    }
}


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """Authenticate user and return JWT access token."""
    user = MOCK_USERS.get(request.email)
    if not user or user["password"] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user["id"],
            "email": request.email,
            "role": user["role"]
        },
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        role=user["role"],
        user_id=user["id"],
        email=request.email,
        expires_in=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )


@router.get("/me", response_model=UserInfoResponse)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information from JWT token."""
    return UserInfoResponse(
        user_id=current_user.get("sub"),
        email=current_user.get("email"),
        role=current_user.get("role")
    )


@router.post("/verify-token")
def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify if the provided JWT token is valid."""
    return {
        "valid": True,
        "user_id": current_user.get("sub"),
        "email": current_user.get("email"),
        "role": current_user.get("role")
    }
