"""
Customer Service

Handles customer management, tier progression, loyalty points,
and customer analytics operations.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import (
    Customer, CustomerKid, CustomerTierHistory,
    CustomerTier, CustomerStatus, LoyaltyTransaction,
    RewardRedemption, User
)
from ..models import TransactionType, TransactionSource


class CustomerService:
    """
    Service for handling customer operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_customer(self, user_id: int, tier: CustomerTier = CustomerTier.BRONZE, notes: Optional[str] = None) -> Customer:
        """Create a new customer."""
        customer = Customer(
            user_id=user_id,
            tier=tier,
            total_points=0,
            lifetime_points=0,
            current_streak=0,
            longest_streak=0,
            status=CustomerStatus.ACTIVE,
            notes=notes
        )

        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)

        return customer

    def get_customer_by_id(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID."""
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def get_customer_by_user_id(self, user_id: int) -> Optional[Customer]:
        """Get customer by user ID."""
        return self.db.query(Customer).filter(Customer.user_id == user_id).first()

    def update_customer(self, customer_id: int, **kwargs) -> Customer:
        """Update customer information."""
        customer = self.get_customer_by_id(customer_id)

        if not customer:
            raise ValueError("Customer not found")

        for key, value in kwargs.items():
            if hasattr(customer, key):
                setattr(customer, key, value)

        customer.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(customer)

        return customer

    def update_customer_tier(self, customer_id: int, new_tier: CustomerTier, reason: str = "Manual update", changed_by: Optional[int] = None) -> Customer:
        """Update customer tier and create history record."""
        customer = self.get_customer_by_id(customer_id)

        if not customer:
            raise ValueError("Customer not found")

        previous_tier = customer.tier

        # Create tier history record
        tier_history = CustomerTierHistory(
            customer_id=customer_id,
            previous_tier=previous_tier,
            new_tier=new_tier,
            points_at_upgrade=customer.total_points,
            reason=reason,
            changed_by=changed_by
        )

        self.db.add(tier_history)

        # Update customer tier
        customer.tier = new_tier
        customer.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(customer)

        return customer

    def add_loyalty_points(self, customer_id: int, points: int, transaction_type: TransactionType = TransactionType.EARNED,
                          source: TransactionSource = TransactionSource.MANUAL, description: str = "Points added",
                          reference_id: Optional[str] = None, user_id: Optional[int] = None) -> LoyaltyTransaction:
        """Add loyalty points to customer."""
        customer = self.get_customer_by_id(customer_id)

        if not customer:
            raise ValueError("Customer not found")

        if points <= 0:
            raise ValueError("Points must be positive")

        # Create transaction record
        transaction = LoyaltyTransaction(
            user_id=user_id or customer.user_id,
            customer_id=customer_id,
            points=points,
            transaction_type=transaction_type,
            source=source,
            description=description,
            reference_id=reference_id,
            is_active=True
        )

        self.db.add(transaction)

        # Update customer points
        customer.total_points += points
        customer.lifetime_points += points

        # Check for tier upgrade
        if customer.tier == CustomerTier.BRONZE and customer.total_points >= 1000:
            customer = self.update_customer_tier(customer_id, CustomerTier.SILVER, "Automatic tier upgrade")
        elif customer.tier == CustomerTier.SILVER and customer.total_points >= 5000:
            customer = self.update_customer_tier(customer_id, CustomerTier.GOLD, "Automatic tier upgrade")
        elif customer.tier == CustomerTier.GOLD and customer.total_points >= 10000:
            customer = self.update_customer_tier(customer_id, CustomerTier.PLATINUM, "Automatic tier upgrade")

        self.db.commit()
        self.db.refresh(transaction)

        return transaction

    def deduct_loyalty_points(self, customer_id: int, points: int, description: str = "Points deducted",
                             reference_id: Optional[str] = None, user_id: Optional[int] = None) -> LoyaltyTransaction:
        """Deduct loyalty points from customer."""
        customer = self.get_customer_by_id(customer_id)

        if not customer:
            raise ValueError("Customer not found")

        if customer.total_points < points:
            raise ValueError("Insufficient points")

        # Create transaction record
        transaction = LoyaltyTransaction(
            user_id=user_id or customer.user_id,
            customer_id=customer_id,
            points=-points,  # Negative for deduction
            transaction_type=TransactionType.REDEEMED,
            source=TransactionSource.MANUAL,
            description=description,
            reference_id=reference_id,
            is_active=True
        )

        self.db.add(transaction)

        # Update customer points
        customer.total_points -= points
        customer.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(transaction)

        return transaction

    def get_customer_points(self, customer_id: int) -> Dict[str, Any]:
        """Get customer points information."""
        customer = self.get_customer_by_id(customer_id)

        if not customer:
            raise ValueError("Customer not found")

        return {
            "total_points": customer.total_points,
            "lifetime_points": customer.lifetime_points,
            "current_tier": customer.tier.value,
            "next_tier": self._get_next_tier(customer.tier),
            "points_to_next_tier": self._get_points_to_next_tier(customer.total_points, customer.tier)
        }

    def get_customer_transactions(self, customer_id: int, limit: int = 50) -> List[LoyaltyTransaction]:
        """Get customer loyalty transactions."""
        customer = self.get_customer_by_id(customer_id)

        if not customer:
            raise ValueError("Customer not found")

        return self.db.query(LoyaltyTransaction)\
            .filter(LoyaltyTransaction.customer_id == customer_id)\
            .order_by(LoyaltyTransaction.created_at.desc())\
            .limit(limit)\
            .all()

    def get_customer_tier_history(self, customer_id: int) -> List[CustomerTierHistory]:
        """Get customer tier history."""
        customer = self.get_customer_by_id(customer_id)

        if not customer:
            raise ValueError("Customer not found")

        return self.db.query(CustomerTierHistory)\
            .filter(CustomerTierHistory.customer_id == customer_id)\
            .order_by(CustomerTierHistory.created_at.desc())\
            .all()

    def add_customer_kid(self, customer_id: int, name: str, date_of_birth: datetime,
                        gender: Optional[str] = None, notes: Optional[str] = None) -> CustomerKid:
        """Add a kid to customer."""
        customer = self.get_customer_by_id(customer_id)

        if not customer:
            raise ValueError("Customer not found")

        kid = CustomerKid(
            customer_id=customer_id,
            name=name,
            date_of_birth=date_of_birth,
            gender=gender,
            notes=notes,
            is_active=True
        )

        self.db.add(kid)
        self.db.commit()
        self.db.refresh(kid)

        return kid

    def get_customer_kids(self, customer_id: int) -> List[CustomerKid]:
        """Get customer kids."""
        customer = self.get_customer_by_id(customer_id)

        if not customer:
            raise ValueError("Customer not found")

        return self.db.query(CustomerKid)\
            .filter(CustomerKid.customer_id == customer_id, CustomerKid.is_active == True)\
            .all()

    def update_customer_kid(self, kid_id: int, **kwargs) -> CustomerKid:
        """Update customer kid information."""
        kid = self.db.query(CustomerKid).filter(CustomerKid.id == kid_id).first()

        if not kid:
            raise ValueError("Kid not found")

        for key, value in kwargs.items():
            if hasattr(kid, key):
                setattr(kid, key, value)

        kid.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(kid)

        return kid

    def delete_customer_kid(self, kid_id: int) -> None:
        """Delete customer kid (soft delete)."""
        kid = self.db.query(CustomerKid).filter(CustomerKid.id == kid_id).first()

        if not kid:
            raise ValueError("Kid not found")

        kid.is_active = False
        kid.updated_at = datetime.utcnow()
        self.db.commit()

    def get_customer_analytics(self, customer_id: int) -> Dict[str, Any]:
        """Get customer analytics."""
        customer = self.get_customer_by_id(customer_id)

        if not customer:
            raise ValueError("Customer not found")

        # Get transaction summary
        transaction_stats = self.db.query(
            func.sum(LoyaltyTransaction.points).label('total_earned'),
            func.count(LoyaltyTransaction.id).label('total_transactions')
        ).filter(
            LoyaltyTransaction.customer_id == customer_id,
            LoyaltyTransaction.points > 0
        ).first()

        # Get redemption summary
        redemption_stats = self.db.query(
            func.count(RewardRedemption.id).label('total_redemptions'),
            func.sum(RewardRedemption.quantity).label('total_items_redeemed')
        ).filter(
            RewardRedemption.customer_id == customer_id
        ).first()

        return {
            "total_earned": transaction_stats.total_earned or 0,
            "total_transactions": transaction_stats.total_transactions or 0,
            "total_redemptions": redemption_stats.total_redemptions or 0,
            "total_items_redeemed": redemption_stats.total_items_redeemed or 0,
            "current_tier": customer.tier.value,
            "join_date": customer.joined_date,
            "last_activity": customer.last_activity
        }

    def get_customers_list(self, skip: int = 0, limit: int = 100, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Get paginated list of customers with optional filters."""
        query = self.db.query(Customer)

        if filters:
            if 'tier' in filters:
                query = query.filter(Customer.tier == filters['tier'])
            if 'status' in filters:
                query = query.filter(Customer.status == filters['status'])
            if 'search' in filters:
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    Customer.notes.ilike(search_term)
                )

        total = query.count()
        customers = query.offset(skip).limit(limit).all()

        return {
            "customers": customers,
            "total": total,
            "skip": skip,
            "limit": limit
        }

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

    def calculate_tier_benefits(self, tier: CustomerTier) -> List[Dict[str, Any]]:
        """Calculate benefits for a specific tier."""
        # This would typically fetch from a tier_benefits table
        # For now, return hardcoded benefits
        benefits = {
            CustomerTier.BRONZE: [
                {"type": "discount", "value": "5%", "description": "Base discount on all purchases"}
            ],
            CustomerTier.SILVER: [
                {"type": "discount", "value": "10%", "description": "Enhanced discount on all purchases"},
                {"type": "priority_support", "value": "Standard", "description": "Priority customer support"}
            ],
            CustomerTier.GOLD: [
                {"type": "discount", "value": "15%", "description": "Premium discount on all purchases"},
                {"type": "priority_support", "value": "Premium", "description": "Premium customer support"},
                {"type": "free_shipping", "value": "All orders", "description": "Free shipping on all orders"}
            ],
            CustomerTier.PLATINUM: [
                {"type": "discount", "value": "20%", "description": "VIP discount on all purchases"},
                {"type": "priority_support", "value": "VIP", "description": "VIP customer support"},
                {"type": "free_shipping", "value": "All orders", "description": "Free shipping on all orders"},
                {"type": "exclusive_access", "value": "Events", "description": "Access to exclusive events"}
            ]
        }

        return benefits.get(tier, [])