from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime
import json

from ...core.database import get_db
from ...services.whatsapp_service import WhatsAppService
from ...models import MessageType, MessageDirection, TemplateCategory

router = APIRouter()


# Pydantic models for request/response
class SendMessageRequest(BaseModel):
    phone_number: str = Field(..., description="Recipient's phone number with country code")
    message_type: MessageType
    content: str
    template_id: Optional[int] = None
    media_url: Optional[str] = None
    customer_id: Optional[int] = None
    scheduled_for: Optional[datetime] = None


class TemplateCreateRequest(BaseModel):
    name: str = Field(..., description="Template name")
    category: TemplateCategory
    content: str = Field(..., description="Template content with {{variable}} placeholders")
    variables: List[str] = Field(..., description="List of variable names")
    message_type: MessageType = MessageType.TEXT
    media_url: Optional[str] = None


class SendTemplateRequest(BaseModel):
    phone_number: str
    template_name: str
    variables: Dict[str, str] = Field(..., description="Variable values for template")
    customer_id: Optional[int] = None


class WebhookResponse(BaseModel):
    status: str
    message: str
    processed_count: Optional[int] = None


class MessageHistoryResponse(BaseModel):
    messages: List[Dict]
    pagination: Dict


class TemplateResponse(BaseModel):
    id: int
    name: str
    category: str
    message_type: str
    content: str
    variables: List[str]
    media_url: Optional[str]
    usage_count: int
    last_used: Optional[str]


