"""
Loyalty Service

Handles loyalty points management, tier progression, transaction processing,
and loyalty program business logic.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ..models import (
    LoyaltyTransaction, Reward, RewardRedemption,
    Customer, TierBenefit, User, TransactionType,
    TransactionSource, RewardStatus, CustomerTier
)
from ..models import CustomerTierHistory


class LoyaltyService:
    """
    Service for handling loyalty program operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def award_points(self, customer_id: int, points: int, source: TransactionSource = TransactionSource.MANUAL,
                    description: str = "Points awarded", reference_id: Optional[str] = None,
                    user_id: Optional[int] = None, expires_at: Optional[datetime] = None) -> LoyaltyTransaction:
        """Award points to a customer."""
        if points <= 0:
            raise ValueError("Points must be positive")

        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError("Customer not found")

        # Create transaction record
        transaction = LoyaltyTransaction(
            user_id=user_id or customer.user_id,
            customer_id=customer_id,
            points=points,
            transaction_type=TransactionType.EARNED,
            source=source,
            description=description,
            reference_id=reference_id,
            expires_at=expires_at,
            is_active=True
        )

        self.db.add(transaction)

        # Update customer points and check for tier upgrades
        customer.total_points += points
        customer.lifetime_points += points

        # Check for automatic tier upgrades
        if customer.tier == CustomerTier.BRONZE and customer.total_points >= 1000:
            self._upgrade_customer_tier(customer, CustomerTier.SILVER, "Automatic upgrade based on points")
        elif customer.tier == CustomerTier.SILVER and customer.total_points >= 5000:
            self._upgrade_customer_tier(customer, CustomerTier.GOLD, "Automatic upgrade based on points")
        elif customer.tier == CustomerTier.GOLD and customer.total_points >= 10000:
            self._upgrade_customer_tier(customer, CustomerTier.PLATINUM, "Automatic upgrade based on points")

        customer.last_activity = datetime.utcnow()
        self.db.commit()
        self.db.refresh(transaction)

        return transaction

    def deduct_points(self, customer_id: int, points: int, source: TransactionSource = TransactionSource.MANUAL,
                     description: str = "Points deducted", reference_id: Optional[str] = None,
                     user_id: Optional[int] = None) -> LoyaltyTransaction:
        """Deduct points from a customer."""
        if points <= 0:
            raise ValueError("Points must be positive")

        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError("Customer not found")

        if customer.total_points < points:
            raise ValueError("Insufficient points")

        # Create transaction record
        transaction = LoyaltyTransaction(
            user_id=user_id or customer.user_id,
            customer_id=customer_id,
            points=-points,
            transaction_type=TransactionType.REDEEMED,
            source=source,
            description=description,
            reference_id=reference_id,
            is_active=True
        )

        self.db.add(transaction)

        # Update customer points
        customer.total_points -= points
        customer.last_activity = datetime.utcnow()

        self.db.commit()
        self.db.refresh(transaction)

        return transaction

    def transfer_points(self, from_customer_id: int, to_customer_id: int, points: int,
                       description: str = "Points transfer", user_id: Optional[int] = None) -> List[LoyaltyTransaction]:
        """Transfer points between customers."""
        if points <= 0:
            raise ValueError("Points must be positive")

        from_customer = self.db.query(Customer).filter(Customer.id == from_customer_id).first()
        to_customer = self.db.query(Customer).filter(Customer.id == to_customer_id).first()

        if not from_customer or not to_customer:
            raise ValueError("Customer not found")

        if from_customer.total_points < points:
            raise ValueError("Insufficient points for transfer")

        # Create deduction transaction for sender
        deduct_transaction = LoyaltyTransaction(
            user_id=user_id or from_customer.user_id,
            customer_id=from_customer_id,
            points=-points,
            transaction_type=TransactionType.TRANSFER,
            source=TransactionSource.MANUAL,
            description=f"{description} to {to_customer.user_id}",
            is_active=True
        )

        # Create addition transaction for receiver
        add_transaction = LoyaltyTransaction(
            user_id=user_id or to_customer.user_id,
            customer_id=to_customer_id,
            points=points,
            transaction_type=TransactionType.EARNED,
            source=TransactionSource.TRANSFER,
            description=f"{description} from {from_customer.user_id}",
            is_active=True
        )

        self.db.add(deduct_transaction)
        self.db.add(add_transaction)

        # Update customer points
        from_customer.total_points -= points
        to_customer.total_points += points

        from_customer.last_activity = datetime.utcnow()
        to_customer.last_activity = datetime.utcnow()

        self.db.commit()
        self.db.refresh(deduct_transaction)
        self.db.refresh(add_transaction)

        return [deduct_transaction, add_transaction]

    def get_customer_points_summary(self, customer_id: int) -> Dict[str, Any]:
        """Get comprehensive points summary for a customer."""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError("Customer not found")

        # Get transaction summary
        transaction_stats = self.db.query(
            func.sum(LoyaltyTransaction.points).label('total_earned'),
            func.sum(func.abs(LoyaltyTransaction.points)).filter(LoyaltyTransaction.points < 0).label('total_spent'),
            func.count(LoyaltyTransaction.id).label('total_transactions')
        ).filter(
            LoyaltyTransaction.customer_id == customer_id,
            LoyaltyTransaction.is_active == True
        ).first()

        # Get expiring points
        expiring_points = self.db.query(
            func.sum(LoyaltyTransaction.points)
        ).filter(
            LoyaltyTransaction.customer_id == customer_id,
            LoyaltyTransaction.expires_at <= datetime.utcnow() + timedelta(days=30),
            LoyaltyTransaction.expires_at > datetime.utcnow(),
            LoyaltyTransaction.points > 0,
            LoyaltyTransaction.is_active == True
        ).scalar() or 0

        # Get expired points (not yet cleaned up)
        expired_points = self.db.query(
            func.sum(LoyaltyTransaction.points)
        ).filter(
            LoyaltyTransaction.customer_id == customer_id,
            LoyaltyTransaction.expires_at <= datetime.utcnow(),
            LoyaltyTransaction.points > 0,
            LoyaltyTransaction.is_active == True
        ).scalar() or 0

        return {
            "current_balance": customer.total_points,
            "lifetime_earned": customer.lifetime_points,
            "total_earned": transaction_stats.total_earned or 0,
            "total_spent": abs(transaction_stats.total_spent or 0),
            "total_transactions": transaction_stats.total_transactions or 0,
            "expiring_soon": expiring_points,
            "expired": expired_points,
            "current_tier": customer.tier.value,
            "next_tier": self._get_next_tier(customer.tier),
            "points_to_next_tier": self._get_points_to_next_tier(customer.total_points, customer.tier),
            "join_date": customer.joined_date,
            "last_activity": customer.last_activity
        }

    def get_transaction_history(self, customer_id: int, limit: int = 50, offset: int = 0,
                               filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Get paginated transaction history with optional filters."""
        query = self.db.query(LoyaltyTransaction).filter(
            LoyaltyTransaction.customer_id == customer_id,
            LoyaltyTransaction.is_active == True
        )

        if filters:
            if 'type' in filters:
                query = query.filter(LoyaltyTransaction.transaction_type == filters['type'])
            if 'source' in filters:
                query = query.filter(LoyaltyTransaction.source == filters['source'])
            if 'date_from' in filters:
                query = query.filter(LoyaltyTransaction.created_at >= filters['date_from'])
            if 'date_to' in filters:
                query = query.filter(LoyaltyTransaction.created_at <= filters['date_to'])

        total = query.count()
        transactions = query.order_by(LoyaltyTransaction.created_at.desc()).offset(offset).limit(limit).all()

        return {
            "transactions": transactions,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    def expire_points(self, customer_id: int) -> List[LoyaltyTransaction]:
        """Mark expired points as inactive."""
        now = datetime.utcnow()
        expired_transactions = self.db.query(LoyaltyTransaction).filter(
            LoyaltyTransaction.customer_id == customer_id,
            LoyaltyTransaction.expires_at <= now,
            LoyaltyTransaction.points > 0,
            LoyaltyTransaction.is_active == True
        ).all()

        for transaction in expired_transactions:
            transaction.is_active = False
            # Create adjustment transaction for the negative points
            adjustment = LoyaltyTransaction(
                user_id=transaction.user_id,
                customer_id=customer_id,
                points=-transaction.points,
                transaction_type=TransactionType.EXPIRED,
                source=TransactionSource.SYSTEM,
                description=f"Points expired from transaction {transaction.id}",
                reference_id=str(transaction.id),
                is_active=True
            )
            self.db.add(adjustment)

        if expired_transactions:
            # Update customer balance
            customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
            if customer:
                customer.total_points -= sum(t.points for t in expired_transactions)
                customer.last_activity = now

            self.db.commit()

        return expired_transactions

    def get_tier_benefits(self, tier: CustomerTier) -> List[Dict[str, Any]]:
        """Get benefits for a specific tier."""
        # This would typically fetch from tier_benefits table
        # For now, return hardcoded benefits
        benefits = {
            CustomerTier.BRONZE: [
                {"type": "points_multiplier", "value": "1x", "description": "Standard points earning rate"},
                {"type": "discount", "value": "5%", "description": "Base discount on all purchases"}
            ],
            CustomerTier.SILVER: [
                {"type": "points_multiplier", "value": "1.5x", "description": "50% bonus points on all purchases"},
                {"type": "discount", "value": "10%", "description": "Enhanced discount on all purchases"},
                {"type": "priority_support", "value": "Standard", "description": "Priority customer support"}
            ],
            CustomerTier.GOLD: [
                {"type": "points_multiplier", "value": "2x", "description": "Double points on all purchases"},
                {"type": "discount", "value": "15%", "description": "Premium discount on all purchases"},
                {"type": "priority_support", "value": "Premium", "description": "Premium customer support"},
                {"type": "free_shipping", "value": "All orders", "description": "Free shipping on all orders"}
            ],
            CustomerTier.PLATINUM: [
                {"type": "points_multiplier", "value": "3x", "description": "Triple points on all purchases"},
                {"type": "discount", "value": "20%", "description": "VIP discount on all purchases"},
                {"type": "priority_support", "value": "VIP", "description": "VIP customer support"},
                {"type": "free_shipping", "value": "All orders", "description": "Free shipping on all orders"},
                {"type": "exclusive_access", "value": "Events", "description": "Access to exclusive events"}
            ]
        }

        return benefits.get(tier, [])

    def get_tier_requirements(self) -> Dict[str, Any]:
        """Get requirements for each tier."""
        return {
            "bronze": {"min_points": 0, "description": "Entry level tier"},
            "silver": {"min_points": 1000, "description": "Intermediate tier with enhanced benefits"},
            "gold": {"min_points": 5000, "description": "Premium tier with exclusive benefits"},
            "platinum": {"min_points": 10000, "description": "VIP tier with maximum benefits"}
        }

    def _upgrade_customer_tier(self, customer: Customer, new_tier: CustomerTier, reason: str):
        """Upgrade customer tier and create history record."""
        previous_tier = customer.tier

        # Create tier history record
        tier_history = CustomerTierHistory(
            customer_id=customer.id,
            previous_tier=previous_tier,
            new_tier=new_tier,
            points_at_upgrade=customer.total_points,
            reason=reason,
            changed_by=None  # System upgrade
        )

        self.db.add(tier_history)
        customer.tier = new_tier
        customer.updated_at = datetime.utcnow()

    def _get_next_tier(self, current_tier: CustomerTier) -> Optional[CustomerTier]:
        """Get next tier for a customer."""
        tier_order = {
            CustomerTier.BRONZE: CustomerTier.SILVER,
            CustomerTier.SILVER: CustomerTier.GOLD,
            CustomerTier.GOLD: CustomerTier.PLATINUM,
            CustomerTier.PLATINUM: None
        }

        return tier_order.get(current_tier)

    def _get_points_to_next_tier(self, current_points: int, current_tier: CustomerTier) -> Optional[int]:
        """Get points needed to reach next tier."""
        tier_thresholds = {
            CustomerTier.BRONZE: 1000,
            CustomerTier.SILVER: 5000,
            CustomerTier.GOLD: 10000,
            CustomerTier.PLATINUM: None
        }

        next_tier_threshold = tier_thresholds.get(self._get_next_tier(current_tier))

        if next_tier_threshold is None:
            return None

        return max(0, next_tier_threshold - current_points)

    def get_loyalty_analytics(self, start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get loyalty program analytics."""
        query = self.db.query(LoyaltyTransaction)

        if start_date:
            query = query.filter(LoyaltyTransaction.created_at >= start_date)
        if end_date:
            query = query.filter(LoyaltyTransaction.created_at <= end_date)

        # Get basic statistics
        total_transactions = query.count()
        total_points_earned = query.filter(LoyaltyTransaction.points > 0).with_entities(func.sum(LoyaltyTransaction.points)).scalar() or 0
        total_points_spent = abs(query.filter(LoyaltyTransaction.points < 0).with_entities(func.sum(LoyaltyTransaction.points)).scalar() or 0)

        # Get transaction type breakdown
        type_breakdown = {}
        for transaction_type in TransactionType:
            count = query.filter(LoyaltyTransaction.transaction_type == transaction_type).count()
            type_breakdown[transaction_type.value] = count

        # Get source breakdown
        source_breakdown = {}
        for source in TransactionSource:
            count = query.filter(LoyaltyTransaction.source == source).count()
            source_breakdown[source.value] = count

        # Get tier distribution
        tier_distribution = {}
        for tier in CustomerTier:
            count = self.db.query(Customer).filter(Customer.tier == tier).count()
            tier_distribution[tier.value] = count

        return {
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "transactions": {
                "total": total_transactions,
                "by_type": type_breakdown,
                "by_source": source_breakdown
            },
            "points": {
                "earned": total_points_earned,
                "spent": total_points_spent,
                "net": total_points_earned - total_points_spent
            },
            "customers": {
                "by_tier": tier_distribution,
                "total": sum(tier_distribution.values())
            }
        }