from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Boolean, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class TransactionType(str, enum.Enum):
    EARNED = "earned"
    REDEEMED = "redeemed"
    EXPIRED = "expired"
    ADJUSTMENT = "adjustment"
    TRANSFER = "transfer"


class TransactionSource(str, enum.Enum):
    PURCHASE = "purchase"
    REFERRAL = "referral"
    BIRTHDAY = "birthday"
    PROMOTION = "promotion"
    MANUAL = "manual"
    SYSTEM = "system"


class RewardStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"


class RedemptionStatus(str, enum.Enum):
    COMPLETED = "completed"
    PENDING = "pending"
    CANCELLED = "cancelled"


class LoyaltyTransaction(Base):
    __tablename__ = "loyalty_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    erp_sale_id = Column(String(100), nullable=True)  # Logic ERP OrderID
    points = Column(Integer, nullable=False)  # Can be negative for redemptions
    transaction_type = Column(Enum(TransactionType), nullable=False)
    source = Column(Enum(TransactionSource), nullable=False)
    description = Column(String(500), nullable=False)
    reference_id = Column(String(100))  # Reference to external system (order_id, etc.)
    metadata = Column(Text)  # JSON data for additional information
    expires_at = Column(DateTime(timezone=True))  # When points expire
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes for performance
    __table_args__ = (
        {'index': True, 'unique': False, 'mysql_length': None},
    )

    # Relationships
    user = relationship("User", back_populates="loyalty_transactions")
    customer = relationship("Customer", back_populates="loyalty_transactions")
    reward_redemptions = relationship("RewardRedemption", back_populates="transaction", cascade="all, delete-orphan")


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    points_required = Column(Integer, nullable=False)
    category = Column(String(100))  # "food", "beverage", "service", "product"
    image_url = Column(String(500))
    status = Column(Enum(RewardStatus), default=RewardStatus.ACTIVE, nullable=False)
    stock_quantity = Column(Integer, default=-1)  # -1 means unlimited
    max_per_customer = Column(Integer, default=1)  # Max redemptions per customer
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True))
    terms_conditions = Column(Text)
    is_featured = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    redemptions = relationship("RewardRedemption", back_populates="reward", cascade="all, delete-orphan")


class RewardRedemption(Base):
    __tablename__ = "reward_redemptions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("loyalty_transactions.id"), unique=True, nullable=False)
    reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    redemption_code = Column(String(100), unique=True)  # Unique code for redemption
    status = Column(Enum(RedemptionStatus), default=RedemptionStatus.COMPLETED, nullable=False)
    fulfilled_at = Column(DateTime(timezone=True))
    fulfilled_by = Column(Integer, ForeignKey("users.id"))  # Admin who fulfilled
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    transaction = relationship("LoyaltyTransaction", back_populates="reward_redemptions")
    reward = relationship("Reward", back_populates="redemptions")
    customer = relationship("Customer")


class TierBenefit(Base):
    __tablename__ = "tier_benefits"

    id = Column(Integer, primary_key=True, index=True)
    tier = Column(Enum(CustomerTier), nullable=False)
    benefit_type = Column(String(100), nullable=False)  # "points_multiplier", "free_shipping", etc.
    benefit_value = Column(String(255), nullable=False)  # Value of the benefit
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes (database-agnostic)
    __table_args__ = ()