@router.post("/send", summary="Send WhatsApp message")
async def send_whatsapp_message(
    request: SendMessageRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Send a WhatsApp message to a customer.

    - **phone_number**: Recipient's phone number with country code (e.g., +1234567890)
    - **message_type**: Type of message (text, template, image, document, etc.)
    - **content**: Message content or template variables
    - **template_id**: Template ID if using a template
    - **media_url**: Media URL for media messages
    - **customer_id**: Associated customer ID (optional)
    - **scheduled_for**: Scheduled delivery time (optional)
    """
    whatsapp_service = WhatsAppService(db)

    try:
        # If scheduled for later, add to background tasks
        if request.scheduled_for and request.scheduled_for > datetime.utcnow():
            # In a real implementation, you'd queue this for later processing
            return {
                "message": "Message scheduled for delivery",
                "scheduled_for": request.scheduled_for.isoformat(),
                "status": "scheduled"
            }

        result = whatsapp_service.send_message(
            phone_number=request.phone_number,
            message_type=request.message_type,
            content=request.content,
            template_id=request.template_id,
            media_url=request.media_url,
            customer_id=request.customer_id,
            scheduled_for=request.scheduled_for
        )

        return {
            "message": "WhatsApp message sent successfully",
            **result
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to send message: {str(e)}")


@router.post("/webhook", summary="WhatsApp webhook handler")
async def whatsapp_webhook(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Handle incoming WhatsApp webhooks for message status updates and incoming messages.

    This endpoint receives webhooks from WhatsApp Business API and processes:
    - Message delivery confirmations
    - Message read receipts
    - Incoming customer messages
    """
    whatsapp_service = WhatsAppService(db)

    try:
        result = whatsapp_service.process_webhook(request)

        return WebhookResponse(
            status=result["status"],
            message=result["message"]
        )

    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webhook processing failed")


@router.get("/history/{customer_id}", response_model=MessageHistoryResponse, summary="Get WhatsApp message history")
async def get_whatsapp_history(
    customer_id: int,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    direction: Optional[MessageDirection] = None,
    db: Session = Depends(get_db)
):
    """
    Get WhatsApp message history for a customer.

    - **customer_id**: Customer ID
    - **limit**: Maximum number of messages to return (max 100)
    - **offset**: Number of messages to skip
    - **direction**: Filter by message direction (optional)
    """
    whatsapp_service = WhatsAppService(db)

    try:
        return whatsapp_service.get_message_history(
            customer_id=customer_id,
            limit=limit,
            offset=offset,
            direction=direction
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/templates", response_model=List[TemplateResponse], summary="Get available WhatsApp templates")
async def get_templates(
    category: Optional[TemplateCategory] = None,
    db: Session = Depends(get_db)
):
    """
    Get available WhatsApp message templates.

    - **category**: Filter by template category (optional)
    """
    whatsapp_service = WhatsAppService(db)

    try:
        templates = whatsapp_service.get_available_templates(category)

        return [
            TemplateResponse(
                id=t["id"],
                name=t["name"],
                category=t["category"],
                message_type=t["message_type"],
                content=t["content"],
                variables=t["variables"],
                media_url=t["media_url"],
                usage_count=t["usage_count"],
                last_used=t["last_used"]
            )
            for t in templates
        ]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/templates", summary="Create new WhatsApp template")
async def create_template(
    request: TemplateCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new WhatsApp message template.

    - **name**: Template name (must be unique)
    - **category**: Template category
    - **content**: Template content with {{variable}} placeholders
    - **variables**: List of variable names used in the template
    - **message_type**: Type of message
    - **media_url**: Optional media URL
    """
    whatsapp_service = WhatsAppService(db)

    try:
        template = whatsapp_service.create_template(
            name=request.name,
            category=request.category,
            content=request.content,
            variables=request.variables,
            message_type=request.message_type,
            media_url=request.media_url,
            created_by=1  # TODO: Get from authenticated user
        )

        return {
            "message": "Template created successfully",
            "template": {
                "id": template.id,
                "name": template.name,
                "category": template.category.value,
                "message_type": template.message_type.value,
                "content": template.content,
                "variables": json.loads(template.variables or "[]"),
                "is_active": template.is_active
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/send-template", summary="Send template-based message")
async def send_template_message(
    request: SendTemplateRequest,
    db: Session = Depends(get_db)
):
    """
    Send a WhatsApp message using a template.

    - **phone_number**: Recipient's phone number
    - **template_name**: Name of the template to use
    - **variables**: Dictionary of variable values
    - **customer_id**: Associated customer ID (optional)
    """
    whatsapp_service = WhatsAppService(db)

    try:
        result = whatsapp_service.send_template_message(
            phone_number=request.phone_number,
            template_name=request.template_name,
            variables=request.variables,
            customer_id=request.customer_id
        )

        return {
            "message": "Template message sent successfully",
            **result
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to send template message: {str(e)}")


@router.post("/notify/points-earned", summary="Send points earned notification")
async def send_points_notification(
    customer_id: int,
    points_earned: int,
    total_points: int,
    reason: str,
    db: Session = Depends(get_db)
):
    """
    Send a points earned notification to a customer.

    - **customer_id**: Customer ID
    - **points_earned**: Points earned in this transaction
    - **total_points**: Customer's total points balance
    - **reason**: Reason for earning points
    """
    whatsapp_service = WhatsAppService(db)

    try:
        result = whatsapp_service.send_points_notification(
            customer_id=customer_id,
            points_earned=points_earned,
            total_points=total_points,
            reason=reason
        )

        return {
            "message": "Points notification sent successfully",
            **result
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/notify/tier-upgrade", summary="Send tier upgrade notification")
async def send_tier_upgrade_notification(
    customer_id: int,
    new_tier: str,
    points_required: int,
    db: Session = Depends(get_db)
):
    """
    Send a tier upgrade notification to a customer.

    - **customer_id**: Customer ID
    - **new_tier**: New tier achieved
    - **points_required**: Points required for the new tier
    """
    whatsapp_service = WhatsAppService(db)

    try:
        result = whatsapp_service.send_tier_upgrade_notification(
            customer_id=customer_id,
            new_tier=new_tier,
            points_required=points_required
        )

        return {
            "message": "Tier upgrade notification sent successfully",
            **result
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/notify/birthday", summary="Send birthday message")
async def send_birthday_message(
    customer_id: int,
    template_category: TemplateCategory = TemplateCategory.BIRTHDAY,
    db: Session = Depends(get_db)
):
    """
    Send a birthday message to a customer.

    - **customer_id**: Customer ID
    - **template_category**: Template category to use (default: birthday)
    """
    whatsapp_service = WhatsAppService(db)

    try:
        result = whatsapp_service.send_birthday_message(
            customer_id=customer_id,
            template_category=template_category
        )

        return {
            "message": "Birthday message sent successfully",
            **result
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/delivery-status/{message_id}", summary="Get message delivery status")
async def get_delivery_status(
    message_id: str,
    db: Session = Depends(get_db)
):
    """
    Get delivery status for a WhatsApp message.

    - **message_id**: WhatsApp message ID
    """
    whatsapp_service = WhatsAppService(db)

    try:
        return whatsapp_service.get_delivery_status(message_id)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/process-birthdays", summary="Process daily birthday messages")
async def process_daily_birthdays(db: Session = Depends(get_db)):
    """
    Process daily birthday messages and create birthday promotions.

    This endpoint should be called daily by a scheduler (e.g., cron job).
    """
    whatsapp_service = WhatsAppService(db)

    try:
        result = whatsapp_service.process_daily_birthdays()

        return {
            "message": "Birthday processing completed",
            "results": result
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Birthday processing failed: {str(e)}")