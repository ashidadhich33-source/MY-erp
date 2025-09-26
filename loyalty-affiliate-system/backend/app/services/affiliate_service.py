"""
Affiliate Service

Handles affiliate management, referral tracking, commission calculation,
and affiliate program business logic.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import secrets
import string

from ..models import (
    Affiliate, CustomerReferral, AffiliateCommission,
    PayoutRequest, User, Customer, AffiliateStatus,
    CommissionStatus
)


class AffiliateService:
    """
    Service for handling affiliate operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_affiliate(self, user_id: int, commission_rate: float = 10.0,
                        website_url: Optional[str] = None, marketing_channels: Optional[str] = None,
                        notes: Optional[str] = None) -> Affiliate:
        """Create a new affiliate."""
        # Check if user is already an affiliate
        existing_affiliate = self.db.query(Affiliate).filter(Affiliate.user_id == user_id).first()
        if existing_affiliate:
            raise ValueError("User is already an affiliate")

        # Generate unique affiliate code and referral link
        affiliate_code = self._generate_unique_affiliate_code()
        referral_link = f"https://yourapp.com/ref/{affiliate_code}"

        affiliate = Affiliate(
            user_id=user_id,
            affiliate_code=affiliate_code,
            referral_link=referral_link,
            status=AffiliateStatus.PENDING,
            commission_rate=commission_rate,
            total_earnings=0,
            total_paid=0,
            unpaid_balance=0,
            payment_method=None,
            payment_details=None,
            website_url=website_url,
            marketing_channels=marketing_channels,
            notes=notes,
            joined_date=datetime.utcnow()
        )

        self.db.add(affiliate)
        self.db.commit()
        self.db.refresh(affiliate)

        return affiliate

    def approve_affiliate(self, affiliate_id: int, approved_by: int) -> Affiliate:
        """Approve an affiliate application."""
        affiliate = self.get_affiliate_by_id(affiliate_id)

        if not affiliate:
            raise ValueError("Affiliate not found")

        if affiliate.status != AffiliateStatus.PENDING:
            raise ValueError("Affiliate is not pending approval")

        affiliate.status = AffiliateStatus.ACTIVE
        affiliate.approved_at = datetime.utcnow()
        affiliate.approved_by = approved_by
        affiliate.last_activity = datetime.utcnow()

        self.db.commit()
        self.db.refresh(affiliate)

        return affiliate

    def reject_affiliate(self, affiliate_id: int, reason: str) -> Affiliate:
        """Reject an affiliate application."""
        affiliate = self.get_affiliate_by_id(affiliate_id)

        if not affiliate:
            raise ValueError("Affiliate not found")

        if affiliate.status != AffiliateStatus.PENDING:
            raise ValueError("Affiliate is not pending approval")

        affiliate.status = AffiliateStatus.REJECTED
        affiliate.notes = f"Rejection reason: {reason}"

        self.db.commit()
        self.db.refresh(affiliate)

        return affiliate

    def get_affiliate_by_id(self, affiliate_id: int) -> Optional[Affiliate]:
        """Get affiliate by ID."""
        return self.db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()

    def get_affiliate_by_user_id(self, user_id: int) -> Optional[Affiliate]:
        """Get affiliate by user ID."""
        return self.db.query(Affiliate).filter(Affiliate.user_id == user_id).first()

    def get_affiliate_by_code(self, affiliate_code: str) -> Optional[Affiliate]:
        """Get affiliate by affiliate code."""
        return self.db.query(Affiliate).filter(Affiliate.affiliate_code == affiliate_code).first()

    def update_affiliate_profile(self, affiliate_id: int, **kwargs) -> Affiliate:
        """Update affiliate profile information."""
        affiliate = self.get_affiliate_by_id(affiliate_id)

        if not affiliate:
            raise ValueError("Affiliate not found")

        for key, value in kwargs.items():
            if hasattr(affiliate, key):
                setattr(affiliate, key, value)

        affiliate.last_activity = datetime.utcnow()
        self.db.commit()
        self.db.refresh(affiliate)

        return affiliate

    def record_referral(self, affiliate_id: int, customer_name: str, customer_email: str,
                       customer_phone: str, referral_source: Optional[str] = None,
                       metadata: Optional[Dict] = None) -> CustomerReferral:
        """Record a new referral."""
        affiliate = self.get_affiliate_by_id(affiliate_id)

        if not affiliate:
            raise ValueError("Affiliate not found")

        if affiliate.status != AffiliateStatus.ACTIVE:
            raise ValueError("Affiliate is not active")

        # Check if referral already exists
        existing_referral = self.db.query(CustomerReferral).filter(
            and_(
                CustomerReferral.affiliate_id == affiliate_id,
                CustomerReferral.customer_email == customer_email,
                CustomerReferral.status == "pending"
            )
        ).first()

        if existing_referral:
            raise ValueError("Referral already exists for this customer")

        referral = CustomerReferral(
            affiliate_id=affiliate_id,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            referral_code_used=affiliate.affiliate_code,
            referral_source=referral_source,
            conversion_value=0,  # Will be updated when customer converts
            commission_amount=0,  # Will be calculated when commission is created
            status="pending",
            metadata=metadata
        )

        self.db.add(referral)
        affiliate.last_activity = datetime.utcnow()
        self.db.commit()
        self.db.refresh(referral)

        return referral

    def convert_referral(self, referral_id: int, customer_id: int, conversion_value: float) -> CustomerReferral:
        """Convert a referral to a successful customer signup."""
        referral = self.db.query(CustomerReferral).filter(CustomerReferral.id == referral_id).first()

        if not referral:
            raise ValueError("Referral not found")

        if referral.status != "pending":
            raise ValueError("Referral is not pending conversion")

        # Calculate commission
        affiliate = self.get_affiliate_by_id(referral.affiliate_id)
        commission_amount = (conversion_value * affiliate.commission_rate) / 100

        referral.status = "converted"
        referral.conversion_value = conversion_value
        referral.commission_amount = commission_amount

        # Update affiliate earnings
        affiliate.total_earnings += commission_amount
        affiliate.unpaid_balance += commission_amount
        affiliate.last_activity = datetime.utcnow()

        # Create commission record
        commission = AffiliateCommission(
            affiliate_id=affiliate.id,
            user_id=affiliate.user_id,
            referral_id=referral.id,
            commission_amount=commission_amount,
            commission_rate=affiliate.commission_rate,
            status=CommissionStatus.PENDING,
            description=f"Commission for referral of {referral.customer_name}"
        )

        self.db.add(commission)
        self.db.commit()
        self.db.refresh(referral)

        return referral

    def approve_commission(self, commission_id: int, approved_by: int) -> AffiliateCommission:
        """Approve a commission for payment."""
        commission = self.db.query(AffiliateCommission).filter(
            AffiliateCommission.id == commission_id
        ).first()

        if not commission:
            raise ValueError("Commission not found")

        if commission.status != CommissionStatus.PENDING:
            raise ValueError("Commission is not pending approval")

        commission.status = CommissionStatus.APPROVED
        commission.approved_by = approved_by
        commission.approved_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(commission)

        return commission

    def create_payout_request(self, affiliate_id: int, amount: float,
                             payment_method: str, payment_details: str) -> PayoutRequest:
        """Create a payout request for an affiliate."""
        affiliate = self.get_affiliate_by_id(affiliate_id)

        if not affiliate:
            raise ValueError("Affiliate not found")

        if affiliate.unpaid_balance < amount:
            raise ValueError("Insufficient unpaid balance")

        if amount <= 0:
            raise ValueError("Amount must be positive")

        payout = PayoutRequest(
            affiliate_id=affiliate_id,
            amount=amount,
            payment_method=payment_method,
            payment_details=payment_details,
            status="pending"
        )

        self.db.add(payout)
        self.db.commit()
        self.db.refresh(payout)

        return payout

    def process_payout(self, payout_id: int, processed_by: int,
                      transaction_id: Optional[str] = None) -> PayoutRequest:
        """Process a payout request."""
        payout = self.db.query(PayoutRequest).filter(PayoutRequest.id == payout_id).first()

        if not payout:
            raise ValueError("Payout request not found")

        if payout.status != "pending":
            raise ValueError("Payout is not pending")

        payout.status = "completed"
        payout.processed_by = processed_by
        payout.processed_at = datetime.utcnow()
        payout.transaction_id = transaction_id

        # Update affiliate balance
        affiliate = self.get_affiliate_by_id(payout.affiliate_id)
        affiliate.total_paid += payout.amount
        affiliate.unpaid_balance -= payout.amount

        self.db.commit()
        self.db.refresh(payout)

        return payout

    def get_affiliate_analytics(self, affiliate_id: int) -> Dict[str, Any]:
        """Get analytics for a specific affiliate."""
        affiliate = self.get_affiliate_by_id(affiliate_id)

        if not affiliate:
            raise ValueError("Affiliate not found")

        # Referral statistics
        total_referrals = self.db.query(func.count(CustomerReferral.id)).filter(
            CustomerReferral.affiliate_id == affiliate_id
        ).scalar()

        successful_referrals = self.db.query(func.count(CustomerReferral.id)).filter(
            and_(
                CustomerReferral.affiliate_id == affiliate_id,
                CustomerReferral.status == "converted"
            )
        ).scalar()

        # Commission statistics
        total_commissions = self.db.query(func.sum(AffiliateCommission.commission_amount)).filter(
            AffiliateCommission.affiliate_id == affiliate_id,
            AffiliateCommission.status == CommissionStatus.APPROVED
        ).scalar() or 0

        paid_commissions = self.db.query(func.sum(AffiliateCommission.commission_amount)).filter(
            AffiliateCommission.affiliate_id == affiliate_id,
            AffiliateCommission.status == CommissionStatus.PAID
        ).scalar() or 0

        # Conversion rate
        conversion_rate = (successful_referrals / max(total_referrals, 1)) * 100

        return {
            "affiliate_id": affiliate_id,
            "referrals": {
                "total": total_referrals,
                "successful": successful_referrals,
                "conversion_rate": round(conversion_rate, 2)
            },
            "commissions": {
                "total_earned": float(total_commissions),
                "total_paid": float(paid_commissions),
                "pending": float(total_commissions - paid_commissions),
                "unpaid_balance": float(affiliate.unpaid_balance)
            },
            "performance": {
                "average_commission": float(total_commissions) / max(successful_referrals, 1),
                "rank": self._calculate_affiliate_rank(affiliate_id)
            }
        }

    def get_affiliates_list(self, status: Optional[str] = None, limit: int = 50,
                           offset: int = 0) -> Dict[str, Any]:
        """Get paginated list of affiliates."""
        query = self.db.query(Affiliate, User).join(User)

        if status:
            query = query.filter(Affiliate.status == status)

        total = query.count()
        affiliates = query.offset(offset).limit(limit).all()

        return {
            "affiliates": [
                {
                    "id": affiliate.id,
                    "user_id": affiliate.user_id,
                    "name": user.name,
                    "email": user.email,
                    "affiliate_code": affiliate.affiliate_code,
                    "status": affiliate.status.value,
                    "total_earnings": float(affiliate.total_earnings),
                    "unpaid_balance": float(affiliate.unpaid_balance),
                    "joined_date": affiliate.joined_date.isoformat(),
                    "last_activity": affiliate.last_activity.isoformat()
                }
                for affiliate, user in affiliates
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }

    def _generate_unique_affiliate_code(self) -> str:
        """Generate a unique affiliate code."""
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

            existing = self.db.query(Affiliate).filter(Affiliate.affiliate_code == code).first()
            if not existing:
                return code

    def _calculate_affiliate_rank(self, affiliate_id: int) -> int:
        """Calculate affiliate rank based on earnings."""
        affiliate = self.get_affiliate_by_id(affiliate_id)
        if not affiliate:
            return 0

        # Get all affiliates ranked by total earnings
        ranked_affiliates = self.db.query(Affiliate.id).filter(
            Affiliate.status == AffiliateStatus.ACTIVE
        ).order_by(Affiliate.total_earnings.desc()).all()

        for i, (aff_id,) in enumerate(ranked_affiliates, 1):
            if aff_id == affiliate_id:
                return i

        return len(ranked_affiliates) + 1

    def get_top_affiliates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing affiliates."""
        affiliates = self.db.query(Affiliate, User).join(User).filter(
            Affiliate.status == AffiliateStatus.ACTIVE
        ).order_by(Affiliate.total_earnings.desc()).limit(limit).all()

        return [
            {
                "id": affiliate.id,
                "name": user.name,
                "email": user.email,
                "affiliate_code": affiliate.affiliate_code,
                "total_earnings": float(affiliate.total_earnings),
                "referral_count": self.db.query(func.count(CustomerReferral.id)).filter(
                    CustomerReferral.affiliate_id == affiliate.id
                ).scalar(),
                "rank": i + 1
            }
            for i, (affiliate, user) in enumerate(affiliates)
        ]