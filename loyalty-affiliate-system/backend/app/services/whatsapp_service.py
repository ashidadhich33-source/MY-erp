"""
WhatsApp Integration Business Logic Service.

Handles WhatsApp Business API integration, message sending, webhook processing,
template management, and automated notifications.
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from ..models import (
    User, Customer, WhatsAppMessage, NotificationTemplate,
    MessageType, MessageDirection, MessageStatus,
    BirthdayPromotion, TemplateCategory
)
from ..core.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Service class for WhatsApp Business API integration."""

    def __init__(self, db: Session):
        self.db = db
        self.api_url = settings.WHATSAPP_API_URL
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.verify_token = settings.WHATSAPP_VERIFY_TOKEN

    def send_message(
        self,
        phone_number: str,
        message_type: MessageType,
        content: str,
        template_id: Optional[int] = None,
        media_url: Optional[str] = None,
        customer_id: Optional[int] = None,
        user_id: Optional[int] = None,
        scheduled_for: Optional[datetime] = None
    ) -> Dict:
        """
        Send a WhatsApp message via WhatsApp Business API.

        Args:
            phone_number: Recipient's phone number
            message_type: Type of message (text, image, document, etc.)
            content: Message content
            template_id: Template ID if using a template
            media_url: Media URL if sending media
            customer_id: Associated customer ID
            user_id: Associated user ID
            scheduled_for: Scheduled delivery time

        Returns:
            Dictionary with message ID and status
        """
        if not self.access_token:
            raise ValueError("WhatsApp access token not configured")

        # Clean phone number (remove +, spaces, etc.)
        clean_phone = phone_number.replace('+', '').replace(' ', '').replace('-', '')

        # Prepare API payload
        if message_type == MessageType.TEXT:
            payload = {
                "messaging_product": "whatsapp",
                "to": clean_phone,
                "type": "text",
                "text": {"body": content}
            }
        elif message_type == MessageType.TEMPLATE and template_id:
            # Get template
            template = self.db.query(NotificationTemplate).filter(
                NotificationTemplate.id == template_id
            ).first()

            if not template:
                raise ValueError(f"Template with ID {template_id} not found")

            payload = {
                "messaging_product": "whatsapp",
                "to": clean_phone,
                "type": "template",
                "template": {
                    "name": template.name.lower().replace(' ', '_'),
                    "language": {"code": "en_US"},
                    "components": [
                        {
                            "type": "body",
                            "parameters": self._parse_template_variables(content)
                        }
                    ]
                }
            }
        else:
            raise ValueError(f"Unsupported message type: {message_type}")

        # Make API call
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                f"{self.api_url}/YOUR_PHONE_NUMBER_ID/messages",
                headers=headers,
                json=payload,
                timeout=30
            )

            response.raise_for_status()
            api_response = response.json()

            # Store message in database
            message = WhatsAppMessage(
                user_id=user_id,
                customer_id=customer_id,
                message_type=message_type,
                direction=MessageDirection.OUTBOUND,
                content=content,
                media_url=media_url,
                template_id=template_id,
                whatsapp_message_id=api_response.get("messages", [{}])[0].get("id"),
                recipient_phone=clean_phone,
                status=MessageStatus.SENT,
                is_automated=template_id is not None,
                scheduled_for=scheduled_for,
                sent_at=datetime.utcnow()
            )

            self.db.add(message)
            self.db.commit()

            logger.info(f"WhatsApp message sent to {clean_phone}: {api_response}")
            return {
                "message_id": message.id,
                "whatsapp_message_id": message.whatsapp_message_id,
                "status": "sent",
                "recipient": clean_phone
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send WhatsApp message: {e}")

            # Store failed message
            message = WhatsAppMessage(
                user_id=user_id,
                customer_id=customer_id,
                message_type=message_type,
                direction=MessageDirection.OUTBOUND,
                content=content,
                recipient_phone=clean_phone,
                status=MessageStatus.FAILED,
                error_message=str(e),
                is_automated=template_id is not None
            )

            self.db.add(message)
            self.db.commit()

            raise ValueError(f"Failed to send WhatsApp message: {e}")

    def _parse_template_variables(self, content: str) -> List[Dict]:
        """
        Parse template variables from content.

        Args:
            content: Message content with variables

        Returns:
            List of parameter dictionaries for WhatsApp API
        """
        # Simple variable parsing - look for {{variable_name}} patterns
        import re

        variables = []
        pattern = r'\{\{(\w+)\}\}'

        for match in re.finditer(pattern, content):
            variables.append({
                "type": "text",
                "text": match.group(1)  # This should be replaced with actual variable values
            })

        return variables

    def process_webhook(self, webhook_data: Dict) -> Dict:
        """
        Process incoming WhatsApp webhook.

        Args:
            webhook_data: Webhook payload from WhatsApp

        Returns:
            Dictionary with processing results
        """
        try:
            # Validate webhook signature (if implemented)
            # For now, just process the webhook

            if webhook_data.get("object") != "whatsapp_business_account":
                return {"status": "ignored", "reason": "Invalid object type"}

            entries = webhook_data.get("entry", [])

            for entry in entries:
                changes = entry.get("changes", [])

                for change in changes:
                    if change.get("field") == "messages":
                        messages = change.get("value", {}).get("messages", [])

                        for message_data in messages:
                            self._handle_incoming_message(message_data)

            return {"status": "processed", "message": "Webhook processed successfully"}

        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return {"status": "error", "message": str(e)}

    def _handle_incoming_message(self, message_data: Dict):
        """
        Handle incoming WhatsApp message.

        Args:
            message_data: Message data from webhook
        """
        try:
            # Extract message information
            whatsapp_message_id = message_data.get("id")
            from_number = message_data.get("from")
            message_type = message_data.get("type", "text")

            # Find customer by phone number
            customer = self.db.query(Customer).join(User).filter(
                User.phone == from_number
            ).first()

            # Store incoming message
            message = WhatsAppMessage(
                user_id=customer.user_id if customer else None,
                customer_id=customer.id if customer else None,
                message_type=MessageType.TEXT,  # Default to text
                direction=MessageDirection.INBOUND,
                content=message_data.get("text", {}).get("body", ""),
                whatsapp_message_id=whatsapp_message_id,
                recipient_phone=from_number,
                status=MessageStatus.DELIVERED,
                is_automated=False
            )

            self.db.add(message)
            self.db.commit()

            logger.info(f"Incoming WhatsApp message from {from_number}: {message.content}")

        except Exception as e:
            logger.error(f"Error handling incoming message: {e}")

    def create_template(
        self,
        name: str,
        category: TemplateCategory,
        content: str,
        variables: List[str],
        message_type: MessageType = MessageType.TEXT,
        media_url: Optional[str] = None,
        created_by: int
    ) -> NotificationTemplate:
        """
        Create a new WhatsApp message template.

        Args:
            name: Template name
            category: Template category
            content: Template content with {{variable}} placeholders
            variables: List of variable names
            message_type: Message type
            media_url: Optional media URL
            created_by: User ID who created the template

        Returns:
            Created template object
        """
        # Check if template name already exists
        existing = self.db.query(NotificationTemplate).filter(
            NotificationTemplate.name == name
        ).first()

        if existing:
            raise ValueError(f"Template with name '{name}' already exists")

        template = NotificationTemplate(
            name=name,
            category=category,
            message_type=message_type,
            content=content,
            variables=json.dumps(variables),
            media_url=media_url,
            is_active=True,
            is_default=False,
            created_by=created_by
        )

        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)

        logger.info(f"WhatsApp template created: {name} by user {created_by}")
        return template

    def get_available_templates(self, category: Optional[TemplateCategory] = None) -> List[Dict]:
        """
        Get available WhatsApp templates.

        Args:
            category: Optional category filter

        Returns:
            List of template dictionaries
        """
        query = self.db.query(NotificationTemplate).filter(
            NotificationTemplate.is_active == True
        )

        if category:
            query = query.filter(NotificationTemplate.category == category)

        templates = query.all()

        return [
            {
                "id": t.id,
                "name": t.name,
                "category": t.category.value,
                "message_type": t.message_type.value,
                "content": t.content,
                "variables": json.loads(t.variables or "[]"),
                "media_url": t.media_url,
                "usage_count": t.usage_count,
                "last_used": t.last_used.isoformat() if t.last_used else None
            }
            for t in templates
        ]

    def send_template_message(
        self,
        phone_number: str,
        template_name: str,
        variables: Dict[str, str],
        customer_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Dict:
        """
        Send a template-based WhatsApp message.

        Args:
            phone_number: Recipient's phone number
            template_name: Name of the template to use
            variables: Dictionary of variable values
            customer_id: Associated customer ID
            user_id: Associated user ID

        Returns:
            Dictionary with message result
        """
        # Get template
        template = self.db.query(NotificationTemplate).filter(
            and_(
                NotificationTemplate.name == template_name,
                NotificationTemplate.is_active == True
            )
        ).first()

        if not template:
            raise ValueError(f"Template '{template_name}' not found or inactive")

        # Substitute variables in content
        content = template.content
        for var_name, var_value in variables.items():
            content = content.replace(f"{{{{{var_name}}}}}", var_value)

        # Update template usage
        template.usage_count += 1
        template.last_used = datetime.utcnow()

        # Send message
        return self.send_message(
            phone_number=phone_number,
            message_type=MessageType.TEMPLATE,
            content=content,
            template_id=template.id,
            customer_id=customer_id,
            user_id=user_id
        )

    def send_birthday_message(
        self,
        customer_id: int,
        template_category: TemplateCategory = TemplateCategory.BIRTHDAY
    ) -> Dict:
        """
        Send birthday message to customer.

        Args:
            customer_id: Customer ID
            template_category: Template category to use

        Returns:
            Dictionary with message result
        """
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found")

        # Get birthday template
        templates = self.get_available_templates(template_category)
        if not templates:
            raise ValueError(f"No active {template_category.value} templates found")

        template = templates[0]  # Use first available template

        # Get customer name
        user = self.db.query(User).filter(User.id == customer.user_id).first()
        if not user:
            raise ValueError("Customer user not found")

        # Prepare variables
        variables = {
            "name": user.name.split()[0],  # First name only
            "full_name": user.name,
            "phone": user.phone
        }

        # Send message
        return self.send_template_message(
            phone_number=user.phone,
            template_name=template["name"],
            variables=variables,
            customer_id=customer_id,
            user_id=user.id
        )

    def send_points_notification(
        self,
        customer_id: int,
        points_earned: int,
        total_points: int,
        reason: str
    ) -> Dict:
        """
        Send points earned notification.

        Args:
            customer_id: Customer ID
            points_earned: Points earned in this transaction
            total_points: Total points balance
            reason: Reason for earning points

        Returns:
            Dictionary with message result
        """
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found")

        user = self.db.query(User).filter(User.id == customer.user_id).first()
        if not user:
            raise ValueError("Customer user not found")

        # Get loyalty template
        templates = self.get_available_templates(TemplateCategory.LOYALTY)
        if not templates:
            logger.warning("No loyalty templates found, skipping notification")
            return {"status": "skipped", "reason": "No templates available"}

        template = templates[0]

        # Prepare variables
        variables = {
            "name": user.name.split()[0],
            "points_earned": str(points_earned),
            "total_points": str(total_points),
            "reason": reason,
            "tier": customer.tier.value
        }

        # Send message
        return self.send_template_message(
            phone_number=user.phone,
            template_name=template["name"],
            variables=variables,
            customer_id=customer_id,
            user_id=user.id
        )

    def send_tier_upgrade_notification(
        self,
        customer_id: int,
        new_tier: str,
        points_required: int
    ) -> Dict:
        """
        Send tier upgrade notification.

        Args:
            customer_id: Customer ID
            new_tier: New tier achieved
            points_required: Points required for the new tier

        Returns:
            Dictionary with message result
        """
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found")

        user = self.db.query(User).filter(User.id == customer.user_id).first()
        if not user:
            raise ValueError("Customer user not found")

        # Get loyalty template
        templates = self.get_available_templates(TemplateCategory.LOYALTY)
        if not templates:
            logger.warning("No loyalty templates found, skipping notification")
            return {"status": "skipped", "reason": "No templates available"}

        template = templates[0]

        # Prepare variables
        variables = {
            "name": user.name.split()[0],
            "new_tier": new_tier,
            "total_points": str(customer.total_points),
            "points_required": str(points_required)
        }

        # Send message
        return self.send_template_message(
            phone_number=user.phone,
            template_name=template["name"],
            variables=variables,
            customer_id=customer_id,
            user_id=user.id
        )

    def get_message_history(
        self,
        customer_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
        direction: Optional[MessageDirection] = None
    ) -> Dict:
        """
        Get WhatsApp message history.

        Args:
            customer_id: Optional customer filter
            limit: Maximum messages to return
            offset: Number of messages to skip
            direction: Optional direction filter

        Returns:
            Dictionary with messages and pagination
        """
        query = self.db.query(WhatsAppMessage)

        if customer_id:
            query = query.filter(WhatsAppMessage.customer_id == customer_id)

        if direction:
            query = query.filter(WhatsAppMessage.direction == direction)

        total = query.count()
        messages = query.order_by(WhatsAppMessage.created_at.desc()).offset(offset).limit(limit).all()

        return {
            "messages": [
                {
                    "id": msg.id,
                    "message_type": msg.message_type.value,
                    "direction": msg.direction.value,
                    "content": msg.content,
                    "media_url": msg.media_url,
                    "status": msg.status.value,
                    "sent_at": msg.sent_at.isoformat() if msg.sent_at else None,
                    "delivered_at": msg.delivered_at.isoformat() if msg.delivered_at else None,
                    "read_at": msg.read_at.isoformat() if msg.read_at else None,
                    "error_message": msg.error_message,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ],
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        }

    def get_delivery_status(self, message_id: int) -> Dict:
        """
        Get delivery status for a message.

        Args:
            message_id: WhatsApp message ID

        Returns:
            Dictionary with delivery status
        """
        message = self.db.query(WhatsAppMessage).filter(
            WhatsAppMessage.whatsapp_message_id == message_id
        ).first()

        if not message:
            raise ValueError(f"Message with ID {message_id} not found")

        return {
            "message_id": message.whatsapp_message_id,
            "status": message.status.value,
            "sent_at": message.sent_at.isoformat() if message.sent_at else None,
            "delivered_at": message.delivered_at.isoformat() if message.delivered_at else None,
            "read_at": message.read_at.isoformat() if message.read_at else None,
            "error_message": message.error_message
        }

    def process_daily_birthdays(self) -> Dict:
        """
        Process daily birthday messages and promotions.

        Returns:
            Dictionary with processing results
        """
        today = datetime.now().date()
        results = {
            "processed": 0,
            "sent": 0,
            "failed": 0,
            "errors": []
        }

        try:
            # Find customers with birthdays today
            customers = self.db.query(Customer).join(User).filter(
                and_(
                    func.date_format(User.phone, '%m%d') == today.strftime('%m%d'),  # This would need to be adapted for your DB
                    Customer.status == "active"
                )
            ).all()

            for customer in customers:
                try:
                    # Send birthday message
                    self.send_birthday_message(customer.id)
                    results["sent"] += 1
                    results["processed"] += 1

                    # Create birthday promotion
                    self._create_birthday_promotion(customer.id)

                except Exception as e:
                    logger.error(f"Failed to process birthday for customer {customer.id}: {e}")
                    results["failed"] += 1
                    results["errors"].append(f"Customer {customer.id}: {str(e)}")

            logger.info(f"Birthday processing completed: {results}")
            return results

        except Exception as e:
            logger.error(f"Error in daily birthday processing: {e}")
            results["errors"].append(str(e))
            return results

    def _create_birthday_promotion(self, customer_id: int):
        """
        Create a birthday promotion for a customer.

        Args:
            customer_id: Customer ID
        """
        try:
            # Generate unique promotion code
            import secrets
            promo_code = f"BDAY{secrets.token_hex(4).upper()}"

            # Create birthday promotion record
            promotion = BirthdayPromotion(
                customer_id=customer_id,
                promotion_type="customer_birthday",
                birthday_date=datetime.now(),
                scheduled_date=datetime.now(),
                status="sent",
                promotion_code=promo_code,
                discount_amount="10%",
                created_by=1  # System user
            )

            self.db.add(promotion)
            self.db.commit()

            logger.info(f"Birthday promotion created for customer {customer_id}: {promo_code}")

        except Exception as e:
            logger.error(f"Failed to create birthday promotion for customer {customer_id}: {e}")