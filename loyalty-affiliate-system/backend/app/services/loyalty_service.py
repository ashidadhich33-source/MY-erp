"""
Loyalty System Business Logic Service.

Handles points management, tier calculations, and reward operations.
"""

from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import logging

from ..models import (
    Customer, CustomerTier, CustomerTierHistory, CustomerStatus,
    LoyaltyTransaction, TransactionType, TransactionSource,
    Reward, RewardStatus, RewardRedemption,
    TierBenefit, User
)
from ..core.database import SessionLocal

logger = logging.getLogger(__name__)


class LoyaltyService:
    """Service class for loyalty system operations."""

    def __init__(self, db: Session):
        self.db = db

    def award_points(
        self,
        customer_id: int,
        points: int,
        source: TransactionSource,
        description: str,
        reference_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        expires_at: Optional[datetime] = None,
        awarded_by: Optional[int] = None
    ) -> LoyaltyTransaction:
        """
        Award points to a customer.

        Args:
            customer_id: Customer ID
            points: Number of points to award (positive)
            source: Source of points (purchase, referral, etc.)
            description: Description of the transaction
            reference_id: Optional reference ID (order ID, etc.)
            metadata: Optional metadata dictionary
            expires_at: Optional expiry date for points
            awarded_by: User ID who awarded the points

        Returns:
            Created loyalty transaction
        """
        if points <= 0:
            raise ValueError("Points must be positive")

        # Get customer
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found")

        if customer.status != CustomerStatus.ACTIVE:
            raise ValueError(f"Customer {customer_id} is not active")

        # Create transaction
        transaction = LoyaltyTransaction(
            user_id=customer.user_id,
            customer_id=customer_id,
            points=points,
            transaction_type=TransactionType.EARNED,
            source=source,
            description=description,
            reference_id=reference_id,
            metadata=metadata,
            expires_at=expires_at,
            is_active=True
        )

        self.db.add(transaction)

        # Update customer points
        customer.total_points += points
        customer.lifetime_points += points
        customer.last_activity = datetime.utcnow()

        # Check for tier upgrade
        self._check_tier_upgrade(customer)

        # Update tier benefits if tier changed
        if customer.tier != customer.tier:  # This comparison will work after _check_tier_upgrade
            self._update_customer_tier(customer, awarded_by)

        self.db.commit()
        self.db.refresh(transaction)

        logger.info(f"Awarded {points} points to customer {customer_id}")
        return transaction

    def deduct_points(
        self,
        customer_id: int,
        points: int,
        source: TransactionSource,
        description: str,
        reference_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        deducted_by: Optional[int] = None
    ) -> LoyaltyTransaction:
        """
        Deduct points from a customer (for redemptions, adjustments).

        Args:
            customer_id: Customer ID
            points: Number of points to deduct (positive)
            source: Source of deduction
            description: Description of the transaction
            reference_id: Optional reference ID
            metadata: Optional metadata dictionary
            deducted_by: User ID who deducted the points

        Returns:
            Created loyalty transaction
        """
        if points <= 0:
            raise ValueError("Points must be positive")

        # Get customer
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found")

        if customer.total_points < points:
            raise ValueError(f"Insufficient points. Customer has {customer.total_points}, trying to deduct {points}")

        # Create transaction (negative points)
        transaction = LoyaltyTransaction(
            user_id=customer.user_id,
            customer_id=customer_id,
            points=-points,
            transaction_type=TransactionType.REDEEMED,
            source=source,
            description=description,
            reference_id=reference_id,
            metadata=metadata,
            is_active=True
        )

        self.db.add(transaction)

        # Update customer points
        customer.total_points -= points
        customer.last_activity = datetime.utcnow()

        self.db.commit()
        self.db.refresh(transaction)

        logger.info(f"Deducted {points} points from customer {customer_id}")
        return transaction

    def adjust_points(
        self,
        customer_id: int,
        points: int,
        description: str,
        reference_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        adjusted_by: Optional[int] = None
    ) -> LoyaltyTransaction:
        """
        Adjust customer points (can be positive or negative).

        Args:
            customer_id: Customer ID
            points: Points adjustment (can be negative)
            description: Description of the adjustment
            reference_id: Optional reference ID
            metadata: Optional metadata dictionary
            adjusted_by: User ID who made the adjustment

        Returns:
            Created loyalty transaction
        """
        # Get customer
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found")

        # Create transaction
        transaction = LoyaltyTransaction(
            user_id=customer.user_id,
            customer_id=customer_id,
            points=points,
            transaction_type=TransactionType.ADJUSTMENT,
            source=TransactionSource.MANUAL,
            description=description,
            reference_id=reference_id,
            metadata=metadata,
            is_active=True
        )

        self.db.add(transaction)

        # Update customer points
        customer.total_points += points
        customer.last_activity = datetime.utcnow()

        # Check for tier upgrade/downgrade
        self._check_tier_upgrade(customer)

        self.db.commit()
        self.db.refresh(transaction)

        logger.info(f"Adjusted {points} points for customer {customer_id}")
        return transaction

    def _check_tier_upgrade(self, customer: Customer) -> bool:
        """
        Check if customer should be upgraded based on points.

        Returns:
            True if tier changed, False otherwise
        """
        tier_thresholds = {
            CustomerTier.BRONZE: 0,
            CustomerTier.SILVER: 200,
            CustomerTier.GOLD: 500,
            CustomerTier.PLATINUM: 1000
        }

        current_threshold = tier_thresholds[customer.tier]
        next_tier = None

        # Find next tier based on points
        for tier, threshold in tier_thresholds.items():
            if customer.total_points >= threshold and threshold > current_threshold:
                if next_tier is None or threshold < tier_thresholds[next_tier]:
                    next_tier = tier

        if next_tier and next_tier != customer.tier:
            customer.tier = next_tier
            return True

        return False

    def _update_customer_tier(self, customer: Customer, changed_by: Optional[int] = None):
        """
        Update customer tier and create history record.
        """
        # Create tier history record
        history = CustomerTierHistory(
            customer_id=customer.id,
            previous_tier=customer.tier,  # This will be the old tier
            new_tier=customer.tier,
            points_at_upgrade=customer.total_points,
            reason="points_threshold",
            changed_by=changed_by
        )
        self.db.add(history)

    def get_customer_balance(self, customer_id: int) -> Dict:
        """
        Get customer points balance and tier information.

        Returns:
            Dictionary with balance, tier, and tier progress info
        """
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found")

        tier_thresholds = {
            CustomerTier.BRONZE: 0,
            CustomerTier.SILVER: 200,
            CustomerTier.GOLD: 500,
            CustomerTier.PLATINUM: 1000
        }

        current_threshold = tier_thresholds[customer.tier]
        next_tier = None
        next_threshold = None

        # Find next tier
        for tier, threshold in tier_thresholds.items():
            if threshold > current_threshold:
                next_tier = tier
                next_threshold = threshold
                break

        progress_to_next = 0
        if next_threshold:
            progress = customer.total_points - current_threshold
            progress_to_next = min(progress / (next_threshold - current_threshold), 1.0)

        return {
            "customer_id": customer.id,
            "total_points": customer.total_points,
            "lifetime_points": customer.lifetime_points,
            "current_tier": customer.tier.value,
            "next_tier": next_tier.value if next_tier else None,
            "progress_to_next": progress_to_next,
            "points_to_next": next_threshold - customer.total_points if next_threshold else 0,
            "tier_benefits": self.get_tier_benefits(customer.tier)
        }

    def get_tier_benefits(self, tier: CustomerTier) -> List[Dict]:
        """
        Get benefits for a specific tier.

        Returns:
            List of benefit dictionaries
        """
        benefits = self.db.query(TierBenefit).filter(
            and_(
                TierBenefit.tier == tier,
                TierBenefit.is_active == True
            )
        ).all()

        return [
            {
                "type": benefit.benefit_type,
                "value": benefit.benefit_value,
                "description": benefit.description
            }
            for benefit in benefits
        ]

    def get_transaction_history(
        self,
        customer_id: int,
        limit: int = 50,
        offset: int = 0,
        transaction_type: Optional[TransactionType] = None,
        source: Optional[TransactionSource] = None
    ) -> Dict:
        """
        Get customer transaction history with pagination.

        Returns:
            Dictionary with transactions and pagination info
        """
        query = self.db.query(LoyaltyTransaction).filter(
            LoyaltyTransaction.customer_id == customer_id
        )

        if transaction_type:
            query = query.filter(LoyaltyTransaction.transaction_type == transaction_type)

        if source:
            query = query.filter(LoyaltyTransaction.source == source)

        total = query.count()
        transactions = query.order_by(desc(LoyaltyTransaction.created_at)).offset(offset).limit(limit).all()

        return {
            "transactions": [
                {
                    "id": t.id,
                    "points": t.points,
                    "type": t.transaction_type.value,
                    "source": t.source.value,
                    "description": t.description,
                    "reference_id": t.reference_id,
                    "created_at": t.created_at.isoformat(),
                    "expires_at": t.expires_at.isoformat() if t.expires_at else None
                }
                for t in transactions
            ],
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        }

    def expire_points(self) -> int:
        """
        Process expired points and create expiry transactions.

        Returns:
            Number of points expired
        """
        expired_transactions = self.db.query(LoyaltyTransaction).filter(
            and_(
                LoyaltyTransaction.expires_at <= datetime.utcnow(),
                LoyaltyTransaction.expires_at.isnot(None),
                LoyaltyTransaction.is_active == True
            )
        ).all()

        expired_count = 0
        for transaction in expired_transactions:
            if transaction.points > 0:  # Only process earned points
                # Create expiry transaction
                expiry_transaction = LoyaltyTransaction(
                    user_id=transaction.user_id,
                    customer_id=transaction.customer_id,
                    points=-transaction.points,
                    transaction_type=TransactionType.EXPIRED,
                    source=TransactionSource.SYSTEM,
                    description=f"Points expired from transaction {transaction.id}",
                    reference_id=f"EXP-{transaction.id}",
                    is_active=True
                )
                self.db.add(expiry_transaction)

                # Update customer points
                customer = self.db.query(Customer).filter(Customer.id == transaction.customer_id).first()
                if customer:
                    customer.total_points -= transaction.points
                    customer.last_activity = datetime.utcnow()

                transaction.is_active = False
                expired_count += transaction.points

        if expired_count > 0:
            self.db.commit()

        logger.info(f"Expired {expired_count} points")
        return expired_count