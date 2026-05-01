from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import timedelta
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..utils.auth_utils import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Available roles
AVAILABLE_ROLES = [
    "Business Analyst (BA)",
    "Functional BA (FBA)",
    "QA / Tester"
]


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    username: str
    roles: List[str] = Field(default=["Business Analyst (BA)"])
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123",
                "username": "john_doe",
                "roles": ["Business Analyst (BA)", "Functional BA (FBA)"]
            }
        }


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    username: Optional[str] = None
    roles: Optional[List[str]] = None


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    roles: List[str]
    is_admin: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminLoginResponse(BaseModel):
    access_token: str = Field(alias="token")
    token_type: str
    user_id: str
    email: str
    is_admin: bool
    expires_in: int
    
    class Config:
        populate_by_name = True


def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Verify that the current user is an admin."""
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.post("/login", response_model=AdminLoginResponse, response_model_by_alias=True)
def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    """Admin login endpoint."""
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.id,
            "email": user.email,
            "is_admin": user.is_admin,
            "roles": user.roles
        },
        expires_delta=access_token_expires
    )
    
    return AdminLoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        is_admin=user.is_admin,
        expires_in=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db),
    admin_user: dict = Depends(get_admin_user)
):
    """Create a new user (admin only)."""
    # Validate roles
    for role in request.roles:
        if role not in AVAILABLE_ROLES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {role}. Available roles: {', '.join(AVAILABLE_ROLES)}"
            )
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == request.email) | (User.username == request.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    new_user = User(
        email=request.email,
        username=request.username,
        hashed_password=get_password_hash(request.password),
        roles=request.roles,
        is_admin=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
        roles=new_user.roles,
        is_admin=new_user.is_admin,
        created_at=new_user.created_at.isoformat(),
        updated_at=new_user.updated_at.isoformat()
    )


@router.get("/users", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    admin_user: dict = Depends(get_admin_user)
):
    """List all users (admin only)."""
    users = db.query(User).all()
    return [
        UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            roles=user.roles,
            is_admin=user.is_admin,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat()
        )
        for user in users
    ]


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin_user: dict = Depends(get_admin_user)
):
    """Get a specific user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        roles=user.roles,
        is_admin=user.is_admin,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat()
    )


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    request: UpdateUserRequest,
    db: Session = Depends(get_db),
    admin_user: dict = Depends(get_admin_user)
):
    """Update a user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update email if provided
    if request.email:
        existing = db.query(User).filter(
            (User.email == request.email) & (User.id != user_id)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        user.email = request.email
    
    # Update username if provided
    if request.username:
        existing = db.query(User).filter(
            (User.username == request.username) & (User.id != user_id)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already in use"
            )
        user.username = request.username
    
    # Update password if provided
    if request.password:
        user.hashed_password = get_password_hash(request.password)
    
    # Update roles if provided
    if request.roles:
        for role in request.roles:
            if role not in AVAILABLE_ROLES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid role: {role}. Available roles: {', '.join(AVAILABLE_ROLES)}"
                )
        user.roles = request.roles
    
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        roles=user.roles,
        is_admin=user.is_admin,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat()
    )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin_user: dict = Depends(get_admin_user)
):
    """Delete a user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting the admin user
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete admin users"
        )
    
    db.delete(user)
    db.commit()


@router.get("/roles")
def get_available_roles(admin_user: dict = Depends(get_admin_user)):
    """Get list of available roles."""
    return {"roles": AVAILABLE_ROLES}
