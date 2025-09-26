"""
Affiliate Management Business Logic Service.

Handles affiliate registration, commission calculations, referral tracking, and payouts.
"""

from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import logging
import random
import string
import secrets

from ..models import (
    User, UserRole, UserStatus,
    Affiliate, AffiliateStatus,
    CustomerReferral,
    AffiliateCommission, CommissionStatus,
    Customer, CustomerStatus,
    LoyaltyTransaction, TransactionSource
)
from ..core.database import SessionLocal

logger = logging.getLogger(__name__)


class AffiliateService:
    """Service class for affiliate system operations."""

    def __init__(self, db: Session):
        self.db = db

    def generate_affiliate_code(self, length: int = 8) -> str:
        """
        Generate a unique affiliate code.

        Args:
            length: Length of the affiliate code

        Returns:
            Unique affiliate code
        """
        while True:
            # Create code with letters and numbers
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))

            # Check if code already exists
            existing = self.db.query(Affiliate).filter(
                Affiliate.affiliate_code == code
            ).first()

            if not existing:
                return code

    def register_affiliate(
        self,
        user_id: int,
        website_url: Optional[str] = None,
        marketing_channels: Optional[List[str]] = None,
        payment_method: Optional[str] = None,
        payment_details: Optional[Dict] = None,
        notes: Optional[str] = None
    ) -> Affiliate:
        """
        Register a new affiliate.

        Args:
            user_id: User ID to register as affiliate
            website_url: Affiliate's website URL
            marketing_channels: Marketing channels they use
            payment_method: Preferred payment method
            payment_details: Payment details (encrypted)
            notes: Additional notes

        Returns:
            Created affiliate object
        """
        # Check if user exists and is not already an affiliate
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        if user.role != UserRole.CUSTOMER:
            raise ValueError("Only customers can become affiliates")

        # Check if user already has an affiliate account
        existing_affiliate = self.db.query(Affiliate).filter(Affiliate.user_id == user_id).first()
        if existing_affiliate:
            raise ValueError("User is already registered as an affiliate")

        # Generate unique affiliate code
        affiliate_code = self.generate_affiliate_code()

        # Create affiliate
        affiliate = Affiliate(
            user_id=user_id,
            affiliate_code=affiliate_code,
            referral_link=f"https://loyaltyapp.com/ref/{affiliate_code}",
            status=AffiliateStatus.PENDING,
            commission_rate=5.0,  # Default 5% commission rate
            total_earnings=0.00,
            total_paid=0.00,
            unpaid_balance=0.00,
            payment_method=payment_method,
            payment_details=str(payment_details) if payment_details else None,
            website_url=website_url,
            marketing_channels=str(marketing_channels) if marketing_channels else None,
            notes=notes,
            joined_date=datetime.utcnow()
        )

        self.db.add(affiliate)
        self.db.commit()
        self.db.refresh(affiliate)

        logger.info(f"Affiliate registered: {user.email} with code {affiliate_code}")
        return affiliate

    def approve_affiliate(self, affiliate_id: int, approved_by: int) -> Affiliate:
        """
        Approve an affiliate application.

        Args:
            affiliate_id: Affiliate ID to approve
            approved_by: User ID who approved the application

        Returns:
            Updated affiliate object
        """
        affiliate = self.db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
        if not affiliate:
            raise ValueError(f"Affiliate with ID {affiliate_id} not found")

        if affiliate.status != AffiliateStatus.PENDING:
            raise ValueError("Affiliate is not in pending status")

        affiliate.status = AffiliateStatus.APPROVED
        affiliate.approved_at = datetime.utcnow()
        affiliate.approved_by = approved_by

        self.db.commit()
        self.db.refresh(affiliate)

        logger.info(f"Affiliate {affiliate_id} approved by user {approved_by}")
        return affiliate

    def update_affiliate_profile(
        self,
        affiliate_id: int,
        website_url: Optional[str] = None,
        marketing_channels: Optional[List[str]] = None,
        payment_method: Optional[str] = None,
        payment_details: Optional[Dict] = None,
        notes: Optional[str] = None
    ) -> Affiliate:
        """
        Update affiliate profile information.

        Args:
            affiliate_id: Affiliate ID to update
            website_url: Updated website URL
            marketing_channels: Updated marketing channels
            payment_method: Updated payment method
            payment_details: Updated payment details
            notes: Updated notes

        Returns:
            Updated affiliate object
        """
        affiliate = self.db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
        if not affiliate:
            raise ValueError(f"Affiliate with ID {affiliate_id} not found")

        if website_url is not None:
            affiliate.website_url = website_url

        if marketing_channels is not None:
            affiliate.marketing_channels = str(marketing_channels)

        if payment_method is not None:
            affiliate.payment_method = payment_method

        if payment_details is not None:
            affiliate.payment_details = str(payment_details)

        if notes is not None:
            affiliate.notes = notes

        affiliate.last_activity = datetime.utcnow()
        self.db.commit()
        self.db.refresh(affiliate)

        logger.info(f"Affiliate {affiliate_id} profile updated")
        return affiliate

    def track_referral(
        self,
        affiliate_code: str,
        customer_id: int,
        referral_source: str = "direct",
        metadata: Optional[Dict] = None
    ) -> Optional[CustomerReferral]:
        """
        Track a customer referral.

        Args:
            affiliate_code: Affiliate code used for referral
            customer_id: Customer who was referred
            referral_source: Source of the referral
            metadata: Additional referral metadata

        Returns:
            Created referral record, or None if affiliate not found
        """
        # Find affiliate by code
        affiliate = self.db.query(Affiliate).filter(Affiliate.affiliate_code == affiliate_code).first()
        if not affiliate:
            logger.warning(f"Affiliate code {affiliate_code} not found")
            return None

        if affiliate.status not in [AffiliateStatus.APPROVED, AffiliateStatus.ACTIVE]:
            logger.warning(f"Affiliate {affiliate_code} is not approved/active")
            return None

        # Check if customer already has a referral from this affiliate
        existing_referral = self.db.query(CustomerReferral).filter(
            and_(
                CustomerReferral.affiliate_id == affiliate.id,
                CustomerReferral.customer_id == customer_id
            )
        ).first()

        if existing_referral:
            logger.info(f"Referral already exists for customer {customer_id} from affiliate {affiliate_code}")
            return existing_referral

        # Create referral record
        referral = CustomerReferral(
            affiliate_id=affiliate.id,
            customer_id=customer_id,
            referral_code_used=affiliate_code,
            referral_source=referral_source,
            conversion_value=0.00,  # Will be updated when purchase is made
            commission_amount=0.00,  # Will be calculated when purchase is made
            status="converted",
            metadata=str(metadata) if metadata else None,
            created_at=datetime.utcnow()
        )

        self.db.add(referral)
        self.db.commit()
        self.db.refresh(referral)

        # Update affiliate last activity
        affiliate.last_activity = datetime.utcnow()
        self.db.commit()

        logger.info(f"Referral tracked: Customer {customer_id} referred by {affiliate_code}")
        return referral

    def calculate_commission(
        self,
        referral_id: int,
        purchase_amount: float,
        commission_rate: Optional[float] = None
    ) -> AffiliateCommission:
        """
        Calculate and create commission for a referral.

        Args:
            referral_id: Referral ID
            purchase_amount: Amount of the purchase
            commission_rate: Commission rate (overrides affiliate's default)

        Returns:
            Created commission record
        """
        referral = self.db.query(CustomerReferral).filter(CustomerReferral.id == referral_id).first()
        if not referral:
            raise ValueError(f"Referral with ID {referral_id} not found")

        affiliate = self.db.query(Affiliate).filter(Affiliate.id == referral.affiliate_id).first()
        if not affiliate:
            raise ValueError("Affiliate not found")

        # Use provided rate or affiliate's default rate
        rate = commission_rate if commission_rate is not None else affiliate.commission_rate
        commission_amount = (purchase_amount * rate) / 100

        # Update referral with conversion value and commission
        referral.conversion_value = purchase_amount
        referral.commission_amount = commission_amount

        # Create commission record
        commission = AffiliateCommission(
            affiliate_id=affiliate.id,
            user_id=affiliate.user_id,
            referral_id=referral_id,
            commission_amount=commission_amount,
            commission_rate=rate,
            status=CommissionStatus.PENDING,
            description=f"Commission for referral {referral_id} - ${purchase_amount} purchase",
            created_at=datetime.utcnow()
        )

        self.db.add(commission)

        # Update affiliate earnings
        affiliate.total_earnings += commission_amount
        affiliate.unpaid_balance += commission_amount
        affiliate.last_activity = datetime.utcnow()

        self.db.commit()
        self.db.refresh(commission)

        logger.info(f"Commission calculated: ${commission_amount} for affiliate {affiliate.affiliate_code}")
        return commission

    def approve_commission(self, commission_id: int, approved_by: int) -> AffiliateCommission:
        """
        Approve a commission for payout.

        Args:
            commission_id: Commission ID to approve
            approved_by: User ID who approved the commission

        Returns:
            Updated commission record
        """
        commission = self.db.query(AffiliateCommission).filter(AffiliateCommission.id == commission_id).first()
        if not commission:
            raise ValueError(f"Commission with ID {commission_id} not found")

        if commission.status != CommissionStatus.PENDING:
            raise ValueError("Commission is not in pending status")

        commission.status = CommissionStatus.APPROVED
        commission.approved_by = approved_by
        commission.approved_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(commission)

        logger.info(f"Commission {commission_id} approved by user {approved_by}")
        return commission

    def get_affiliate_performance(self, affiliate_id: int, days: int = 30) -> Dict:
        """
        Get affiliate performance metrics.

        Args:
            affiliate_id: Affiliate ID
            days: Number of days to look back

        Returns:
            Dictionary with performance metrics
        """
        affiliate = self.db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
        if not affiliate:
            raise ValueError(f"Affiliate with ID {affiliate_id} not found")

        start_date = datetime.utcnow() - timedelta(days=days)

        # Get referrals in the period
        referrals = self.db.query(CustomerReferral).filter(
            and_(
                CustomerReferral.affiliate_id == affiliate_id,
                CustomerReferral.created_at >= start_date
            )
        ).all()

        # Get commissions in the period
        commissions = self.db.query(AffiliateCommission).filter(
            and_(
                AffiliateCommission.affiliate_id == affiliate_id,
                AffiliateCommission.created_at >= start_date
            )
        ).all()

        # Calculate metrics
        total_referrals = len(referrals)
        total_conversion_value = sum(r.conversion_value for r in referrals)
        total_commission_earned = sum(c.commission_amount for c in commissions if c.status == CommissionStatus.APPROVED)
        total_commission_pending = sum(c.commission_amount for c in commissions if c.status == CommissionStatus.PENDING)
        total_commission_paid = sum(c.commission_amount for c in commissions if c.status == CommissionStatus.PAID)

        # Conversion rate (referrals that resulted in purchases)
        converted_referrals = len([r for r in referrals if r.conversion_value > 0])
        conversion_rate = (converted_referrals / total_referrals * 100) if total_referrals > 0 else 0

        return {
            "affiliate_id": affiliate_id,
            "affiliate_code": affiliate.affiliate_code,
            "period_days": days,
            "total_referrals": total_referrals,
            "converted_referrals": converted_referrals,
            "conversion_rate": round(conversion_rate, 2),
            "total_conversion_value": total_conversion_value,
            "total_commission_earned": total_commission_earned,
            "total_commission_pending": total_commission_pending,
            "total_commission_paid": total_commission_paid,
            "average_commission_per_referral": total_commission_earned / converted_referrals if converted_referrals > 0 else 0
        }

    def get_affiliate_referrals(
        self,
        affiliate_id: int,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None
    ) -> Dict:
        """
        Get referrals for an affiliate.

        Args:
            affiliate_id: Affiliate ID
            limit: Maximum number of referrals to return
            offset: Number of referrals to skip
            status: Filter by referral status

        Returns:
            Dictionary with referrals and pagination info
        """
        query = self.db.query(CustomerReferral).filter(
            CustomerReferral.affiliate_id == affiliate_id
        )

        if status:
            query = query.filter(CustomerReferral.status == status)

        total = query.count()
        referrals = query.order_by(desc(CustomerReferral.created_at)).offset(offset).limit(limit).all()

        return {
            "referrals": [
                {
                    "id": r.id,
                    "customer_id": r.customer_id,
                    "referral_code_used": r.referral_code_used,
                    "referral_source": r.referral_source,
                    "conversion_value": r.conversion_value,
                    "commission_amount": r.commission_amount,
                    "status": r.status,
                    "created_at": r.created_at.isoformat(),
                    "metadata": r.metadata
                }
                for r in referrals
            ],
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        }

    def get_affiliate_commissions(
        self,
        affiliate_id: int,
        limit: int = 50,
        offset: int = 0,
        status: Optional[CommissionStatus] = None
    ) -> Dict:
        """
        Get commissions for an affiliate.

        Args:
            affiliate_id: Affiliate ID
            limit: Maximum number of commissions to return
            offset: Number of commissions to skip
            status: Filter by commission status

        Returns:
            Dictionary with commissions and pagination info
        """
        query = self.db.query(AffiliateCommission).filter(
            AffiliateCommission.affiliate_id == affiliate_id
        )

        if status:
            query = query.filter(AffiliateCommission.status == status)

        total = query.count()
        commissions = query.order_by(desc(AffiliateCommission.created_at)).offset(offset).limit(limit).all()

        return {
            "commissions": [
                {
                    "id": c.id,
                    "commission_amount": c.commission_amount,
                    "commission_rate": c.commission_rate,
                    "status": c.status.value,
                    "description": c.description,
                    "approved_at": c.approved_at.isoformat() if c.approved_at else None,
                    "paid_at": c.paid_at.isoformat() if c.paid_at else None,
                    "payment_reference": c.payment_reference,
                    "created_at": c.created_at.isoformat()
                }
                for c in commissions
            ],
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        }

    def get_affiliate_dashboard(self, affiliate_id: int) -> Dict:
        """
        Get comprehensive dashboard data for an affiliate.

        Args:
            affiliate_id: Affiliate ID

        Returns:
            Dictionary with dashboard data
        """
        affiliate = self.db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
        if not affiliate:
            raise ValueError(f"Affiliate with ID {affiliate_id} not found")

        # Get performance metrics
        performance_30d = self.get_affiliate_performance(affiliate_id, days=30)
        performance_7d = self.get_affiliate_performance(affiliate_id, days=7)

        # Get recent referrals and commissions
        recent_referrals = self.get_affiliate_referrals(affiliate_id, limit=5)
        recent_commissions = self.get_affiliate_commissions(affiliate_id, limit=5)

        # Calculate tier based on performance
        tier = "Bronze"
        if performance_30d["total_commission_earned"] >= 1000:
            tier = "Platinum"
        elif performance_30d["total_commission_earned"] >= 500:
            tier = "Gold"
        elif performance_30d["total_commission_earned"] >= 100:
            tier = "Silver"

        return {
            "affiliate": {
                "id": affiliate.id,
                "affiliate_code": affiliate.affiliate_code,
                "referral_link": affiliate.referral_link,
                "status": affiliate.status.value,
                "commission_rate": affiliate.commission_rate,
                "total_earnings": affiliate.total_earnings,
                "total_paid": affiliate.total_paid,
                "unpaid_balance": affiliate.unpaid_balance,
                "joined_date": affiliate.joined_date.isoformat(),
                "last_activity": affiliate.last_activity.isoformat()
            },
            "performance": {
                "this_month": performance_30d,
                "this_week": performance_7d,
                "current_tier": tier
            },
            "recent_referrals": recent_referrals["referrals"],
            "recent_commissions": recent_commissions["commissions"],
            "summary_stats": {
                "total_referrals": performance_30d["total_referrals"],
                "conversion_rate": performance_30d["conversion_rate"],
                "avg_commission": performance_30d["average_commission_per_referral"]
            }
        }