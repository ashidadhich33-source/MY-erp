from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db

router = APIRouter()


@router.post("/send", summary="Send WhatsApp message")
async def send_whatsapp_message(message_data: dict, db: Session = Depends(get_db)):
    """
    Send a WhatsApp message to a customer.
    """
    # Mock implementation - replace with WhatsApp API integration in Phase 6
    return {"message_id": "msg123", "status": "sent", "recipient": message_data.get("phone")}


@router.post("/webhook", summary="WhatsApp webhook handler")
async def whatsapp_webhook(data: dict):
    """
    Handle incoming WhatsApp webhooks.
    """
    # Mock implementation - replace with webhook processing in Phase 6
    return {"status": "received", "message": "Webhook processed successfully"}


@router.get("/history/{customer_id}", summary="Get WhatsApp message history")
async def get_whatsapp_history(customer_id: int, db: Session = Depends(get_db)):
    """
    Get WhatsApp message history for a customer.
    """
    # Mock implementation - replace with database query in Phase 6
    return {
        "customer_id": customer_id,
        "messages": [
            {
                "id": 1,
                "type": "outbound",
                "content": "Welcome to our loyalty program!",
                "status": "delivered",
                "created_at": "2024-01-01T10:00:00Z"
            }
        ]
    }