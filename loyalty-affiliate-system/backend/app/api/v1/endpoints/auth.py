from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from ...core.database import get_db
from ...core.security import verify_token
from ...core.config import settings
from ...services.auth_service import AuthService
from ...models import UserRole, UserStatus

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

    model_config = {"from_attributes": True}


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
    auth_service = AuthService(db)

    try:
        # Create user (this will handle password hashing)
        user = auth_service.create_user(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            password=user_data.password,
            role=UserRole(user_data.role)
        )

        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            role=user.role.value,
            is_active=user.status == UserStatus.ACTIVE,
            created_at=user.created_at.isoformat() if user.created_at else None
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


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
    auth_service = AuthService(db)

    try:
        result = auth_service.authenticate_user(
            email=form_data.username,
            password=form_data.password
        )

        return Token(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"]
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout", summary="Logout user")
async def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Logout user and invalidate tokens.

    This endpoint will be enhanced in Phase 3 with proper token blacklisting.
    """
    auth_service = AuthService(db)

    try:
        # Get user from token
        user = auth_service.get_user_by_token(token)

        # In a real implementation, you might want to blacklist the token
        result = auth_service.logout_user(user.id)

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse, summary="Get current user")
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information.

    Returns user details for the authenticated user.
    """
    auth_service = AuthService(db)

    try:
        user = auth_service.get_user_by_token(token)

        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            role=user.role.value,
            is_active=user.status == UserStatus.ACTIVE,
            created_at=user.created_at.isoformat() if user.created_at else None
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=Token, summary="Refresh access token")
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.

    - **refresh_token**: Valid refresh token
    """
    auth_service = AuthService(db)

    try:
        result = auth_service.refresh_token(request.refresh_token)

        return Token(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"]
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )