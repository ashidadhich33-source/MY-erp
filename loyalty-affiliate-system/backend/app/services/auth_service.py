"""
Authentication Service

Handles user authentication, JWT token management, password hashing,
and security-related operations.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..core.config import settings
from ..models import User, UserRole, UserStatus
from ..core.security import verify_password, get_password_hash
from ..utils.email import send_password_reset_email


class AuthService:
    """
    Service for handling authentication operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return get_password_hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return verify_password(plain_password, hashed_password)

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user with email and password.

        Returns:
            Dict containing user info and tokens
        """
        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            raise ValueError("Invalid credentials")

        if not self.verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")

        if user.status != UserStatus.ACTIVE:
            raise ValueError("Account is inactive")

        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()

        # Create tokens
        access_token = self.create_access_token(
            user_id=user.id,
            role=user.role.value
        )

        refresh_token = self.create_refresh_token(user.id)

        return {
            "user_id": user.id,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role.value,
                "status": user.status.value
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    def create_access_token(self, user_id: int, role: str, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode = {
            "sub": str(user_id),
            "role": role,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow()
        }

        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, user_id: int) -> str:
        """Create a JWT refresh token."""
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }

        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

            # Check if it's a refresh token (shouldn't be used for access)
            if payload.get("type") == "refresh":
                return payload

            # For access tokens, validate user still exists
            user_id = payload.get("sub")
            if user_id:
                user = self.db.query(User).filter(User.id == int(user_id)).first()
                if user and user.status == UserStatus.ACTIVE:
                    return payload

            return None
        except JWTError:
            return None

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an access token using a refresh token."""
        payload = self.verify_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")

        user_id = int(payload["sub"])
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user or user.status != UserStatus.ACTIVE:
            raise ValueError("Invalid refresh token")

        # Create new tokens
        access_token = self.create_access_token(
            user_id=user.id,
            role=user.role.value
        )
        new_refresh_token = self.create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    def change_password(self, user_id: int, current_password: str, new_password: str) -> Dict[str, str]:
        """Change user password."""
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            raise ValueError("User not found")

        if not self.verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")

        user.password_hash = self.hash_password(new_password)
        self.db.commit()

        return {"message": "Password changed successfully"}

    def request_password_reset(self, email: str) -> Dict[str, str]:
        """Request password reset for a user."""
        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            # Don't reveal if email exists for security
            return {"message": "Password reset email sent", "reset_token": None}

        # Generate reset token
        reset_token = self.create_refresh_token(user.id)  # Reuse refresh token logic
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
        self.db.commit()

        # Send email (in real implementation)
        # send_password_reset_email(email, reset_token)

        return {"message": "Password reset email sent", "reset_token": reset_token}

    def confirm_password_reset(self, reset_token: str, new_password: str) -> Dict[str, str]:
        """Confirm password reset with token."""
        try:
            payload = jwt.decode(reset_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = int(payload["sub"])

            user = self.db.query(User).filter(User.id == user_id).first()

            if not user or not user.reset_token or user.reset_token != reset_token:
                raise ValueError("Invalid or expired reset token")

            if user.reset_token_expires < datetime.utcnow():
                raise ValueError("Invalid or expired reset token")

            # Update password and clear reset token
            user.password_hash = self.hash_password(new_password)
            user.reset_token = None
            user.reset_token_expires = None
            self.db.commit()

            return {"message": "Password reset successfully"}

        except JWTError:
            raise ValueError("Invalid or expired reset token")

    def has_permission(self, user_id: int, permission: str) -> bool:
        """Check if user has a specific permission."""
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            return False

        # Simple permission mapping - in real implementation, use roles/permissions table
        if user.role == UserRole.ADMIN:
            return permission in ["admin_access", "customer_access", "affiliate_access"]

        if user.role == UserRole.CUSTOMER:
            return permission in ["customer_access"]

        if user.role == UserRole.AFFILIATE:
            return permission in ["affiliate_access", "customer_access"]

        return False

    def get_user_by_token(self, token: str) -> User:
        """Get user by JWT token."""
        payload = self.verify_token(token)

        if not payload:
            raise ValueError("Invalid token")

        user_id = int(payload["sub"])
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            raise ValueError("User not found")

        return user

    def logout_user(self, user_id: int) -> Dict[str, str]:
        """Logout user (invalidate tokens)."""
        # In a real implementation, you might want to maintain a blacklist
        # For now, just return success
        return {"message": "User logged out successfully"}

    def get_user_permissions(self, user_id: int) -> list:
        """Get list of user permissions."""
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            return []

        # Return permissions based on role
        if user.role == UserRole.ADMIN:
            return ["admin_access", "customer_access", "affiliate_access", "system_config"]

        if user.role == UserRole.CUSTOMER:
            return ["customer_access", "profile_edit"]

        if user.role == UserRole.AFFILIATE:
            return ["affiliate_access", "customer_access", "profile_edit"]

        return []

    def create_user(self, name: str, email: str, phone: str, password: str, role: UserRole = UserRole.CUSTOMER) -> User:
        """Create a new user."""
        hashed_password = self.hash_password(password)

        user = User(
            name=name,
            email=email,
            phone=phone,
            password_hash=hashed_password,
            role=role,
            status=UserStatus.ACTIVE,
            email_verified=False,
            phone_verified=False
        )

        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("User with this email or phone already exists")

    def _validate_password_strength(self, password: str) -> bool:
        """Validate password strength (minimum requirements)."""
        if len(password) < 8:
            return False

        # Check for at least one uppercase, lowercase, number
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        return has_upper and has_lower and has_digit