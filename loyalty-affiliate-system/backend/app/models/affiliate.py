from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Boolean, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class AffiliateStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    ACTIVE = "active"
    INACTIVE = "inactive"


class CommissionStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"


class Affiliate(Base):
    __tablename__ = "affiliates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    affiliate_code = Column(String(50), unique=True, index=True, nullable=False)
    referral_link = Column(String(500), nullable=False)
    status = Column(Enum(AffiliateStatus), default=AffiliateStatus.PENDING, nullable=False)
    commission_rate = Column(DECIMAL(5, 2), default=5.00, nullable=False)  # Percentage
    total_earnings = Column(DECIMAL(15, 2), default=0.00, nullable=False)
    total_paid = Column(DECIMAL(15, 2), default=0.00, nullable=False)
    unpaid_balance = Column(DECIMAL(15, 2), default=0.00, nullable=False)
    payment_method = Column(String(50))  # bank_transfer, paypal, etc.
    payment_details = Column(Text)  # JSON data with payment information
    website_url = Column(String(500))
    marketing_channels = Column(Text)  # JSON array of channels used
    notes = Column(Text)
    approved_at = Column(DateTime(timezone=True))
    approved_by = Column(Integer, ForeignKey("users.id"))
    joined_date = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="affiliates")
    referrals = relationship("CustomerReferral", back_populates="affiliate", cascade="all, delete-orphan")
    commissions = relationship("AffiliateCommission", back_populates="affiliate", cascade="all, delete-orphan")


class CustomerReferral(Base):
    __tablename__ = "customer_referrals"

    id = Column(Integer, primary_key=True, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    referral_code_used = Column(String(50), nullable=False)
    referral_source = Column(String(100))  # website, social_media, email, etc.
    conversion_value = Column(DECIMAL(15, 2), default=0.00)  # Value of the conversion
    commission_amount = Column(DECIMAL(15, 2), default=0.00)
    status = Column(String(50), default="converted")  # converted, pending, cancelled
    metadata = Column(Text)  # Additional referral data
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes for performance
    __table_args__ = (
        {'mysql_index': [('affiliate_id', 'customer_id')]},
        {'mysql_index': [('referral_code_used',)]}
    )

    # Relationships
    affiliate = relationship("Affiliate", back_populates="referrals")
    customer = relationship("Customer")


class AffiliateCommission(Base):
    __tablename__ = "affiliate_commissions"

    id = Column(Integer, primary_key=True, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    referral_id = Column(Integer, ForeignKey("customer_referrals.id"), nullable=True)
    commission_amount = Column(DECIMAL(15, 2), nullable=False)
    commission_rate = Column(DECIMAL(5, 2), nullable=False)
    status = Column(Enum(CommissionStatus), default=CommissionStatus.PENDING, nullable=False)
    description = Column(String(500), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    paid_at = Column(DateTime(timezone=True))
    payment_reference = Column(String(100))  # Transaction ID or check number
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    affiliate = relationship("Affiliate", back_populates="commissions")
    user = relationship("User", back_populates="affiliate_commissions")
    referral = relationship("CustomerReferral")


class PayoutRequest(Base):
    __tablename__ = "payout_requests"

    id = Column(Integer, primary_key=True, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id"), nullable=False)
    amount = Column(DECIMAL(15, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    payment_details = Column(Text, nullable=False)
    status = Column(String(50), default="pending")  # pending, processing, completed, rejected
    transaction_id = Column(String(100))  # External payment system ID
    processed_by = Column(Integer, ForeignKey("users.id"))
    processed_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    affiliate = relationship("Affiliate")