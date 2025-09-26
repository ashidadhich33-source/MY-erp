"""
WhatsApp Service

Handles WhatsApp messaging, templates, delivery tracking,
and WhatsApp Business API integration.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import requests
import json

from ..models import (
    WhatsAppMessage, NotificationTemplate, WhatsAppWebhook,
    Customer, User, MessageType, MessageDirection,
    MessageStatus, TemplateCategory
)


class WhatsAppService:
    """
    Service for handling WhatsApp operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def send_message(self, recipient_phone: str, message_type: MessageType,
                    content: str, user_id: Optional[int] = None,
                    customer_id: Optional[int] = None, template_id: Optional[int] = None,
                    media_url: Optional[str] = None, is_automated: bool = False) -> WhatsAppMessage:
        """Send a WhatsApp message."""
        message = WhatsAppMessage(
            user_id=user_id,
            customer_id=customer_id,
            message_type=message_type,
            direction=MessageDirection.OUTBOUND,
            content=content,
            media_url=media_url,
            template_id=template_id,
            recipient_phone=recipient_phone,
            status=MessageStatus.PENDING,
            is_automated=is_automated,
            scheduled_for=datetime.utcnow()
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        # In a real implementation, you would send the message to WhatsApp API here
        # For now, we'll simulate sending
        self._simulate_message_send(message.id)

        return message

    def send_template_message(self, recipient_phone: str, template_id: int,
                             variables: Optional[Dict] = None, user_id: Optional[int] = None,
                             customer_id: Optional[int] = None) -> WhatsAppMessage:
        """Send a WhatsApp template message."""
        template = self.get_template_by_id(template_id)

        if not template:
            raise ValueError("Template not found")

        # Replace variables in template content
        content = template.content
        if variables:
            for key, value in variables.items():
                content = content.replace(f"{{{{{key}}}}}", str(value))

        return self.send_message(
            recipient_phone=recipient_phone,
            message_type=MessageType.TEMPLATE,
            content=content,
            user_id=user_id,
            customer_id=customer_id,
            template_id=template_id,
            is_automated=True
        )

    def create_template(self, name: str, category: TemplateCategory,
                       message_type: MessageType, content: str,
                       variables: Optional[List[str]] = None, media_url: Optional[str] = None,
                       created_by: int = None) -> NotificationTemplate:
        """Create a new WhatsApp template."""
        # Check if template name already exists
        existing_template = self.db.query(NotificationTemplate).filter(
            NotificationTemplate.name == name
        ).first()

        if existing_template:
            raise ValueError("Template name already exists")

        template = NotificationTemplate(
            name=name,
            category=category,
            message_type=message_type,
            content=content,
            variables=json.dumps(variables) if variables else None,
            media_url=media_url,
            is_active=True,
            is_default=False,
            usage_count=0,
            created_by=created_by
        )

        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)

        return template

    def get_template_by_id(self, template_id: int) -> Optional[NotificationTemplate]:
        """Get template by ID."""
        return self.db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()

    def get_templates_by_category(self, category: TemplateCategory) -> List[NotificationTemplate]:
        """Get templates by category."""
        return self.db.query(NotificationTemplate).filter(
            and_(
                NotificationTemplate.category == category,
                NotificationTemplate.is_active == True
            )
        ).all()

    def get_all_templates(self) -> List[NotificationTemplate]:
        """Get all active templates."""
        return self.db.query(NotificationTemplate).filter(
            NotificationTemplate.is_active == True
        ).order_by(NotificationTemplate.name).all()

    def update_template_usage(self, template_id: int) -> NotificationTemplate:
        """Update template usage statistics."""
        template = self.get_template_by_id(template_id)

        if not template:
            raise ValueError("Template not found")

        template.usage_count += 1
        template.last_used = datetime.utcnow()

        self.db.commit()
        self.db.refresh(template)

        return template

    def process_webhook(self, webhook_data: Dict) -> WhatsAppWebhook:
        """Process a WhatsApp webhook."""
        webhook = WhatsAppWebhook(
            webhook_id=webhook_data.get("id", ""),
            event_type=webhook_data.get("event_type", ""),
            payload=json.dumps(webhook_data),
            processed=False
        )

        self.db.add(webhook)
        self.db.commit()
        self.db.refresh(webhook)

        # Process the webhook asynchronously
        self._process_webhook_async(webhook.id)

        return webhook

    def get_message_history(self, customer_id: Optional[int] = None,
                           user_id: Optional[int] = None, limit: int = 50) -> List[WhatsAppMessage]:
        """Get WhatsApp message history."""
        query = self.db.query(WhatsAppMessage)

        if customer_id:
            query = query.filter(WhatsAppMessage.customer_id == customer_id)
        if user_id:
            query = query.filter(WhatsAppMessage.user_id == user_id)

        return query.order_by(WhatsAppMessage.created_at.desc()).limit(limit).all()

    def get_message_by_id(self, message_id: int) -> Optional[WhatsAppMessage]:
        """Get message by ID."""
        return self.db.query(WhatsAppMessage).filter(WhatsAppMessage.id == message_id).first()

    def update_message_status(self, message_id: int, status: MessageStatus,
                             status_timestamp: Optional[datetime] = None) -> WhatsAppMessage:
        """Update message delivery status."""
        message = self.get_message_by_id(message_id)

        if not message:
            raise ValueError("Message not found")

        message.status = status
        if status_timestamp:
            message.status_timestamp = status_timestamp
        else:
            message.status_timestamp = datetime.utcnow()

        # Update specific timestamp fields based on status
        if status == MessageStatus.SENT:
            message.sent_at = message.status_timestamp
        elif status == MessageStatus.DELIVERED:
            message.delivered_at = message.status_timestamp
        elif status == MessageStatus.READ:
            message.read_at = message.status_timestamp

        self.db.commit()
        self.db.refresh(message)

        return message

    def schedule_message(self, recipient_phone: str, message_type: MessageType,
                        content: str, scheduled_time: datetime, user_id: Optional[int] = None,
                        customer_id: Optional[int] = None, template_id: Optional[int] = None,
                        media_url: Optional[str] = None) -> WhatsAppMessage:
        """Schedule a message for later delivery."""
        message = WhatsAppMessage(
            user_id=user_id,
            customer_id=customer_id,
            message_type=message_type,
            direction=MessageDirection.OUTBOUND,
            content=content,
            media_url=media_url,
            template_id=template_id,
            recipient_phone=recipient_phone,
            status=MessageStatus.PENDING,
            is_automated=False,
            scheduled_for=scheduled_time
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message

    def get_scheduled_messages(self) -> List[WhatsAppMessage]:
        """Get messages scheduled for sending."""
        now = datetime.utcnow()

        return self.db.query(WhatsAppMessage).filter(
            and_(
                WhatsAppMessage.status == MessageStatus.PENDING,
                WhatsAppMessage.scheduled_for <= now
            )
        ).all()

    def get_message_analytics(self, start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get WhatsApp message analytics."""
        query = self.db.query(WhatsAppMessage)

        if start_date:
            query = query.filter(WhatsAppMessage.created_at >= start_date)
        if end_date:
            query = query.filter(WhatsAppMessage.created_at <= end_date)

        total_sent = query.filter(WhatsAppMessage.direction == MessageDirection.OUTBOUND).count()

        # Status breakdown
        status_breakdown = {}
        for status in MessageStatus:
            count = query.filter(WhatsAppMessage.status == status).count()
            status_breakdown[status.value] = count

        # Type breakdown
        type_breakdown = {}
        for msg_type in MessageType:
            count = query.filter(WhatsAppMessage.message_type == msg_type).count()
            type_breakdown[msg_type.value] = count

        # Response rate (simplified calculation)
        outbound_messages = query.filter(WhatsAppMessage.direction == MessageDirection.OUTBOUND).all()
        inbound_count = query.filter(WhatsAppMessage.direction == MessageDirection.INBOUND).count()
        response_rate = (inbound_count / max(len(outbound_messages), 1)) * 100

        return {
            "total_sent": total_sent,
            "status_breakdown": status_breakdown,
            "type_breakdown": type_breakdown,
            "response_rate": round(response_rate, 2),
            "delivery_rate": self._calculate_delivery_rate(status_breakdown, total_sent),
            "read_rate": self._calculate_read_rate(status_breakdown)
        }

    def send_birthday_message(self, customer_id: int, template_id: Optional[int] = None) -> WhatsAppMessage:
        """Send birthday message to customer."""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()

        if not customer:
            raise ValueError("Customer not found")

        # Get customer phone from associated user
        user = self.db.query(User).filter(User.id == customer.user_id).first()
        if not user:
            raise ValueError("User not found")

        # Use default birthday template if none specified
        if not template_id:
            template = self.db.query(NotificationTemplate).filter(
                and_(
                    NotificationTemplate.category == TemplateCategory.BIRTHDAY,
                    NotificationTemplate.is_default == True,
                    NotificationTemplate.is_active == True
                )
            ).first()

            if template:
                template_id = template.id

        if not template_id:
            raise ValueError("No birthday template available")

        return self.send_template_message(
            recipient_phone=user.phone,
            template_id=template_id,
            variables={
                "customer_name": user.name,
                "birthday_date": datetime.now().strftime("%B %d")
            },
            customer_id=customer_id
        )

    def send_welcome_message(self, customer_id: int) -> WhatsAppMessage:
        """Send welcome message to new customer."""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()

        if not customer:
            raise ValueError("Customer not found")

        user = self.db.query(User).filter(User.id == customer.user_id).first()
        if not user:
            raise ValueError("User not found")

        # Get welcome template
        template = self.db.query(NotificationTemplate).filter(
            and_(
                NotificationTemplate.category == TemplateCategory.WELCOME,
                NotificationTemplate.is_default == True,
                NotificationTemplate.is_active == True
            )
        ).first()

        if not template:
            raise ValueError("No welcome template available")

        return self.send_template_message(
            recipient_phone=user.phone,
            template_id=template.id,
            variables={
                "customer_name": user.name,
                "tier": customer.tier.value
            },
            customer_id=customer_id
        )

    def _simulate_message_send(self, message_id: int) -> None:
        """Simulate sending message to WhatsApp API."""
        # In a real implementation, this would call the WhatsApp Business API
        # For now, we'll just update the message status after a delay
        import threading
        import time

        def update_message():
            time.sleep(1)  # Simulate API call delay
            message = self.get_message_by_id(message_id)

            if message:
                # Simulate successful delivery
                self.update_message_status(message_id, MessageStatus.SENT)

                # Simulate delivery after 2 seconds
                time.sleep(2)
                self.update_message_status(message_id, MessageStatus.DELIVERED)

        # Run in background thread
        thread = threading.Thread(target=update_message)
        thread.daemon = True
        thread.start()

    def _process_webhook_async(self, webhook_id: int) -> None:
        """Process webhook asynchronously."""
        import threading

        def process():
            webhook = self.db.query(WhatsAppWebhook).filter(
                WhatsAppWebhook.id == webhook_id
            ).first()

            if webhook and not webhook.processed:
                try:
                    # Process webhook data
                    payload = json.loads(webhook.payload)

                    # Handle different webhook events
                    if webhook.event_type == "message":
                        self._handle_message_webhook(payload)
                    elif webhook.event_type == "status":
                        self._handle_status_webhook(payload)

                    webhook.processed = True
                    webhook.processed_at = datetime.utcnow()
                    self.db.commit()

                except Exception as e:
                    webhook.error_message = str(e)
                    self.db.commit()

        thread = threading.Thread(target=process)
        thread.daemon = True
        thread.start()

    def _handle_message_webhook(self, payload: Dict) -> None:
        """Handle incoming message webhook."""
        # Extract message data from webhook payload
        message_data = payload.get("message", {})

        # Create inbound message record
        message = WhatsAppMessage(
            user_id=None,  # Will be determined based on phone number
            customer_id=None,
            message_type=MessageType.TEXT,  # Default to text
            direction=MessageDirection.INBOUND,
            content=message_data.get("text", {}).get("body", ""),
            recipient_phone=payload.get("to", ""),
            status=MessageStatus.DELIVERED,
            is_automated=False,
            whatsapp_message_id=payload.get("id")
        )

        self.db.add(message)
        self.db.commit()

    def _handle_status_webhook(self, payload: Dict) -> None:
        """Handle message status webhook."""
        # Update message status based on webhook
        message_id = payload.get("id")
        status = payload.get("status")

        if message_id and status:
            # Find message by WhatsApp message ID
            message = self.db.query(WhatsAppMessage).filter(
                WhatsAppMessage.whatsapp_message_id == message_id
            ).first()

            if message:
                message_status = MessageStatus(status.lower())
                self.update_message_status(message.id, message_status)

    def _calculate_delivery_rate(self, status_breakdown: Dict, total_sent: int) -> float:
        """Calculate message delivery rate."""
        if total_sent == 0:
            return 0

        delivered = status_breakdown.get('delivered', 0) + status_breakdown.get('read', 0)
        return (delivered / total_sent) * 100

    def _calculate_read_rate(self, status_breakdown: Dict) -> float:
        """Calculate message read rate."""
        total_delivered = status_breakdown.get('delivered', 0) + status_breakdown.get('read', 0)

        if total_delivered == 0:
            return 0

        read = status_breakdown.get('read', 0)
        return (read / total_delivered) * 100