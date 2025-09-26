from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db

router = APIRouter()


@router.post("/register", summary="Register new affiliate")
async def register_affiliate(affiliate_data: dict, db: Session = Depends(get_db)):
    """
    Register a new affiliate account.
    """
    # Mock implementation - replace with database operations in Phase 5
    return {"id": 1, "message": "Affiliate registered successfully", **affiliate_data}


@router.get("/", summary="Get all affiliates")
async def get_affiliates(db: Session = Depends(get_db)):
    """
    Get all registered affiliates.
    """
    # Mock implementation - replace with database query in Phase 5
    return {
        "affiliates": [
            {
                "id": 1,
                "name": "Jane Smith",
                "email": "jane@example.com",
                "referral_code": "AFF123",
                "status": "active",
                "total_commissions": 250.00
            }
        ]
    }


@router.get("/commissions/{affiliate_id}", summary="Get affiliate commissions")
async def get_affiliate_commissions(affiliate_id: int, db: Session = Depends(get_db)):
    """
    Get commission history for an affiliate.
    """
    # Mock implementation - replace with database query in Phase 5
    return {
        "affiliate_id": affiliate_id,
        "commissions": [
            {
                "id": 1,
                "amount": 25.00,
                "status": "pending",
                "created_at": "2024-01-01T10:00:00Z"
            }
        ]
    }