"""
Unit tests for Loyalty Service.

Tests loyalty points management, tier progression, transaction handling,
and reward redemption functionality.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.loyalty_service import LoyaltyService
from app.models import (
    Customer, User, CustomerTier, LoyaltyTransaction,
    TransactionType, TransactionSource, Reward, RewardRedemption
)


class TestLoyaltyService:
    """Test cases for LoyaltyService."""

    @pytest.fixture
    def loyalty_service(self, db_session):
        """Create loyalty service instance."""
        return LoyaltyService(db_session)

    @pytest.fixture
    def mock_customer(self, db_session):
        """Create mock customer for testing."""
        user = User(
            name="Test User",
            email="test@example.com",
            phone="+1234567890",
            role="customer",
            status="active"
        )
        db_session.add(user)
        db_session.flush()

        customer = Customer(
            user_id=user.id,
            tier=CustomerTier.BRONZE,
            total_points=100,
            lifetime_points=150,
            current_streak=5,
            longest_streak=10,
            status="active",
            joined_date=datetime.utcnow() - timedelta(days=30),
            last_activity=datetime.utcnow() - timedelta(hours=1)
        )
        db_session.add(customer)
        db_session.commit()
        return customer

    def test_award_points_success(self, loyalty_service, mock_customer, db_session):
        """Test successful points awarding."""
        # Award points
        result = loyalty_service.award_points(
            customer_id=mock_customer.id,
            points=50,
            transaction_type=TransactionType.EARNED,
            source=TransactionSource.PURCHASE,
            description="Test purchase"
        )

        # Verify result
        assert result["points_awarded"] == 50
        assert result["new_balance"] == 150
        assert result["transaction_id"] is not None

        # Verify database changes
        customer = db_session.query(Customer).filter(Customer.id == mock_customer.id).first()
        assert customer.total_points == 150
        assert customer.lifetime_points == 200

        # Verify transaction created
        transaction = db_session.query(LoyaltyTransaction).filter(
            LoyaltyTransaction.customer_id == mock_customer.id
        ).order_by(LoyaltyTransaction.created_at.desc()).first()

        assert transaction.points == 50
        assert transaction.transaction_type == TransactionType.EARNED
        assert transaction.source == TransactionSource.PURCHASE
        assert transaction.description == "Test purchase"

    def test_deduct_points_success(self, loyalty_service, mock_customer, db_session):
        """Test successful points deduction."""
        # Deduct points
        result = loyalty_service.deduct_points(
            customer_id=mock_customer.id,
            points=30,
            transaction_type=TransactionType.SPENT,
            source=TransactionSource.REDEMPTION,
            description="Reward redemption"
        )

        # Verify result
        assert result["points_deducted"] == 30
        assert result["new_balance"] == 70
        assert result["transaction_id"] is not None

        # Verify database changes
        customer = db_session.query(Customer).filter(Customer.id == mock_customer.id).first()
        assert customer.total_points == 70
        assert customer.lifetime_points == 150

    def test_deduct_points_insufficient_balance(self, loyalty_service, mock_customer):
        """Test points deduction with insufficient balance."""
        with pytest.raises(ValueError) as exc_info:
            loyalty_service.deduct_points(
                customer_id=mock_customer.id,
                points=200,  # More than available balance
                transaction_type=TransactionType.SPENT,
                source=TransactionSource.REDEMPTION,
                description="Overspending test"
            )

        assert "Insufficient points balance" in str(exc_info.value)

    def test_tier_progression(self, loyalty_service, mock_customer, db_session):
        """Test automatic tier progression."""
        # Set customer to near Gold tier threshold
        mock_customer.total_points = 450  # 50 points below Gold (500)
        db_session.commit()

        # Award enough points to reach Gold tier
        result = loyalty_service.award_points(
            customer_id=mock_customer.id,
            points=60,  # 450 + 60 = 510 (exceeds Gold threshold)
            transaction_type=TransactionType.EARNED,
            source=TransactionSource.PURCHASE,
            description="Tier upgrade test"
        )

        # Verify tier upgrade
        customer = db_session.query(Customer).filter(Customer.id == mock_customer.id).first()
        assert customer.tier == CustomerTier.GOLD
        assert customer.total_points == 510

        # Verify tier history created
        tier_history = db_session.query(CustomerTierHistory).filter(
            CustomerTierHistory.customer_id == mock_customer.id
        ).order_by(CustomerTierHistory.created_at.desc()).first()

        assert tier_history.previous_tier == CustomerTier.BRONZE
        assert tier_history.new_tier == CustomerTier.GOLD
        assert tier_history.points_at_upgrade == 510

    def test_adjust_points(self, loyalty_service, mock_customer, db_session):
        """Test manual points adjustment."""
        # Adjust points
        result = loyalty_service.adjust_points(
            customer_id=mock_customer.id,
            points_adjustment=25,
            reason="Manual adjustment",
            description="Admin correction"
        )

        assert result["points_adjusted"] == 25
        assert result["new_balance"] == 125

        # Verify database changes
        customer = db_session.query(Customer).filter(Customer.id == mock_customer.id).first()
        assert customer.total_points == 125

    def test_get_customer_points_summary(self, loyalty_service, mock_customer):
        """Test customer points summary retrieval."""
        summary = loyalty_service.get_customer_points_summary(mock_customer.id)

        assert summary["customer_id"] == mock_customer.id
        assert summary["current_points"] == 100
        assert summary["lifetime_points"] == 150
        assert summary["tier"] == CustomerTier.BRONZE.value
        assert "recent_transactions" in summary
        assert "tier_progress" in summary

    def test_get_transaction_history(self, loyalty_service, mock_customer, db_session):
        """Test transaction history retrieval."""
        # Create some test transactions
        transactions = [
            LoyaltyTransaction(
                customer_id=mock_customer.id,
                points=50,
                transaction_type=TransactionType.EARNED,
                source=TransactionSource.PURCHASE,
                description="Purchase 1"
            ),
            LoyaltyTransaction(
                customer_id=mock_customer.id,
                points=-20,
                transaction_type=TransactionType.SPENT,
                source=TransactionSource.REDEMPTION,
                description="Redemption 1"
            )
        ]

        for transaction in transactions:
            db_session.add(transaction)
        db_session.commit()

        # Get transaction history
        history = loyalty_service.get_transaction_history(
            customer_id=mock_customer.id,
            limit=10,
            offset=0
        )

        assert len(history["transactions"]) == 2
        assert history["pagination"]["total"] == 2
        assert history["pagination"]["limit"] == 10
        assert history["pagination"]["offset"] == 0

    def test_validate_reward_redemption_success(self, loyalty_service, mock_customer, db_session):
        """Test successful reward redemption validation."""
        # Create a test reward
        reward = Reward(
            name="Test Reward",
            description="Test reward for validation",
            points_required=50,
            category="Test",
            is_active=True,
            stock_quantity=100
        )
        db_session.add(reward)
        db_session.commit()

        # Validate redemption
        validation = loyalty_service.validate_reward_redemption(
            customer_id=mock_customer.id,
            reward_id=reward.id,
            quantity=1
        )

        assert validation["can_redeem"] == True
        assert validation["points_required"] == 50
        assert validation["customer_balance"] == 100
        assert len(validation["issues"]) == 0

    def test_validate_reward_redemption_insufficient_points(self, loyalty_service, mock_customer, db_session):
        """Test reward redemption with insufficient points."""
        # Create a test reward that requires more points than customer has
        reward = Reward(
            name="Expensive Reward",
            description="Test reward requiring many points",
            points_required=200,  # More than customer's 100 points
            category="Test",
            is_active=True,
            stock_quantity=100
        )
        db_session.add(reward)
        db_session.commit()

        # Validate redemption
        validation = loyalty_service.validate_reward_redemption(
            customer_id=mock_customer.id,
            reward_id=reward.id,
            quantity=1
        )

        assert validation["can_redeem"] == False
        assert validation["points_required"] == 200
        assert validation["customer_balance"] == 100
        assert len(validation["issues"]) > 0
        assert "Insufficient points balance" in validation["issues"][0]

    def test_redeem_reward_success(self, loyalty_service, mock_customer, db_session):
        """Test successful reward redemption."""
        # Create a test reward
        reward = Reward(
            name="Test Reward",
            description="Test reward for redemption",
            points_required=50,
            category="Test",
            is_active=True,
            stock_quantity=100
        )
        db_session.add(reward)
        db_session.commit()

        # Redeem reward
        result = loyalty_service.redeem_reward(
            customer_id=mock_customer.id,
            reward_id=reward.id,
            quantity=1,
            redemption_source="test"
        )

        assert result["redemption_id"] is not None
        assert result["points_deducted"] == 50
        assert result["new_balance"] == 50

        # Verify database changes
        customer = db_session.query(Customer).filter(Customer.id == mock_customer.id).first()
        assert customer.total_points == 50

        # Verify redemption record
        redemption = db_session.query(RewardRedemption).filter(
            RewardRedemption.customer_id == mock_customer.id
        ).first()

        assert redemption.reward_id == reward.id
        assert redemption.quantity == 1
        assert redemption.status.value == "completed"

    def test_get_tier_benefits(self, loyalty_service):
        """Test tier benefits retrieval."""
        benefits = loyalty_service.get_tier_benefits(CustomerTier.GOLD)

        assert isinstance(benefits, list)
        assert len(benefits) > 0

        # Verify benefit structure
        for benefit in benefits:
            assert "name" in benefit
            assert "description" in benefit
            assert "category" in benefit
            assert "value" in benefit

    def test_calculate_tier_progress(self, loyalty_service, mock_customer):
        """Test tier progress calculation."""
        progress = loyalty_service.calculate_tier_progress(mock_customer.id)

        assert "current_tier" in progress
        assert "next_tier" in progress
        assert "points_to_next" in progress
        assert "progress_percentage" in progress
        assert 0 <= progress["progress_percentage"] <= 100

    @patch('app.services.loyalty_service.datetime')
    def test_process_daily_tier_evaluations(self, mock_datetime, loyalty_service, mock_customer, db_session):
        """Test daily tier evaluations processing."""
        # Set up mock datetime
        mock_datetime.utcnow.return_value = datetime.utcnow()
        mock_datetime.now.return_value = datetime.now()

        # Process daily evaluations
        results = loyalty_service.process_daily_tier_evaluations()

        assert "processed" in results
        assert "upgraded" in results
        assert "downgraded" in results
        assert "errors" in results
        assert isinstance(results["processed"], int)
        assert isinstance(results["upgraded"], int)
        assert isinstance(results["downgraded"], int)

    def test_get_loyalty_analytics(self, loyalty_service, mock_customer, db_session):
        """Test loyalty analytics retrieval."""
        # Create some test transactions
        transactions = [
            LoyaltyTransaction(
                customer_id=mock_customer.id,
                points=50,
                transaction_type=TransactionType.EARNED,
                source=TransactionSource.PURCHASE,
                description="Purchase 1"
            ),
            LoyaltyTransaction(
                customer_id=mock_customer.id,
                points=-20,
                transaction_type=TransactionType.SPENT,
                source=TransactionSource.REDEMPTION,
                description="Redemption 1"
            )
        ]

        for transaction in transactions:
            db_session.add(transaction)
        db_session.commit()

        # Get analytics
        analytics = loyalty_service.get_loyalty_analytics(
            date_from=datetime.utcnow() - timedelta(days=30),
            date_to=datetime.utcnow()
        )

        assert "total_points_earned" in analytics
        assert "total_points_spent" in analytics
        assert "net_points" in analytics
        assert "transactions_by_type" in analytics
        assert "transactions_by_source" in analytics
        assert "redemption_rate" in analytics
        assert isinstance(analytics["total_points_earned"], (int, float))
        assert isinstance(analytics["total_points_spent"], (int, float))