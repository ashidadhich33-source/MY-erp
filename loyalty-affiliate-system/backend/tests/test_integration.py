"""
Integration Tests for Loyalty & Affiliate System

Tests the complete flow from API endpoints through services to database operations.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.main import app
from app.models import User, UserRole, UserStatus, Customer, CustomerTier
from app.services.auth_service import AuthService
from app.services.customer_service import CustomerService
from app.services.loyalty_service import LoyaltyService


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Create database session for testing."""
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    auth_service = AuthService(db_session)

    user = auth_service.create_user(
        name="Test User",
        email="test@example.com",
        phone="+1234567890",
        password="test_password123",
        role=UserRole.CUSTOMER
    )

    return user


@pytest.fixture
def test_customer(db_session, test_user):
    """Create a test customer."""
    customer_service = CustomerService(db_session)

    customer = customer_service.create_customer(
        user_id=test_user.id,
        tier=CustomerTier.BRONZE
    )

    return customer


class TestAuthIntegration:
    """Test authentication integration."""

    def test_user_registration_and_login(self, client, db_session):
        """Test complete user registration and login flow."""
        # Register user
        register_data = {
            "name": "Integration Test User",
            "email": "integration@example.com",
            "phone": "+1234567891",
            "password": "integration123",
            "role": "customer"
        }

        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 200

        user_data = response.json()
        assert user_data["name"] == "Integration Test User"
        assert user_data["email"] == "integration@example.com"
        assert user_data["role"] == "customer"

        # Login user
        login_data = {
            "username": "integration@example.com",
            "password": "integration123"
        }

        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200

        tokens = response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"

        # Test getting current user
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200

        user_info = response.json()
        assert user_info["id"] == user_data["id"]
        assert user_info["name"] == "Integration Test User"


class TestCustomerIntegration:
    """Test customer management integration."""

    def test_customer_creation_and_management(self, client, db_session, test_user):
        """Test complete customer lifecycle."""
        auth_service = AuthService(db_session)
        customer_service = CustomerService(db_session)

        # Create tokens for test user
        tokens = auth_service.authenticate_user(
            email="test@example.com",
            password="test_password123"
        )

        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Get customer (should be auto-created)
        customer = customer_service.get_customer_by_user_id(test_user.id)
        assert customer is not None
        assert customer.tier == CustomerTier.BRONZE
        assert customer.total_points == 0

        # Test customer data retrieval via API
        response = client.get(f"/api/v1/customers/{customer.id}", headers=headers)
        assert response.status_code == 200

        customer_data = response.json()
        assert customer_data["customer"]["tier"] == "bronze"
        assert customer_data["customer"]["total_points"] == 0


class TestLoyaltyIntegration:
    """Test loyalty program integration."""

    def test_loyalty_points_flow(self, client, db_session, test_customer):
        """Test complete loyalty points flow."""
        auth_service = AuthService(db_session)
        loyalty_service = LoyaltyService(db_session)

        # Get user and create tokens
        user = db_session.query(User).filter(User.id == test_customer.user_id).first()
        tokens = auth_service.authenticate_user(
            email=user.email,
            password="test_password123"
        )

        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Award points
        points_data = {
            "customer_id": test_customer.id,
            "points": 100,
            "description": "Test points award",
            "source": "manual"
        }

        response = client.post("/api/v1/loyalty/points/award", json=points_data, headers=headers)
        assert response.status_code == 200

        # Check points were awarded
        customer = db_session.query(Customer).filter(Customer.id == test_customer.id).first()
        assert customer.total_points == 100
        assert customer.lifetime_points == 100

        # Test points summary
        response = client.get(f"/api/v1/loyalty/points/{test_customer.id}", headers=headers)
        assert response.status_code == 200

        points_summary = response.json()
        assert points_summary["total_points"] == 100
        assert points_summary["lifetime_points"] == 100

        # Test tier upgrade
        # Award more points to trigger tier upgrade
        points_data = {
            "customer_id": test_customer.id,
            "points": 900,  # Total will be 1000, should upgrade to silver
            "description": "More test points",
            "source": "manual"
        }

        response = client.post("/api/v1/loyalty/points/award", json=points_data, headers=headers)
        assert response.status_code == 200

        # Check tier was upgraded
        updated_customer = db_session.query(Customer).filter(Customer.id == test_customer.id).first()
        assert updated_customer.tier == CustomerTier.SILVER
        assert updated_customer.total_points == 1000


class TestEndToEndFlow:
    """Test complete end-to-end user flows."""

    def test_complete_customer_journey(self, client, db_session):
        """Test complete customer journey from registration to redemption."""
        # 1. Register user
        register_data = {
            "name": "Journey Test User",
            "email": "journey@example.com",
            "phone": "+1234567892",
            "password": "journey123",
            "role": "customer"
        }

        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 200

        # 2. Login
        login_data = {
            "username": "journey@example.com",
            "password": "journey123"
        }

        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200

        tokens = response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # 3. Get user info
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200

        user_data = response.json()
        assert user_data["name"] == "Journey Test User"

        # 4. Get customer (should be auto-created)
        customer = db_session.query(Customer).filter(Customer.user_id == user_data["id"]).first()
        assert customer is not None

        # 5. Award points
        points_data = {
            "customer_id": customer.id,
            "points": 500,
            "description": "Welcome bonus",
            "source": "promotion"
        }

        response = client.post("/api/v1/loyalty/points/award", json=points_data, headers=headers)
        assert response.status_code == 200

        # 6. Check updated points
        response = client.get(f"/api/v1/loyalty/points/{customer.id}", headers=headers)
        assert response.status_code == 200

        points_summary = response.json()
        assert points_summary["total_points"] == 500

        # 7. Test transaction history
        response = client.get(f"/api/v1/loyalty/transactions/{customer.id}", headers=headers)
        assert response.status_code == 200

        transactions = response.json()
        assert len(transactions) == 1
        assert transactions[0]["points"] == 500


class TestErrorHandling:
    """Test error handling in the system."""

    def test_invalid_authentication(self, client):
        """Test invalid authentication handling."""
        # Test invalid login
        response = client.post("/api/v1/auth/login", data={
            "username": "invalid@example.com",
            "password": "wrong_password"
        })
        assert response.status_code == 401

        # Test accessing protected endpoint without auth
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_invalid_customer_operations(self, client, db_session):
        """Test error handling for invalid customer operations."""
        # Try to get non-existent customer
        response = client.get("/api/v1/customers/99999")
        assert response.status_code == 404

        # Try to award points to non-existent customer
        points_data = {
            "customer_id": 99999,
            "points": 100,
            "description": "Test points",
            "source": "manual"
        }

        response = client.post("/api/v1/loyalty/points/award", json=points_data)
        assert response.status_code == 401  # Should be unauthorized without auth

    def test_insufficient_permissions(self, client, db_session):
        """Test permission-based access control."""
        # Try to access admin endpoints without admin privileges
        # This would require creating a non-admin user and testing admin endpoints
        pass


class TestSystemHealth:
    """Test system health and monitoring endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200

        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert "message" in health_data

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200

        root_data = response.json()
        assert "message" in root_data
        assert "version" in root_data
        assert "docs" in root_data