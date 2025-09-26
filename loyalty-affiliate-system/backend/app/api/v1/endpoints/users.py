from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.security import get_password_hash

router = APIRouter()


class UserResponse:
    """Mock user response model for now"""
    def __init__(self, id: int, name: str, email: str, role: str, is_active: bool):
        self.id = id
        self.name = name
        self.email = email
        self.role = role
        self.is_active = is_active


@router.get("/", response_model=List[UserResponse], summary="Get all users")
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all users with pagination.

    - **skip**: Number of users to skip (for pagination)
    - **limit**: Maximum number of users to return
    """
    # Mock data - replace with database query in Phase 3
    users = [
        UserResponse(1, "Admin User", "admin@example.com", "admin", True),
        UserResponse(2, "John Doe", "user@example.com", "customer", True),
        UserResponse(3, "Jane Smith", "jane@example.com", "affiliate", True),
    ]

    return users[skip:skip + limit]


@router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by their ID.

    - **user_id**: The user's unique identifier
    """
    # Mock data - replace with database query in Phase 3
    if user_id == 1:
        return UserResponse(1, "Admin User", "admin@example.com", "admin", True)
    elif user_id == 2:
        return UserResponse(2, "John Doe", "user@example.com", "customer", True)
    elif user_id == 3:
        return UserResponse(3, "Jane Smith", "jane@example.com", "affiliate", True)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.put("/{user_id}", response_model=UserResponse, summary="Update user")
async def update_user(
    user_id: int,
    name: str = None,
    email: str = None,
    role: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """
    Update user information.

    - **user_id**: The user's unique identifier
    - **name**: Updated name (optional)
    - **email**: Updated email (optional)
    - **role**: Updated role (optional)
    - **is_active**: Updated active status (optional)
    """
    # Mock update - replace with database update in Phase 3
    if user_id == 1:
        return UserResponse(
            user_id,
            name or "Admin User",
            email or "admin@example.com",
            role or "admin",
            is_active if is_active is not None else True
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.delete("/{user_id}", summary="Delete user")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user account.

    - **user_id**: The user's unique identifier
    """
    # Mock delete - replace with database delete in Phase 3
    if user_id in [1, 2, 3]:
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.post("/change-password", summary="Change user password")
async def change_password(
    user_id: int,
    current_password: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    """
    Change user password.

    - **user_id**: The user's unique identifier
    - **current_password**: Current password for verification
    - **new_password**: New password to set
    """
    # Mock password change - replace with database update in Phase 3
    if user_id in [1, 2, 3]:
        # In real implementation, verify current_password against stored hash
        # Then hash new_password and store it
        return {"message": "Password changed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )