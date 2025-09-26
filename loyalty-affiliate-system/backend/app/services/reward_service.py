"""
Reward System Business Logic Service.

Handles reward catalog management, redemptions, and availability checking.
"""

from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import logging
import random
import string

from ..models import (
    Customer, CustomerTier,
    Reward, RewardStatus, RewardRedemption,
    LoyaltyTransaction, TransactionType, TransactionSource,
    TierBenefit, User
)
from ..core.database import SessionLocal
from .loyalty_service import LoyaltyService

logger = logging.getLogger(__name__)


class RewardService:
    """Service class for reward system operations."""

    def __init__(self, db: Session):
        self.db = db
        self.loyalty_service = LoyaltyService(db)

    def get_available_rewards(self, customer_id: int) -> List[Dict]:
        """
        Get rewards available for a customer based on their points and tier.

        Args:
            customer_id: Customer ID

        Returns:
            List of available rewards with redemption info
        """
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found")

        # Get all active rewards
        rewards = self.db.query(Reward).filter(
            and_(
                Reward.status == RewardStatus.ACTIVE,
                Reward.points_required <= customer.total_points,
                or_(
                    Reward.stock_quantity == -1,  # Unlimited stock
                    Reward.stock_quantity > 0     # Limited stock available
                ),
                or_(
                    Reward.valid_until.is_(None),  # No expiry
                    Reward.valid_until >= datetime.utcnow()  # Not expired
                )
            )
        ).all()

        available_rewards = []
        for reward in rewards:
            # Check if customer hasn't exceeded max redemptions
            redemption_count = self.db.query(func.count(RewardRedemption.id)).filter(
                and_(
                    RewardRedemption.reward_id == reward.id,
                    RewardRedemption.customer_id == customer_id,
                    RewardRedemption.status.in_(["completed", "pending"])
                )
            ).scalar()

            if redemption_count < reward.max_per_customer:
                available_rewards.append({
                    "id": reward.id,
                    "name": reward.name,
                    "description": reward.description,
                    "points_required": reward.points_required,
                    "category": reward.category,
                    "image_url": reward.image_url,
                    "is_featured": reward.is_featured,
                    "stock_remaining": reward.stock_quantity if reward.stock_quantity != -1 else "unlimited",
                    "customer_redemptions": redemption_count,
                    "max_per_customer": reward.max_per_customer
                })

        return available_rewards

    def redeem_reward(
        self,
        customer_id: int,
        reward_id: int,
        quantity: int = 1,
        redeemed_by: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Redeem a reward for a customer.

        Args:
            customer_id: Customer ID
            reward_id: Reward ID to redeem
            quantity: Quantity to redeem
            redeemed_by: User ID who processed the redemption
            notes: Optional notes

        Returns:
            Dictionary with redemption result
        """
        # Get customer and reward
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        reward = self.db.query(Reward).filter(Reward.id == reward_id).first()

        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found")

        if not reward:
            raise ValueError(f"Reward with ID {reward_id} not found")

        if reward.status != RewardStatus.ACTIVE:
            raise ValueError("Reward is not available")

        if customer.total_points < (reward.points_required * quantity):
            raise ValueError(f"Insufficient points. Required: {reward.points_required * quantity}, Available: {customer.total_points}")

        # Check stock availability
        if reward.stock_quantity != -1:  # Limited stock
            available_stock = reward.stock_quantity
            current_redemptions = self.db.query(func.sum(RewardRedemption.quantity)).filter(
                and_(
                    RewardRedemption.reward_id == reward_id,
                    RewardRedemption.status.in_(["completed", "pending"])
                )
            ).scalar() or 0

            if (current_redemptions + quantity) > available_stock:
                raise ValueError("Insufficient stock available")

        # Check max per customer
        current_customer_redemptions = self.db.query(func.sum(RewardRedemption.quantity)).filter(
            and_(
                RewardRedemption.reward_id == reward_id,
                RewardRedemption.customer_id == customer_id,
                RewardRedemption.status.in_(["completed", "pending"])
            )
        ).scalar() or 0

        if (current_customer_redemptions + quantity) > reward.max_per_customer:
            raise ValueError(f"Maximum redemptions per customer exceeded. Max: {reward.max_per_customer}")

        # Generate redemption code
        redemption_code = self._generate_redemption_code()

        # Deduct points
        total_points = reward.points_required * quantity
        transaction = self.loyalty_service.deduct_points(
            customer_id=customer_id,
            points=total_points,
            source=TransactionSource.MANUAL,
            description=f"Redeemed {quantity}x {reward.name}",
            reference_id=f"REWARD-{reward.id}",
            metadata={"reward_id": reward_id, "quantity": quantity}
        )

        # Create redemption record
        redemption = RewardRedemption(
            transaction_id=transaction.id,
            reward_id=reward_id,
            customer_id=customer_id,
            quantity=quantity,
            redemption_code=redemption_code,
            status="pending",
            notes=notes
        )

        self.db.add(redemption)

        # Update stock if limited
        if reward.stock_quantity != -1:
            # This would typically be done in a transaction to prevent race conditions
            reward.stock_quantity -= quantity

        self.db.commit()

        logger.info(f"Reward {reward_id} redeemed by customer {customer_id}")
        return {
            "success": True,
            "redemption_id": redemption.id,
            "redemption_code": redemption_code,
            "points_deducted": total_points,
            "transaction_id": transaction.id,
            "reward": {
                "id": reward.id,
                "name": reward.name,
                "description": reward.description,
                "category": reward.category
            }
        }

    def _generate_redemption_code(self, length: int = 8) -> str:
        """
        Generate a unique redemption code.

        Args:
            length: Length of the code

        Returns:
            Unique redemption code
        """
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

            # Check if code already exists
            existing = self.db.query(RewardRedemption).filter(
                RewardRedemption.redemption_code == code
            ).first()

            if not existing:
                return code

    def fulfill_redemption(
        self,
        redemption_id: int,
        fulfilled_by: int,
        notes: Optional[str] = None
    ) -> bool:
        """
        Mark a redemption as fulfilled.

        Args:
            redemption_id: Redemption ID to fulfill
            fulfilled_by: User ID who fulfilled it
            notes: Optional fulfillment notes

        Returns:
            True if successful
        """
        redemption = self.db.query(RewardRedemption).filter(
            RewardRedemption.id == redemption_id
        ).first()

        if not redemption:
            raise ValueError(f"Redemption with ID {redemption_id} not found")

        if redemption.status == "completed":
            raise ValueError("Redemption is already completed")

        redemption.status = "completed"
        redemption.fulfilled_at = datetime.utcnow()
        redemption.fulfilled_by = fulfilled_by
        redemption.notes = notes

        self.db.commit()

        logger.info(f"Redemption {redemption_id} fulfilled by user {fulfilled_by}")
        return True

    def cancel_redemption(
        self,
        redemption_id: int,
        cancelled_by: int,
        reason: str
    ) -> Dict:
        """
        Cancel a redemption and refund points.

        Args:
            redemption_id: Redemption ID to cancel
            cancelled_by: User ID who cancelled it
            reason: Reason for cancellation

        Returns:
            Dictionary with cancellation result
        """
        redemption = self.db.query(RewardRedemption).filter(
            RewardRedemption.id == redemption_id
        ).first()

        if not redemption:
            raise ValueError(f"Redemption with ID {redemption_id} not found")

        if redemption.status not in ["pending", "completed"]:
            raise ValueError("Redemption cannot be cancelled")

        # Get transaction to refund points
        transaction = self.db.query(LoyaltyTransaction).filter(
            LoyaltyTransaction.id == redemption.transaction_id
        ).first()

        if not transaction:
            raise ValueError("Associated transaction not found")

        # Refund points (reverse the transaction)
        refund_transaction = self.loyalty_service.award_points(
            customer_id=redemption.customer_id,
            points=abs(transaction.points),  # Points were deducted, so refund the positive amount
            source=TransactionSource.MANUAL,
            description=f"Refund for cancelled redemption: {redemption.reward.name}",
            reference_id=f"REFUND-{redemption.id}",
            metadata={"original_redemption_id": redemption_id, "reason": reason}
        )

        # Update redemption status
        redemption.status = "cancelled"
        redemption.notes = f"Cancelled: {reason}"

        # Restore stock if limited
        reward = self.db.query(Reward).filter(Reward.id == redemption.reward_id).first()
        if reward and reward.stock_quantity != -1:
            reward.stock_quantity += redemption.quantity

        self.db.commit()

        logger.info(f"Redemption {redemption_id} cancelled by user {cancelled_by}")
        return {
            "success": True,
            "redemption_id": redemption_id,
            "refunded_points": abs(transaction.points),
            "refund_transaction_id": refund_transaction.id,
            "reason": reason
        }

    def get_redemption_history(self, customer_id: int, limit: int = 50, offset: int = 0) -> Dict:
        """
        Get customer's redemption history.

        Returns:
            Dictionary with redemptions and pagination info
        """
        total = self.db.query(func.count(RewardRedemption.id)).filter(
            RewardRedemption.customer_id == customer_id
        ).scalar()

        redemptions = self.db.query(RewardRedemption).filter(
            RewardRedemption.customer_id == customer_id
        ).order_by(desc(RewardRedemption.created_at)).offset(offset).limit(limit).all()

        return {
            "redemptions": [
                {
                    "id": r.id,
                    "redemption_code": r.redemption_code,
                    "reward": {
                        "id": r.reward.id,
                        "name": r.reward.name,
                        "description": r.reward.description,
                        "category": r.reward.category,
                        "points_required": r.reward.points_required
                    },
                    "quantity": r.quantity,
                    "status": r.status,
                    "created_at": r.created_at.isoformat(),
                    "fulfilled_at": r.fulfilled_at.isoformat() if r.fulfilled_at else None,
                    "fulfilled_by": r.fulfilled_by,
                    "notes": r.notes
                }
                for r in redemptions
            ],
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        }

    def get_reward_statistics(self, reward_id: int) -> Dict:
        """
        Get statistics for a specific reward.

        Returns:
            Dictionary with reward statistics
        """
        reward = self.db.query(Reward).filter(Reward.id == reward_id).first()
        if not reward:
            raise ValueError(f"Reward with ID {reward_id} not found")

        total_redemptions = self.db.query(func.sum(RewardRedemption.quantity)).filter(
            and_(
                RewardRedemption.reward_id == reward_id,
                RewardRedemption.status.in_(["completed", "pending"])
            )
        ).scalar() or 0

        completed_redemptions = self.db.query(func.sum(RewardRedemption.quantity)).filter(
            and_(
                RewardRedemption.reward_id == reward_id,
                RewardRedemption.status == "completed"
            )
        ).scalar() or 0

        return {
            "reward_id": reward.id,
            "reward_name": reward.name,
            "total_redemptions": total_redemptions,
            "completed_redemptions": completed_redemptions,
            "stock_remaining": reward.stock_quantity if reward.stock_quantity != -1 else "unlimited",
            "is_available": reward.status == RewardStatus.ACTIVE and (
                reward.stock_quantity == -1 or reward.stock_quantity > 0
            ),
            "total_points_redeemed": total_redemptions * reward.points_required
        }

    def create_reward(
        self,
        name: str,
        description: str,
        points_required: int,
        category: str,
        stock_quantity: int = -1,
        max_per_customer: int = 1,
        image_url: Optional[str] = None,
        terms_conditions: Optional[str] = None,
        is_featured: bool = False,
        valid_from: Optional[datetime] = None,
        valid_until: Optional[datetime] = None,
        created_by: int
    ) -> Reward:
        """
        Create a new reward.

        Args:
            name: Reward name
            description: Reward description
            points_required: Points required for redemption
            category: Reward category
            stock_quantity: Stock quantity (-1 for unlimited)
            max_per_customer: Maximum redemptions per customer
            image_url: Optional image URL
            terms_conditions: Optional terms and conditions
            is_featured: Whether to feature this reward
            valid_from: Optional valid from date
            valid_until: Optional valid until date
            created_by: User ID who created the reward

        Returns:
            Created reward object
        """
        reward = Reward(
            name=name,
            description=description,
            points_required=points_required,
            category=category,
            stock_quantity=stock_quantity,
            max_per_customer=max_per_customer,
            image_url=image_url,
            terms_conditions=terms_conditions,
            is_featured=is_featured,
            status=RewardStatus.ACTIVE,
            valid_from=valid_from or datetime.utcnow(),
            valid_until=valid_until
        )

        self.db.add(reward)
        self.db.commit()
        self.db.refresh(reward)

        logger.info(f"Reward '{name}' created by user {created_by}")
        return reward

    def update_reward(
        self,
        reward_id: int,
        updates: Dict,
        updated_by: int
    ) -> Reward:
        """
        Update an existing reward.

        Args:
            reward_id: Reward ID to update
            updates: Dictionary of fields to update
            updated_by: User ID making the update

        Returns:
            Updated reward object
        """
        reward = self.db.query(Reward).filter(Reward.id == reward_id).first()
        if not reward:
            raise ValueError(f"Reward with ID {reward_id} not found")

        # Update allowed fields
        allowed_fields = [
            'name', 'description', 'points_required', 'category',
            'stock_quantity', 'max_per_customer', 'image_url',
            'terms_conditions', 'is_featured', 'valid_until'
        ]

        for field, value in updates.items():
            if field in allowed_fields:
                setattr(reward, field, value)

        self.db.commit()
        self.db.refresh(reward)

        logger.info(f"Reward {reward_id} updated by user {updated_by}")
        return reward