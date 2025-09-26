from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from ...core.database import get_db
from ...core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    verify_token,
)
from ...core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    role: str = "customer"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    role: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


@router.post("/register", response_model=UserResponse, summary="Register new user")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user account.

    - **name**: Full name of the user
    - **email**: Valid email address
    - **phone**: Phone number
    - **password**: Password (min 8 characters)
    - **role**: User role (admin, customer, affiliate)
    """
    # For now, we'll create a mock user since we don't have database models yet
    # In Phase 3, this will be replaced with actual database operations

    user = {
        "id": 1,
        "name": user_data.name,
        "email": user_data.email,
        "phone": user_data.phone,
        "role": user_data.role,
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z"
    }

    return user


@router.post("/login", response_model=Token, summary="Login user")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens.

    - **username**: User email address
    - **password**: User password
    """
    # For now, we'll use mock authentication
    # In Phase 3, this will be replaced with actual database authentication

    if form_data.username == "admin@example.com" and form_data.password == "admin123":
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject="1", expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(subject="1")

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    # Mock user for testing
    if form_data.username == "user@example.com" and form_data.password == "user123":
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject="2", expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(subject="2")

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/logout", summary="Logout user")
async def logout(token: str = Depends(oauth2_scheme)):
    """
    Logout user and invalidate tokens.

    This endpoint will be enhanced in Phase 3 with proper token blacklisting.
    """
    # For now, just return success
    # In Phase 3, this will blacklist the token
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse, summary="Get current user")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get current authenticated user information.

    Returns user details for the authenticated user.
    """
    # For now, return mock user based on token
    # In Phase 3, this will validate the token and fetch user from database

    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Mock user data - replace with database query in Phase 3
    if payload == "1":
        return {
            "id": 1,
            "name": "Admin User",
            "email": "admin@example.com",
            "phone": "+1234567890",
            "role": "admin",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
    else:
        return {
            "id": 2,
            "name": "John Doe",
            "email": "user@example.com",
            "phone": "+1234567891",
            "role": "customer",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        }


@router.post("/refresh", response_model=Token, summary="Refresh access token")
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token.

    - **refresh_token**: Valid refresh token
    """
    # For now, create new tokens
    # In Phase 3, this will validate the refresh token and generate new ones

    payload = verify_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=payload, expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(subject=payload)

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )