"""
Test configuration and fixtures for pytest.

This file contains common fixtures, test database setup,
and shared test utilities for the loyalty system.
"""

import pytest
import os
import tempfile
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from unittest.mock import Mock, MagicMock

# Import all models for test database setup
from app.models import (
    Base, User, UserRole, UserStatus,
    Customer, CustomerTier, CustomerStatus, CustomerTierHistory,
    LoyaltyTransaction, TransactionType, TransactionSource,
    Reward, RewardRedemption, RedemptionStatus,
    Affiliate, CustomerReferral, AffiliateCommission, PayoutRequest,
    WhatsAppMessage, MessageType, MessageDirection, MessageStatus,
    NotificationTemplate, TemplateCategory,
    BirthdayPromotion, WhatsAppWebhook
)

# Test database configuration
TEST_DATABASE_URL = "sqlite:///:memory:"  # In-memory SQLite for testing

# Create test database engine
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False  # Set to True for SQL query logging during tests
)

# Create SessionLocal for tests
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    return engine


@pytest.fixture(scope="session", autouse=True)
def setup_test_database(test_engine):
    """Set up test database with all tables."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    yield
    # Clean up after tests
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(test_engine):
    """Create database session for tests."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    # Rollback transaction and close session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def mock_erp_connector():
    """Create mock ERP connector for testing."""
    mock_connector = Mock()
    mock_connector.connect.return_value = True
    mock_connector.test_connection.return_value = True
    mock_connector.get_customers.return_value = []
    mock_connector.get_products.return_value = []
    mock_connector.get_sales.return_value = []
    return mock_connector


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing."""
    return {
        "erp_id": "CUST_001",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "address": "123 Main St, City, State 12345",
        "customer_type": "Regular",
        "credit_limit": 1000.00,
        "tax_id": "123-45-6789",
        "sync_timestamp": datetime.utcnow()
    }


@pytest.fixture
def sample_sale_data():
    """Sample sale data for testing."""
    return {
        "erp_sale_id": "SALE_001",
        "customer_erp_id": "CUST_001",
        "sale_amount": 150.00,
        "points_earned": 15,
        "transaction_date": datetime.utcnow() - timedelta(days=1),
        "sync_timestamp": datetime.utcnow()
    }


@pytest.fixture
def sample_whatsapp_message():
    """Sample WhatsApp message data for testing."""
    return {
        "message_type": MessageType.TEXT,
        "direction": MessageDirection.OUTBOUND,
        "content": "Welcome to our loyalty program!",
        "recipient_phone": "+1234567890",
        "status": MessageStatus.SENT,
        "is_automated": True
    }


@pytest.fixture
def test_user_data():
    """Test user data for authentication testing."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+1234567890",
        "role": UserRole.CUSTOMER,
        "status": UserStatus.ACTIVE
    }


@pytest.fixture
def test_reward_data():
    """Test reward data for loyalty testing."""
    return {
        "name": "Free Coffee",
        "description": "Enjoy a free coffee on us!",
        "points_required": 100,
        "category": "Food & Beverage",
        "is_active": True,
        "stock_quantity": 50
    }


@pytest.fixture
def test_affiliate_data():
    """Test affiliate data for affiliate testing."""
    return {
        "name": "Test Affiliate",
        "email": "affiliate@example.com",
        "phone": "+1234567891",
        "company": "Test Company",
        "website": "https://testcompany.com",
        "status": "active",
        "commission_rate": 10.0
    }


# Mock fixtures for external services
@pytest.fixture
def mock_whatsapp_api():
    """Mock WhatsApp API for testing."""
    mock_api = Mock()
    mock_api.send_message.return_value = {
        "message_id": "msg_123",
        "status": "sent",
        "recipient": "+1234567890"
    }
    mock_api.send_template_message.return_value = {
        "message_id": "msg_456",
        "status": "sent",
        "recipient": "+1234567890"
    }
    return mock_api


@pytest.fixture
def mock_email_service():
    """Mock email service for testing."""
    mock_email = Mock()
    mock_email.send.return_value = True
    mock_email.send_template.return_value = True
    return mock_email


@pytest.fixture
def mock_sms_service():
    """Mock SMS service for testing."""
    mock_sms = Mock()
    mock_sms.send.return_value = True
    mock_sms.send_template.return_value = True
    return mock_sms


