"""
Reward Service

Handles reward catalog management, redemptions, inventory tracking,
and reward-related business logic.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ..models import (
    Reward, RewardRedemption, LoyaltyTransaction,
    Customer, User, RewardStatus, TransactionType,
    TransactionSource
)


class RewardService:
    """
    Service for handling reward operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_reward(self, name: str, description: Optional[str], points_required: int,
                     category: Optional[str] = None, image_url: Optional[str] = None,
                     stock_quantity: int = 0, max_per_customer: int = 1,
                     valid_from: Optional[datetime] = None, valid_until: Optional[datetime] = None,
                     terms_conditions: Optional[str] = None, is_featured: bool = False,
                     created_by: int = None) -> Reward:
        """Create a new reward."""
        if points_required <= 0:
            raise ValueError("Points required must be positive")

        if stock_quantity < 0:
            raise ValueError("Stock quantity cannot be negative")

        reward = Reward(
            name=name,
            description=description,
            points_required=points_required,
            category=category,
            image_url=image_url,
            status=RewardStatus.ACTIVE,
            stock_quantity=stock_quantity,
            max_per_customer=max_per_customer,
            valid_from=valid_from or datetime.utcnow(),
            valid_until=valid_until,
            terms_conditions=terms_conditions,
            is_featured=is_featured,
            created_by=created_by
        )

        self.db.add(reward)
        self.db.commit()
        self.db.refresh(reward)

        return reward

    def get_reward_by_id(self, reward_id: int) -> Optional[Reward]:
        """Get reward by ID."""
        return self.db.query(Reward).filter(Reward.id == reward_id).first()

    def get_available_rewards(self, customer_id: Optional[int] = None, category: Optional[str] = None) -> List[Reward]:
        """Get available rewards, optionally filtered by customer eligibility."""
        query = self.db.query(Reward).filter(
            Reward.status == RewardStatus.ACTIVE,
            Reward.valid_from <= datetime.utcnow(),
            Reward.stock_quantity > 0
        )

        if Reward.valid_until.isnot(None):
            query = query.filter(Reward.valid_until >= datetime.utcnow())

        if category:
            query = query.filter(Reward.category == category)

        rewards = query.all()

        if customer_id:
            # Filter by customer eligibility (points and redemption limits)
            customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
            if customer:
                eligible_rewards = []
                for reward in rewards:
                    if self._is_customer_eligible_for_reward(customer, reward):
                        eligible_rewards.append(reward)
                return eligible_rewards

        return rewards

    def redeem_reward(self, customer_id: int, reward_id: int, quantity: int = 1,
                     notes: Optional[str] = None, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Redeem a reward for a customer."""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        reward = self.get_reward_by_id(reward_id)

        if not customer:
            raise ValueError("Customer not found")

        if not reward:
            raise ValueError("Reward not found")

        if reward.status != RewardStatus.ACTIVE:
            raise ValueError("Reward is not available")

        if reward.stock_quantity < quantity:
            raise ValueError("Insufficient stock")

        if not self._is_customer_eligible_for_reward(customer, reward, quantity):
            raise ValueError("Customer is not eligible for this reward")

        # Check if customer has already reached max redemptions for this reward
        existing_redemptions = self.db.query(RewardRedemption).filter(
            RewardRedemption.customer_id == customer_id,
            RewardRedemption.reward_id == reward_id,
            RewardRedemption.status.in_(["pending", "approved", "fulfilled"])
        ).count()

        if existing_redemptions >= reward.max_per_customer:
            raise ValueError("Maximum redemptions per customer reached")

        total_points_required = reward.points_required * quantity

        if customer.total_points < total_points_required:
            raise ValueError("Insufficient points")

        # Create redemption record
        redemption = RewardRedemption(
            transaction_id=None,  # Will be set after transaction creation
            reward_id=reward_id,
            customer_id=customer_id,
            quantity=quantity,
            redemption_code=self._generate_redemption_code(),
            status="pending",
            notes=notes
        )

        self.db.add(redemption)

        # Deduct points
        transaction = self.db.query(LoyaltyTransaction).filter(
            LoyaltyTransaction.customer_id == customer_id,
            LoyaltyTransaction.points == -total_points_required,
            LoyaltyTransaction.transaction_type == TransactionType.REDEEMED,
            LoyaltyTransaction.description.like(f"%Reward redemption%")
        ).first()

        if not transaction:
            # Create points deduction transaction
            from ..services.loyalty_service import LoyaltyService
            loyalty_service = LoyaltyService(self.db)

            transaction = loyalty_service.deduct_points(
                customer_id=customer_id,
                points=total_points_required,
                source=TransactionSource.REDEMPTION,
                description=f"Reward redemption: {reward.name}",
                user_id=user_id
            )

        # Update redemption with transaction ID
        redemption.transaction_id = transaction.id

        # Update reward stock
        reward.stock_quantity -= quantity

        # Check if reward should be deactivated due to low stock
        if reward.stock_quantity == 0:
            reward.status = RewardStatus.OUT_OF_STOCK

        customer.last_activity = datetime.utcnow()
        self.db.commit()
        self.db.refresh(redemption)

        return {
            "redemption": redemption,
            "transaction": transaction,
            "reward": reward
        }

    def get_customer_redemptions(self, customer_id: int, status: Optional[str] = None,
                                limit: int = 50) -> List[RewardRedemption]:
        """Get customer redemption history."""
        query = self.db.query(RewardRedemption).filter(RewardRedemption.customer_id == customer_id)

        if status:
            query = query.filter(RewardRedemption.status == status)

        return query.order_by(RewardRedemption.created_at.desc()).limit(limit).all()

    def fulfill_redemption(self, redemption_id: int, fulfilled_by: int,
                          notes: Optional[str] = None) -> RewardRedemption:
        """Mark a redemption as fulfilled."""
        redemption = self.db.query(RewardRedemption).filter(RewardRedemption.id == redemption_id).first()

        if not redemption:
            raise ValueError("Redemption not found")

        if redemption.status not in ["pending", "approved"]:
            raise ValueError("Redemption cannot be fulfilled in current status")

        redemption.status = "fulfilled"
        redemption.fulfilled_at = datetime.utcnow()
        redemption.fulfilled_by = fulfilled_by
        redemption.notes = notes or redemption.notes

        self.db.commit()
        self.db.refresh(redemption)

        return redemption

    def cancel_redemption(self, redemption_id: int, notes: Optional[str] = None) -> RewardRedemption:
        """Cancel a redemption and restore points."""
        redemption = self.db.query(RewardRedemption).filter(RewardRedemption.id == redemption_id).first()

        if not redemption:
            raise ValueError("Redemption not found")

        if redemption.status not in ["pending", "approved"]:
            raise ValueError("Redemption cannot be cancelled in current status")

        # Restore points
        if redemption.transaction_id:
            transaction = self.db.query(LoyaltyTransaction).filter(
                LoyaltyTransaction.id == redemption.transaction_id
            ).first()

            if transaction:
                # Create reversal transaction
                from ..services.loyalty_service import LoyaltyService
                loyalty_service = LoyaltyService(self.db)

                loyalty_service.award_points(
                    customer_id=redemption.customer_id,
                    points=abs(transaction.points),
                    source=TransactionSource.REDEMPTION,
                    description=f"Redemption cancelled: {redemption.reward.name}",
                    reference_id=str(redemption.id)
                )

                transaction.is_active = False

        # Restore stock
        reward = self.get_reward_by_id(redemption.reward_id)
        if reward:
            reward.stock_quantity += redemption.quantity

            if reward.stock_quantity > 0 and reward.status == RewardStatus.OUT_OF_STOCK:
                reward.status = RewardStatus.ACTIVE

        redemption.status = "cancelled"
        redemption.notes = notes or redemption.notes

        self.db.commit()
        self.db.refresh(redemption)

        return redemption

    def get_reward_categories(self) -> List[str]:
        """Get all unique reward categories."""
        categories = self.db.query(Reward.category).distinct().filter(
            Reward.category.isnot(None)
        ).all()

        return [cat[0] for cat in categories if cat[0]]

    def get_featured_rewards(self, limit: int = 10) -> List[Reward]:
        """Get featured rewards."""
        return self.db.query(Reward).filter(
            Reward.is_featured == True,
            Reward.status == RewardStatus.ACTIVE
        ).limit(limit).all()

    def update_reward_stock(self, reward_id: int, new_stock: int) -> Reward:
        """Update reward stock quantity."""
        reward = self.get_reward_by_id(reward_id)

        if not reward:
            raise ValueError("Reward not found")

        if new_stock < 0:
            raise ValueError("Stock quantity cannot be negative")

        previous_stock = reward.stock_quantity
        reward.stock_quantity = new_stock

        # Update status based on stock
        if new_stock == 0 and previous_stock > 0:
            reward.status = RewardStatus.OUT_OF_STOCK
        elif new_stock > 0 and reward.status == RewardStatus.OUT_OF_STOCK:
            reward.status = RewardStatus.ACTIVE

        self.db.commit()
        self.db.refresh(reward)

        return reward

    def get_reward_analytics(self, start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get reward analytics."""
        query = self.db.query(RewardRedemption)

        if start_date:
            query = query.filter(RewardRedemption.created_at >= start_date)
        if end_date:
            query = query.filter(RewardRedemption.created_at <= end_date)

        total_redemptions = query.count()

        # Status breakdown
        status_breakdown = {}
        for status in ["pending", "approved", "fulfilled", "cancelled"]:
            count = query.filter(RewardRedemption.status == status).count()
            status_breakdown[status] = count

        # Most popular rewards
        popular_rewards = self.db.query(
            RewardRedemption.reward_id,
            func.count(RewardRedemption.id).label('redemption_count')
        ).group_by(RewardRedemption.reward_id).order_by(
            func.count(RewardRedemption.id).desc()
        ).limit(10).all()

        # Total points redeemed
        total_points_redeemed = abs(
            self.db.query(func.sum(LoyaltyTransaction.points)).filter(
                LoyaltyTransaction.transaction_type == TransactionType.REDEEMED,
                LoyaltyTransaction.source == TransactionSource.REDEMPTION
            ).scalar() or 0
        )

        # Reward inventory status
        inventory_status = self.db.query(
            func.sum(Reward.stock_quantity).label('total_stock'),
            func.count(Reward.id).label('total_rewards'),
            func.count(func.case((Reward.stock_quantity == 0, 1))).label('out_of_stock')
        ).first()

        return {
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "redemptions": {
                "total": total_redemptions,
                "by_status": status_breakdown,
                "points_redeemed": total_points_redeemed
            },
            "popular_rewards": [
                {"reward_id": r.reward_id, "redemption_count": r.redemption_count}
                for r in popular_rewards
            ],
            "inventory": {
                "total_stock": inventory_status.total_stock or 0,
                "total_rewards": inventory_status.total_rewards or 0,
                "out_of_stock": inventory_status.out_of_stock or 0
            }
        }

    def _is_customer_eligible_for_reward(self, customer: Customer, reward: Reward, quantity: int = 1) -> bool:
        """Check if customer is eligible for a reward."""
        if customer.total_points < (reward.points_required * quantity):
            return False

        # Check if customer has reached max redemptions
        existing_redemptions = self.db.query(RewardRedemption).filter(
            RewardRedemption.customer_id == customer.id,
            RewardRedemption.reward_id == reward.id,
            RewardRedemption.status.in_(["pending", "approved", "fulfilled"])
        ).count()

        return existing_redemptions < reward.max_per_customer

    def _generate_redemption_code(self) -> str:
        """Generate a unique redemption code."""
        import random
        import string

        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            existing = self.db.query(RewardRedemption).filter(
                RewardRedemption.redemption_code == code
            ).first()

            if not existing:
                return code