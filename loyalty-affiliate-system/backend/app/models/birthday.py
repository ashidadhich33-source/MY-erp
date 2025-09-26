from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class PromotionStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BirthdayPromotion(Base):
    __tablename__ = "birthday_promotions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    kid_id = Column(Integer, ForeignKey("customer_kids.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who the promotion is for
    promotion_type = Column(String(50), nullable=False)  # "customer_birthday", "kid_birthday"
    birthday_date = Column(DateTime(timezone=True), nullable=False)
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    sent_date = Column(DateTime(timezone=True))
    status = Column(Enum(PromotionStatus), default=PromotionStatus.SCHEDULED, nullable=False)
    promotion_code = Column(String(100), unique=True)  # Unique promotion code generated
    discount_amount = Column(String(50))  # "10%", "$5", "100 points", etc.
    message_content = Column(Text)
    template_id = Column(Integer, ForeignKey("notification_templates.id"), nullable=True)
    whatsapp_message_id = Column(Integer, ForeignKey("whatsapp_messages.id"), nullable=True)
    is_recurring = Column(Boolean, default=False, nullable=False)  # For annual birthdays
    metadata = Column(Text)  # JSON data for additional promotion info
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Ensure either customer_id or kid_id is set, but not both
    # Note: Check constraints are database-specific and should be handled at application level
    __table_args__ = ()

    # Relationships
    customer = relationship("Customer", back_populates="birthday_promotions")
    kid = relationship("CustomerKid", back_populates="birthday_promotions")
    user = relationship("User", back_populates="birthday_promotions")
    template = relationship("NotificationTemplate")
    message = relationship("WhatsAppMessage", back_populates="birthday_promotion")
    creator = relationship("User", foreign_keys=[created_by])


class BirthdaySchedule(Base):
    __tablename__ = "birthday_schedules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # "Customer Birthdays", "Kids Birthdays"
    description = Column(Text)
    promotion_type = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    advance_notice_days = Column(Integer, default=7, nullable=False)  # Days before birthday to send
    template_id = Column(Integer, ForeignKey("notification_templates.id"), nullable=False)
    discount_amount = Column(String(50), default="10%")  # Default discount for promotions
    max_promotions_per_day = Column(Integer, default=100)  # Rate limiting
    last_processed = Column(DateTime(timezone=True))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    template = relationship("NotificationTemplate")
    creator = relationship("User", foreign_keys=[created_by])