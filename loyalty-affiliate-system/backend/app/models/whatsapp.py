from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    TEMPLATE = "template"


class MessageDirection(str, enum.Enum):
    OUTBOUND = "outbound"
    INBOUND = "inbound"


class MessageStatus(str, enum.Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    PENDING = "pending"


class TemplateCategory(str, enum.Enum):
    BILL = "bill"
    BIRTHDAY = "birthday"
    PROMOTION = "promotion"
    WELCOME = "welcome"
    LOYALTY = "loyalty"
    AFFILIATE = "affiliate"


class WhatsAppMessage(Base):
    __tablename__ = "whatsapp_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    message_type = Column(Enum(MessageType), nullable=False)
    direction = Column(Enum(MessageDirection), nullable=False)
    content = Column(Text, nullable=False)
    media_url = Column(String(500))  # URL to media file if applicable
    template_id = Column(Integer, ForeignKey("notification_templates.id"), nullable=True)
    whatsapp_message_id = Column(String(100), index=True)  # WhatsApp's unique message ID
    recipient_phone = Column(String(20), nullable=False)
    status = Column(Enum(MessageStatus), default=MessageStatus.SENT, nullable=False)
    status_timestamp = Column(DateTime(timezone=True))
    error_message = Column(Text)
    metadata = Column(Text)  # JSON data for additional message info
    is_automated = Column(Boolean, default=False, nullable=False)
    scheduled_for = Column(DateTime(timezone=True))  # For scheduled messages
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes for performance
    __table_args__ = (
        {'mysql_index': [('user_id', 'customer_id')]},
        {'mysql_index': [('status',)]},
        {'mysql_index': [('message_type',)]},
        {'mysql_index': [('recipient_phone',)]}
    )

    # Relationships
    user = relationship("User", back_populates="whatsapp_messages")
    customer = relationship("Customer", back_populates="whatsapp_messages")
    template = relationship("NotificationTemplate", back_populates="messages")
    birthday_promotion = relationship("BirthdayPromotion", back_populates="message", uselist=False)


class NotificationTemplate(Base):
    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(Enum(TemplateCategory), nullable=False)
    message_type = Column(Enum(MessageType), default=MessageType.TEXT, nullable=False)
    content = Column(Text, nullable=False)
    variables = Column(Text)  # JSON array of variable names (e.g., ["name", "points"])
    media_url = Column(String(500))
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)
    last_used = Column(DateTime(timezone=True))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes
    __table_args__ = (
        {'mysql_index': [('category',)]},
        {'mysql_index': [('is_active',)]}
    )

    # Relationships
    messages = relationship("WhatsAppMessage", back_populates="template")
    creator = relationship("User")


class WhatsAppWebhook(Base):
    __tablename__ = "whatsapp_webhooks"

    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(String(100), unique=True, nullable=False)
    event_type = Column(String(100), nullable=False)  # message, delivery, read, etc.
    payload = Column(Text, nullable=False)  # Full webhook payload JSON
    processed = Column(Boolean, default=False, nullable=False)
    processed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        {'mysql_index': [('event_type',)]},
        {'mysql_index': [('processed',)]}
    )