# Test utilities
class TestUtils:
    """Utility class for common test operations."""

    @staticmethod
    def create_test_user(db_session, **overrides):
        """Create a test user with optional overrides."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "role": UserRole.CUSTOMER,
            "status": UserStatus.ACTIVE,
            "email_verified": True,
            "phone_verified": True
        }
        user_data.update(overrides)

        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        return user

    @staticmethod
    def create_test_customer(db_session, user=None, **overrides):
        """Create a test customer with optional user and overrides."""
        if not user:
            user = TestUtils.create_test_user(db_session)

        customer_data = {
            "user_id": user.id,
            "tier": CustomerTier.BRONZE,
            "total_points": 100,
            "lifetime_points": 150,
            "current_streak": 5,
            "longest_streak": 10,
            "status": CustomerStatus.ACTIVE,
            "joined_date": datetime.utcnow() - timedelta(days=30),
            "last_activity": datetime.utcnow() - timedelta(hours=1)
        }
        customer_data.update(overrides)

        customer = Customer(**customer_data)
        db_session.add(customer)
        db_session.commit()
        return customer

    @staticmethod
    def create_test_transaction(db_session, customer, **overrides):
        """Create a test loyalty transaction."""
        transaction_data = {
            "customer_id": customer.id,
            "points": 50,
            "transaction_type": TransactionType.EARNED,
            "source": TransactionSource.PURCHASE,
            "description": "Test transaction"
        }
        transaction_data.update(overrides)

        transaction = LoyaltyTransaction(**transaction_data)
        db_session.add(transaction)
        db_session.commit()
        return transaction

    @staticmethod
    def create_test_reward(db_session, **overrides):
        """Create a test reward."""
        reward_data = {
            "name": "Test Reward",
            "description": "Test reward description",
            "points_required": 100,
            "category": "Test",
            "is_active": True,
            "stock_quantity": 50
        }
        reward_data.update(overrides)

        reward = Reward(**reward_data)
        db_session.add(reward)
        db_session.commit()
        return reward


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "auth: marks tests related to authentication"
    )
    config.addinivalue_line(
        "markers", "loyalty: marks tests related to loyalty system"
    )
    config.addinivalue_line(
        "markers", "whatsapp: marks tests related to WhatsApp integration"
    )


# Environment variables for testing
os.environ.setdefault('TESTING', 'True')
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-testing-only')
os.environ.setdefault('ALGORITHM', 'HS256')
os.environ.setdefault('ACCESS_TOKEN_EXPIRE_MINUTES', '30')
os.environ.setdefault('REFRESH_TOKEN_EXPIRE_DAYS', '7')

# Test data generators
class TestDataGenerator:
    """Generate test data for various scenarios."""

    @staticmethod
    def generate_customers(n=10):
        """Generate test customer data."""
        customers = []
        for i in range(n):
            customers.append({
                "name": f"Test Customer {i+1}",
                "email": f"customer{i+1}@example.com",
                "phone": f"+12345678{i"02d"}",
                "role": UserRole.CUSTOMER,
                "status": UserStatus.ACTIVE
            })
        return customers

    @staticmethod
    def generate_transactions(customer_id, n=5):
        """Generate test transaction data."""
        transactions = []
        for i in range(n):
            transactions.append({
                "customer_id": customer_id,
                "points": (i + 1) * 10,
                "transaction_type": TransactionType.EARNED,
                "source": TransactionSource.PURCHASE,
                "description": f"Test transaction {i+1}"
            })
        return transactions

    @staticmethod
    def generate_erp_sync_data():
        """Generate test ERP synchronization data."""
        return {
            "customers": [
                {
                    "id": "CUST_001",
                    "customer_name": "ERP Customer 1",
                    "email_address": "erp1@company.com",
                    "phone_number": "+1987654321",
                    "address": "456 ERP St, City, State 54321",
                    "customer_type": "Premium",
                    "credit_limit": 5000.00,
                    "tax_id": "987-65-4321"
                }
            ],
            "sales": [
                {
                    "id": "SALE_001",
                    "customer_id": "CUST_001",
                    "total_amount": 299.99,
                    "sale_date": datetime.utcnow() - timedelta(days=1)
                }
            ]
        }