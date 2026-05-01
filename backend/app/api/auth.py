from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from datetime import timedelta
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..utils.auth_utils import (
    create_access_token,
    get_current_user,
    verify_password,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str = Field(alias="token")
    token_type: str
    roles: list
    user_id: str
    email: str
    expires_in: int
    
    class Config:
        populate_by_name = True


class UserInfoResponse(BaseModel):
    user_id: str
    email: str
    roles: list


MOCK_USERS = {
    "ba@hsbc.com": {
        "password": "password123",
        "roles": ["Business Analyst (BA)"],
        "id": "u1"
    },
    "fba@hsbc.com": {
        "password": "password123",
        "roles": ["Functional BA (FBA)"],
        "id": "u2"
    },
    "qa@hsbc.com": {
        "password": "password123",
        "roles": ["QA / Tester"],
        "id": "u3"
    }
}


@router.post("/login", response_model=LoginResponse, response_model_by_alias=True)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT access token."""
    # First try database
    user = db.query(User).filter(User.email == request.email).first()
    
    if user and verify_password(request.password, user.hashed_password):
        access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user.id,
                "email": user.email,
                "roles": user.roles,
                "is_admin": user.is_admin
            },
            expires_delta=access_token_expires
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            roles=user.roles,
            user_id=user.id,
            email=request.email,
            expires_in=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Fallback to mock users for backward compatibility
    mock_user = MOCK_USERS.get(request.email)
    if mock_user and mock_user["password"] == request.password:
        access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": mock_user["id"],
                "email": request.email,
                "roles": mock_user["roles"],
                "is_admin": False
            },
            expires_delta=access_token_expires
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            roles=mock_user["roles"],
            user_id=mock_user["id"],
            email=request.email,
            expires_in=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.get("/me", response_model=UserInfoResponse)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information from JWT token."""
    return UserInfoResponse(
        user_id=current_user.get("sub"),
        email=current_user.get("email"),
        roles=current_user.get("roles", [])
    )


@router.post("/verify-token")
def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify if the provided JWT token is valid."""
    return {
        "valid": True,
        "user_id": current_user.get("sub"),
        "email": current_user.get("email"),
        "roles": current_user.get("roles", []),
        "is_admin": current_user.get("is_admin", False)
    }
