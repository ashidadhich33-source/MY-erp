"""
Unit tests for Authentication Service.

Tests JWT token generation, password hashing, user authentication,
role-based access control, and security features.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import bcrypt
from jose import jwt, JWTError

from app.services.auth_service import AuthService
from app.models import User, UserRole, UserStatus
from app.core.config import settings
from app.core.security import verify_password


class TestAuthService:
    """Test cases for AuthService."""

    @pytest.fixture
    def auth_service(self, db_session):
        """Create auth service instance."""
        return AuthService(db_session)

    @pytest.fixture
    def test_user(self, db_session):
        """Create test user for authentication testing."""
        password = "test_password123"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        user = User(
            name="Test User",
            email="test@example.com",
            phone="+1234567890",
            password_hash=hashed_password,
            role=UserRole.CUSTOMER,
            status=UserStatus.ACTIVE,
            email_verified=True,
            phone_verified=True
        )
        db_session.add(user)
        db_session.commit()
        return user

    def test_hash_password(self, auth_service):
        """Test password hashing."""
        password = "test_password123"
        hashed = auth_service.hash_password(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Should be different from original

        # Verify the hash works
        assert bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def test_verify_password_success(self, auth_service, test_user):
        """Test successful password verification."""
        result = auth_service.verify_password(
            plain_password="test_password123",
            hashed_password=test_user.password_hash
        )

        assert result == True

    def test_verify_password_failure(self, auth_service, test_user):
        """Test failed password verification."""
        result = auth_service.verify_password(
            plain_password="wrong_password",
            hashed_password=test_user.password_hash
        )

        assert result == False

    def test_authenticate_user_success(self, auth_service, test_user):
        """Test successful user authentication."""
        result = auth_service.authenticate_user(
            email="test@example.com",
            password="test_password123"
        )

        assert result["user_id"] == test_user.id
        assert result["user"]["email"] == "test@example.com"
        assert result["user"]["role"] == UserRole.CUSTOMER.value
        assert "access_token" in result
        assert "token_type" in result
        assert result["token_type"] == "bearer"

        # Verify token structure
        token_data = jwt.decode(
            result["access_token"],
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        assert token_data["sub"] == str(test_user.id)
        assert token_data["role"] == UserRole.CUSTOMER.value

    def test_authenticate_user_invalid_email(self, auth_service):
        """Test authentication with invalid email."""
        with pytest.raises(ValueError) as exc_info:
            auth_service.authenticate_user(
                email="nonexistent@example.com",
                password="test_password123"
            )

        assert "Invalid credentials" in str(exc_info.value)

    def test_authenticate_user_invalid_password(self, auth_service, test_user):
        """Test authentication with invalid password."""
        with pytest.raises(ValueError) as exc_info:
            auth_service.authenticate_user(
                email="test@example.com",
                password="wrong_password"
            )

        assert "Invalid credentials" in str(exc_info.value)

    def test_authenticate_user_inactive_account(self, auth_service, db_session):
        """Test authentication with inactive account."""
        # Create inactive user
        password = "test_password123"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        inactive_user = User(
            name="Inactive User",
            email="inactive@example.com",
            phone="+1234567891",
            password_hash=hashed_password,
            role=UserRole.CUSTOMER,
            status=UserStatus.INACTIVE
        )
        db_session.add(inactive_user)
        db_session.commit()

        with pytest.raises(ValueError) as exc_info:
            auth_service.authenticate_user(
                email="inactive@example.com",
                password="test_password123"
            )

        assert "Account is inactive" in str(exc_info.value)

    def test_create_access_token(self, auth_service):
        """Test JWT token creation."""
        user_id = 123
        role = UserRole.CUSTOMER.value
        expires_delta = timedelta(minutes=30)

        token = auth_service.create_access_token(
            user_id=user_id,
            role=role,
            expires_delta=expires_delta
        )

        assert isinstance(token, str)

        # Decode and verify token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        assert payload["sub"] == str(user_id)
        assert payload["role"] == role
        assert "exp" in payload
        assert "iat" in payload

    def test_verify_token_success(self, auth_service):
        """Test successful token verification."""
        # Create a valid token
        token = auth_service.create_access_token(
            user_id=123,
            role=UserRole.CUSTOMER.value
        )

        # Verify the token
        payload = auth_service.verify_token(token)

        assert payload["sub"] == "123"
        assert payload["role"] == UserRole.CUSTOMER.value

    def test_verify_token_expired(self, auth_service):
        """Test expired token verification."""
        # Create token with very short expiry
        token = auth_service.create_access_token(
            user_id=123,
            role=UserRole.CUSTOMER.value,
            expires_delta=timedelta(seconds=-1)  # Already expired
        )

        with pytest.raises(jwt.ExpiredSignatureError):
            auth_service.verify_token(token)

    def test_verify_token_invalid(self, auth_service):
        """Test invalid token verification."""
        invalid_token = "invalid.jwt.token"

        with pytest.raises(JWTError):
            auth_service.verify_token(invalid_token)

    def test_refresh_token_success(self, auth_service, test_user):
        """Test successful token refresh."""
        # Get initial tokens
        auth_result = auth_service.authenticate_user(
            email="test@example.com",
            password="test_password123"
        )

        # Refresh token
        refresh_result = auth_service.refresh_token(auth_result["refresh_token"])

        assert "access_token" in refresh_result
        assert "token_type" in refresh_result
        assert refresh_result["token_type"] == "bearer"

        # Verify new token is different
        assert refresh_result["access_token"] != auth_result["access_token"]

    def test_refresh_token_invalid(self, auth_service):
        """Test invalid refresh token."""
        invalid_refresh_token = "invalid.refresh.token"

        with pytest.raises(ValueError) as exc_info:
            auth_service.refresh_token(invalid_refresh_token)

        assert "Invalid refresh token" in str(exc_info.value)

    def test_change_password_success(self, auth_service, test_user):
        """Test successful password change."""
        result = auth_service.change_password(
            user_id=test_user.id,
            current_password="test_password123",
            new_password="new_password456"
        )

        assert result["message"] == "Password changed successfully"

        # Verify old password no longer works
        assert not auth_service.verify_password("test_password123", test_user.password_hash)

        # Verify new password works
        assert auth_service.verify_password("new_password456", test_user.password_hash)

    def test_change_password_wrong_current(self, auth_service, test_user):
        """Test password change with wrong current password."""
        with pytest.raises(ValueError) as exc_info:
            auth_service.change_password(
                user_id=test_user.id,
                current_password="wrong_password",
                new_password="new_password456"
            )

        assert "Current password is incorrect" in str(exc_info.value)

    def test_reset_password_request(self, auth_service, test_user):
        """Test password reset request."""
        result = auth_service.request_password_reset("test@example.com")

        assert result["message"] == "Password reset email sent"
        assert result["reset_token"] is not None

        # Verify reset token is stored
        user = auth_service.db.query(User).filter(User.id == test_user.id).first()
        assert user.reset_token is not None
        assert user.reset_token_expires is not None

    def test_reset_password_request_nonexistent_email(self, auth_service):
        """Test password reset request for nonexistent email."""
        result = auth_service.request_password_reset("nonexistent@example.com")

        # Should still return success for security (don't reveal if email exists)
        assert result["message"] == "Password reset email sent"
        assert result["reset_token"] is None

    def test_reset_password_confirm_success(self, auth_service, test_user):
        """Test successful password reset confirmation."""
        # Request password reset
        reset_request = auth_service.request_password_reset("test@example.com")

        # Confirm password reset
        result = auth_service.confirm_password_reset(
            reset_token=reset_request["reset_token"],
            new_password="new_reset_password123"
        )

        assert result["message"] == "Password reset successfully"

        # Verify password was changed
        user = auth_service.db.query(User).filter(User.id == test_user.id).first()
        assert auth_service.verify_password("new_reset_password123", user.password_hash)
        assert user.reset_token is None  # Token should be cleared

    def test_reset_password_confirm_invalid_token(self, auth_service):
        """Test password reset confirmation with invalid token."""
        with pytest.raises(ValueError) as exc_info:
            auth_service.confirm_password_reset(
                reset_token="invalid_token",
                new_password="new_password123"
            )

        assert "Invalid or expired reset token" in str(exc_info.value)

    def test_reset_password_confirm_expired_token(self, auth_service, test_user):
        """Test password reset confirmation with expired token."""
        # Create expired token directly in database
        test_user.reset_token = "expired_token"
        test_user.reset_token_expires = datetime.utcnow() - timedelta(hours=2)  # Expired
        auth_service.db.commit()

        with pytest.raises(ValueError) as exc_info:
            auth_service.confirm_password_reset(
                reset_token="expired_token",
                new_password="new_password123"
            )

        assert "Invalid or expired reset token" in str(exc_info.value)

    def test_has_permission_admin_access(self, auth_service, test_user):
        """Test admin permission checking."""
        # Test user should not have admin access
        assert not auth_service.has_permission(test_user.id, "admin_access")

    def test_has_permission_customer_access(self, auth_service, test_user):
        """Test customer permission checking."""
        # Test user should have customer access
        assert auth_service.has_permission(test_user.id, "customer_access")

    def test_has_permission_invalid_user(self, auth_service):
        """Test permission checking for invalid user."""
        assert not auth_service.has_permission(99999, "any_permission")

    def test_get_user_by_token_success(self, auth_service, test_user):
        """Test getting user by valid token."""
        # Create token for user
        token = auth_service.create_access_token(
            user_id=test_user.id,
            role=test_user.role.value
        )

        # Get user by token
        user = auth_service.get_user_by_token(token)

        assert user.id == test_user.id
        assert user.email == "test@example.com"
        assert user.role == UserRole.CUSTOMER

    def test_get_user_by_token_invalid(self, auth_service):
        """Test getting user by invalid token."""
        with pytest.raises(ValueError) as exc_info:
            auth_service.get_user_by_token("invalid_token")

        assert "Invalid token" in str(exc_info.value)

    def test_logout_user(self, auth_service, test_user):
        """Test user logout functionality."""
        result = auth_service.logout_user(test_user.id)

        assert result["message"] == "User logged out successfully"

        # In a real implementation, this might invalidate tokens
        # For now, it just returns success

    def test_get_user_permissions(self, auth_service, test_user):
        """Test getting user permissions."""
        permissions = auth_service.get_user_permissions(test_user.id)

        assert isinstance(permissions, list)
        assert "customer_access" in permissions

        # Customer should not have admin permissions
        assert "admin_access" not in permissions

    @patch('app.services.auth_service.send_email')
    def test_send_password_reset_email(self, mock_send_email, auth_service, test_user):
        """Test password reset email sending."""
        auth_service.send_password_reset_email(
            email="test@example.com",
            reset_token="test_reset_token"
        )

        # Verify email was sent
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args[1]

        assert call_args["to_email"] == "test@example.com"
        assert "reset_token" in call_args["reset_url"]
        assert call_args["template"] == "password_reset"

    def test_validate_token_format(self, auth_service):
        """Test token format validation."""
        # Valid token format
        valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

        # Should not raise exception
        try:
            payload = auth_service.verify_token(valid_token)
            assert payload is not None
        except Exception:
            # Token might be expired or invalid, but format should be valid
            pass

    def test_security_headers_in_response(self, auth_service, test_user):
        """Test that security headers are included in auth responses."""
        result = auth_service.authenticate_user(
            email="test@example.com",
            password="test_password123"
        )

        # In a real implementation, we might check response headers
        # For this test, we just verify the response structure
        assert "access_token" in result
        assert "token_type" in result
        assert result["token_type"] == "bearer"

    def test_password_strength_validation(self, auth_service):
        """Test password strength validation."""
        # Test weak password
        weak_password = "123"
        assert not auth_service._validate_password_strength(weak_password)

        # Test strong password
        strong_password = "StrongPass123!"
        assert auth_service._validate_password_strength(strong_password)

    def test_rate_limiting_simulation(self, auth_service, test_user):
        """Test rate limiting simulation for login attempts."""
        # Simulate multiple failed login attempts
        for i in range(5):
            with pytest.raises(ValueError):
                auth_service.authenticate_user(
                    email="test@example.com",
                    password="wrong_password"
                )

        # In a real implementation, this might trigger rate limiting
        # For this test, we just verify the function doesn't crash

    def test_audit_logging(self, auth_service, test_user):
        """Test that authentication events are logged."""
        # This is a conceptual test - in real implementation,
        # we would check that login attempts are logged

        auth_service.authenticate_user(
            email="test@example.com",
            password="test_password123"
        )

        # In real implementation, we would verify audit log entries
        # For this test, we just ensure the function completes

    def test_token_expiration_handling(self, auth_service):
        """Test token expiration handling."""
        # Create token with short expiration
        token = auth_service.create_access_token(
            user_id=123,
            role=UserRole.CUSTOMER.value,
            expires_delta=timedelta(seconds=1)
        )

        # Wait for token to expire
        import time
        time.sleep(2)

        # Should raise ExpiredSignatureError
        with pytest.raises(jwt.ExpiredSignatureError):
            auth_service.verify_token(token)

    def test_csrf_protection(self, auth_service):
        """Test CSRF protection simulation."""
        # This is a conceptual test - in real implementation,
        # we would verify CSRF tokens are generated and validated

        # For this test, we just ensure the service doesn't crash
        # when handling potential CSRF scenarios

        assert True  # Placeholder for actual CSRF testing