from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class CustomerTier(str, enum.Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class CustomerStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    erp_id = Column(String(100), nullable=True)  # Logic ERP CustomerID
    tier = Column(Enum(CustomerTier), default=CustomerTier.BRONZE, nullable=False)
    total_points = Column(Integer, default=0, nullable=False)
    lifetime_points = Column(Integer, default=0, nullable=False)
    current_streak = Column(Integer, default=0)  # Consecutive days of activity
    longest_streak = Column(Integer, default=0)
    status = Column(Enum(CustomerStatus), default=CustomerStatus.ACTIVE, nullable=False)
    joined_date = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    last_sync = Column(DateTime(timezone=True), nullable=True)  # Last sync with Logic ERP
    data_hash = Column(String(64), nullable=True)  # Hash for change detection
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="customers")
    kids = relationship("CustomerKid", back_populates="customer", cascade="all, delete-orphan")
    loyalty_transactions = relationship("LoyaltyTransaction", back_populates="customer", cascade="all, delete-orphan")
    whatsapp_messages = relationship("WhatsAppMessage", back_populates="customer", cascade="all, delete-orphan")
    birthday_promotions = relationship("BirthdayPromotion", back_populates="customer", cascade="all, delete-orphan")
    tier_history = relationship("CustomerTierHistory", back_populates="customer", cascade="all, delete-orphan")


class CustomerKid(Base):
    __tablename__ = "customer_kids"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime(timezone=True), nullable=False)
    gender = Column(String(10))  # male, female, other
    notes = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="kids")
    birthday_promotions = relationship("BirthdayPromotion", back_populates="kid", cascade="all, delete-orphan")


class CustomerTierHistory(Base):
    __tablename__ = "customer_tier_history"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    previous_tier = Column(Enum(CustomerTier), nullable=True)
    new_tier = Column(Enum(CustomerTier), nullable=False)
    points_at_upgrade = Column(Integer, nullable=False)
    reason = Column(String(255))  # "points_threshold", "manual_upgrade", etc.
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Admin who made the change
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="tier_history")