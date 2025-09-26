"""
Customer Management Business Logic Service.

Handles customer CRUD operations, search and filtering, analytics, segmentation,
and kids information management.
"""

from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, text
import logging
import re
from collections import defaultdict

from ..models import (
    User, UserRole, UserStatus,
    Customer, CustomerTier, CustomerStatus, CustomerTierHistory,
    CustomerKid,
    LoyaltyTransaction, TransactionType, TransactionSource,
    RewardRedemption,
    BirthdayPromotion,
    Affiliate, CustomerReferral
)
from ..core.database import SessionLocal

logger = logging.getLogger(__name__)


class CustomerService:
    """Service class for customer management operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_customer_list(
        self,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        tier: Optional[CustomerTier] = None,
        status: Optional[CustomerStatus] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Dict:
        """
        Get paginated list of customers with filtering and sorting.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Search term for name, email, or phone
            tier: Filter by customer tier
            status: Filter by customer status
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)

        Returns:
            Dictionary with customers and pagination info
        """
        query = self.db.query(Customer).join(User)

        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.name.ilike(search_term),
                    User.email.ilike(search_term),
                    User.phone.ilike(search_term)
                )
            )

        if tier:
            query = query.filter(Customer.tier == tier)

        if status:
            query = query.filter(Customer.status == status)

        # Apply sorting
        valid_sort_fields = {
            "name": User.name,
            "email": User.email,
            "phone": User.phone,
            "tier": Customer.tier,
            "total_points": Customer.total_points,
            "created_at": Customer.created_at,
            "last_activity": Customer.last_activity
        }

        sort_field = valid_sort_fields.get(sort_by, Customer.created_at)
        if sort_order.lower() == "desc":
            sort_field = sort_field.desc()

        total = query.count()
        customers = query.order_by(sort_field).offset(skip).limit(limit).all()

        return {
            "customers": [
                {
                    "id": customer.id,
                    "user_id": customer.user_id,
                    "name": customer.user.name,
                    "email": customer.user.email,
                    "phone": customer.user.phone,
                    "tier": customer.tier.value,
                    "total_points": customer.total_points,
                    "lifetime_points": customer.lifetime_points,
                    "current_streak": customer.current_streak,
                    "longest_streak": customer.longest_streak,
                    "status": customer.status.value,
                    "joined_date": customer.joined_date.isoformat(),
                    "last_activity": customer.last_activity.isoformat(),
                    "created_at": customer.created_at.isoformat()
                }
                for customer in customers
            ],
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_more": skip + limit < total
            }
        }

    def get_customer_details(self, customer_id: int) -> Dict:
        """
        Get detailed customer information including activity and statistics.

        Args:
            customer_id: Customer ID

        Returns:
            Dictionary with comprehensive customer data
        """
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found")

        # Get recent transactions
        recent_transactions = self.db.query(LoyaltyTransaction).filter(
            LoyaltyTransaction.customer_id == customer_id
        ).order_by(LoyaltyTransaction.created_at.desc()).limit(10).all()

        # Get recent redemptions
        recent_redemptions = self.db.query(RewardRedemption).filter(
            RewardRedemption.customer_id == customer_id
        ).order_by(RewardRedemption.created_at.desc()).limit(5).all()

        # Get kids information
        kids = self.db.query(CustomerKid).filter(
            CustomerKid.customer_id == customer_id
        ).all()

        # Get tier history
        tier_history = self.db.query(CustomerTierHistory).filter(
            CustomerTierHistory.customer_id == customer_id
        ).order_by(CustomerTierHistory.created_at.desc()).limit(5).all()

        # Calculate analytics
        analytics = self._calculate_customer_analytics(customer_id)

        return {
            "customer": {
                "id": customer.id,
                "user_id": customer.user_id,
                "name": customer.user.name,
                "email": customer.user.email,
                "phone": customer.user.phone,
                "tier": customer.tier.value,
                "total_points": customer.total_points,
                "lifetime_points": customer.lifetime_points,
                "current_streak": customer.current_streak,
                "longest_streak": customer.longest_streak,
                "status": customer.status.value,
                "joined_date": customer.joined_date.isoformat(),
                "last_activity": customer.last_activity.isoformat(),
                "created_at": customer.created_at.isoformat()
            },
            "analytics": analytics,
            "recent_transactions": [
                {
                    "id": t.id,
                    "points": t.points,
                    "type": t.transaction_type.value,
                    "source": t.source.value,
                    "description": t.description,
                    "created_at": t.created_at.isoformat()
                }
                for t in recent_transactions
            ],
            "recent_redemptions": [
                {
                    "id": r.id,
                    "reward_name": r.reward.name,
                    "reward_category": r.reward.category,
                    "points_required": r.reward.points_required,
                    "quantity": r.quantity,
                    "status": r.status,
                    "created_at": r.created_at.isoformat()
                }
                for r in recent_redemptions
            ],
            "kids": [
                {
                    "id": kid.id,
                    "name": kid.name,
                    "date_of_birth": kid.date_of_birth.isoformat(),
                    "gender": kid.gender,
                    "notes": kid.notes,
                    "is_active": kid.is_active,
                    "age": self._calculate_age(kid.date_of_birth)
                }
                for kid in kids
            ],
            "tier_history": [
                {
                    "id": h.id,
                    "previous_tier": h.previous_tier.value if h.previous_tier else None,
                    "new_tier": h.new_tier.value,
                    "points_at_upgrade": h.points_at_upgrade,
                    "reason": h.reason,
                    "changed_by": h.changed_by,
                    "created_at": h.created_at.isoformat()
                }
                for h in tier_history
            ]
        }

    def _calculate_age(self, birth_date: datetime) -> int:
        """Calculate age from birth date."""
        today = datetime.now()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    def _calculate_customer_analytics(self, customer_id: int) -> Dict:
        """
        Calculate customer analytics including spending patterns and engagement.

        Args:
            customer_id: Customer ID

        Returns:
            Dictionary with customer analytics
        """
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found")

        # Get transaction statistics
        transactions = self.db.query(LoyaltyTransaction).filter(
            LoyaltyTransaction.customer_id == customer_id
        ).all()

        # Separate earned vs spent points
        earned_points = sum(t.points for t in transactions if t.points > 0)
        spent_points = sum(abs(t.points) for t in transactions if t.points < 0)

        # Transaction type breakdown
        transaction_types = defaultdict(int)
        transaction_sources = defaultdict(int)

        for t in transactions:
            transaction_types[t.transaction_type.value] += 1
            transaction_sources[t.source.value] += 1

        # Recent activity (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_transactions = [t for t in transactions if t.created_at >= thirty_days_ago]
        recent_activity_score = len(recent_transactions)

        # Average points per transaction
        avg_points_per_transaction = earned_points / len([t for t in transactions if t.points > 0]) if transaction_types.get('earned', 0) > 0 else 0

        # Calculate tier progress
        tier_thresholds = {
            CustomerTier.BRONZE: 0,
            CustomerTier.SILVER: 200,
            CustomerTier.GOLD: 500,
            CustomerTier.PLATINUM: 1000
        }

        current_threshold = tier_thresholds[customer.tier]
        next_tier = None
        points_to_next = 0

        for tier, threshold in tier_thresholds.items():
            if threshold > current_threshold:
                next_tier = tier
                points_to_next = threshold - customer.total_points
                break

        return {
            "total_transactions": len(transactions),
            "earned_points": earned_points,
            "spent_points": spent_points,
            "net_points": customer.total_points,
            "transaction_types": dict(transaction_types),
            "transaction_sources": dict(transaction_sources),
            "recent_activity_score": recent_activity_score,
            "avg_points_per_transaction": round(avg_points_per_transaction, 2),
            "current_tier": customer.tier.value,
            "next_tier": next_tier.value if next_tier else None,
            "points_to_next_tier": points_to_next,
            "tier_progress": min(1.0, customer.total_points / (next_tier_threshold if next_tier else 1)) if next_tier else 1.0,
            "engagement_score": self._calculate_engagement_score(transactions, customer.last_activity)
        }

    def _calculate_engagement_score(self, transactions: List, last_activity: datetime) -> float:
        """
        Calculate customer engagement score based on activity patterns.

        Args:
            transactions: List of customer transactions
            last_activity: Customer's last activity date

        Returns:
            Engagement score (0-100)
        """
        score = 0

        # Recency score (0-40 points)
        days_since_active = (datetime.now() - last_activity).days
        if days_since_active <= 7:
            score += 40
        elif days_since_active <= 30:
            score += 30
        elif days_since_active <= 90:
            score += 20
        elif days_since_active <= 180:
            score += 10

        # Frequency score (0-30 points)
        transaction_count = len(transactions)
        if transaction_count >= 20:
            score += 30
        elif transaction_count >= 10:
            score += 20
        elif transaction_count >= 5:
            score += 10

        # Consistency score (0-30 points)
        if transaction_count > 0:
            # Check for regular activity (multiple transactions over time)
            first_transaction = min(t.created_at for t in transactions)
            days_active = (datetime.now() - first_transaction).days
            if days_active > 0:
                transactions_per_day = transaction_count / days_active
                if transactions_per_day >= 0.1:  # At least 1 transaction per 10 days
                    score += 30
                elif transactions_per_day >= 0.05:
                    score += 20
                elif transactions_per_day >= 0.02:
                    score += 10

        return min(score, 100)

    def create_customer(
        self,
        name: str,
        email: str,
        phone: str,
        tier: Optional[CustomerTier] = CustomerTier.BRONZE,
        notes: Optional[str] = None
    ) -> Customer:
        """
        Create a new customer.

        Args:
            name: Customer name
            email: Customer email
            phone: Customer phone number
            tier: Initial tier (default: Bronze)
            notes: Optional notes

        Returns:
            Created customer object
        """
        # Check if user already exists
        existing_user = self.db.query(User).filter(
            or_(User.email == email, User.phone == phone)
        ).first()

        if existing_user:
            raise ValueError("User with this email or phone already exists")

        # Create user
        user = User(
            name=name,
            email=email,
            phone=phone,
            password_hash="temp_password",  # Should be set properly
            role=UserRole.CUSTOMER,
            status=UserStatus.ACTIVE,
            email_verified=True,
            phone_verified=True
        )

        self.db.add(user)
        self.db.flush()  # Get user ID

        # Create customer
        customer = Customer(
            user_id=user.id,
            tier=tier,
            total_points=0,
            lifetime_points=0,
            current_streak=0,
            longest_streak=0,
            status=CustomerStatus.ACTIVE,
            joined_date=datetime.now(),
            last_activity=datetime.now()
        )

        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)

        logger.info(f"Customer created: {name} ({email})")
        return customer

    def update_customer(
        self,
        customer_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        tier: Optional[CustomerTier] = None,
        status: Optional[CustomerStatus] = None,
        notes: Optional[str] = None
    ) -> Customer:
        """
        Update customer information.

        Args:
            customer_id: Customer ID
            name: Updated name
            email: Updated email
            phone: Updated phone
            tier: Updated tier
            status: Updated status
            notes: Updated notes

        Returns:
            Updated customer object
        """
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found")

        # Update user information
        if name:
            customer.user.name = name
        if email:
            # Check if email is already taken by another user
            existing_user = self.db.query(User).filter(
                and_(User.email == email, User.id != customer.user_id)
            ).first()
            if existing_user:
                raise ValueError("Email already taken by another user")
            customer.user.email = email
        if phone:
            # Check if phone is already taken by another user
            existing_user = self.db.query(User).filter(
                and_(User.phone == phone, User.id != customer.user_id)
            ).first()
            if existing_user:
                raise ValueError("Phone number already taken by another user")
            customer.user.phone = phone

        # Update customer information
        if tier and tier != customer.tier:
            previous_tier = customer.tier
            customer.tier = tier

            # Create tier history
            history = CustomerTierHistory(
                customer_id=customer_id,
                previous_tier=previous_tier,
                new_tier=tier,
                points_at_upgrade=customer.total_points,
                reason="manual_update",
                changed_by=1  # TODO: Get from authenticated user
            )
            self.db.add(history)

        if status:
            customer.status = status

        customer.last_activity = datetime.now()
        self.db.commit()
        self.db.refresh(customer)

        logger.info(f"Customer {customer_id} updated")
        return customer

    def delete_customer(self, customer_id: int) -> bool:
        """
        Delete a customer (soft delete).

        Args:
            customer_id: Customer ID to delete

        Returns:
            True if deleted successfully
        """
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found")

        # Soft delete - mark as inactive
        customer.status = CustomerStatus.INACTIVE
        customer.user.status = UserStatus.INACTIVE

        self.db.commit()

        logger.info(f"Customer {customer_id} marked as inactive")
        return True

    def manage_customer_kids(
        self,
        customer_id: int,
        kids_data: List[Dict]
    ) -> List[CustomerKid]:
        """
        Manage customer's kids information.

        Args:
            customer_id: Customer ID
            kids_data: List of kid information dictionaries

        Returns:
            List of updated/created kids
        """
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found")

        existing_kids = self.db.query(CustomerKid).filter(
            CustomerKid.customer_id == customer_id
        ).all()

        # Create lookup for existing kids
        existing_kids_by_id = {kid.id: kid for kid in existing_kids}
        updated_kids = []

        for kid_data in kids_data:
            if 'id' in kid_data and kid_data['id']:
                # Update existing kid
                kid = existing_kids_by_id.get(kid_data['id'])
                if kid:
                    kid.name = kid_data['name']
                    kid.date_of_birth = kid_data['date_of_birth']
                    kid.gender = kid_data.get('gender')
                    kid.notes = kid_data.get('notes')
                    kid.is_active = kid_data.get('is_active', True)
                    updated_kids.append(kid)
            else:
                # Create new kid
                new_kid = CustomerKid(
                    customer_id=customer_id,
                    name=kid_data['name'],
                    date_of_birth=kid_data['date_of_birth'],
                    gender=kid_data.get('gender'),
                    notes=kid_data.get('notes'),
                    is_active=kid_data.get('is_active', True)
                )
                self.db.add(new_kid)
                updated_kids.append(new_kid)

        self.db.commit()

        logger.info(f"Updated kids information for customer {customer_id}")
        return updated_kids

    def get_customer_segmentation(self, segment_criteria: Dict) -> Dict:
        """
        Get customer segmentation based on criteria.

        Args:
            segment_criteria: Dictionary with segmentation criteria

        Returns:
            Dictionary with customer segments
        """
        query = self.db.query(Customer)

        segments = {
            "high_value": [],
            "active": [],
            "inactive": [],
            "new_customers": [],
            "birthday_month": []
        }

        # Get all customers
        customers = query.all()

        for customer in customers:
            # High value customers (Gold/Platinum tier with high points)
            if customer.tier in [CustomerTier.GOLD, CustomerTier.PLATINUM] and customer.total_points > 500:
                segments["high_value"].append(customer.id)

            # Active customers (activity within last 30 days)
            days_since_active = (datetime.now() - customer.last_activity).days
            if days_since_active <= 30:
                segments["active"].append(customer.id)
            elif days_since_active > 90:
                segments["inactive"].append(customer.id)

            # New customers (joined within last 30 days)
            days_since_joined = (datetime.now() - customer.joined_date).days
            if days_since_joined <= 30:
                segments["new_customers"].append(customer.id)

        return {
            "segments": {
                name: {
                    "count": len(customer_ids),
                    "customer_ids": customer_ids
                }
                for name, customer_ids in segments.items()
            },
            "total_customers": len(customers)
        }

    def get_customer_activity_timeline(self, customer_id: int, limit: int = 20) -> List[Dict]:
        """
        Get customer activity timeline including transactions, redemptions, tier changes.

        Args:
            customer_id: Customer ID
            limit: Maximum number of activities to return

        Returns:
            List of activity dictionaries
        """
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found")

        activities = []

        # Get transactions
        transactions = self.db.query(LoyaltyTransaction).filter(
            LoyaltyTransaction.customer_id == customer_id
        ).order_by(LoyaltyTransaction.created_at.desc()).limit(limit).all()

        for transaction in transactions:
            activities.append({
                "type": "transaction",
                "id": transaction.id,
                "description": f"{transaction.transaction_type.value.title()} {abs(transaction.points)} points ({transaction.source.value})",
                "details": transaction.description,
                "timestamp": transaction.created_at.isoformat(),
                "points_change": transaction.points
            })

        # Get redemptions
        redemptions = self.db.query(RewardRedemption).filter(
            RewardRedemption.customer_id == customer_id
        ).order_by(RewardRedemption.created_at.desc()).limit(limit // 2).all()

        for redemption in redemptions:
            activities.append({
                "type": "redemption",
                "id": redemption.id,
                "description": f"Redeemed {redemption.reward.name}",
                "details": f"{redemption.quantity}x {redemption.reward.category}",
                "timestamp": redemption.created_at.isoformat(),
                "points_change": -redemption.reward.points_required * redemption.quantity
            })

        # Get tier changes
        tier_changes = self.db.query(CustomerTierHistory).filter(
            CustomerTierHistory.customer_id == customer_id
        ).order_by(CustomerTierHistory.created_at.desc()).limit(limit // 4).all()

        for change in tier_changes:
            activities.append({
                "type": "tier_change",
                "id": change.id,
                "description": f"Tier upgraded to {change.new_tier.value}",
                "details": f"From {change.previous_tier.value if change.previous_tier else 'new'} - Reason: {change.reason}",
                "timestamp": change.created_at.isoformat(),
                "points_change": 0
            })

        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:limit]