from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime

from ...core.database import get_db
from ...services.loyalty_service import LoyaltyService
from ...services.reward_service import RewardService
from ...models import TransactionType, TransactionSource

router = APIRouter()


# Pydantic models for request/response
class AwardPointsRequest(BaseModel):
    customer_id: int
    points: int = Field(gt=0, description="Points must be positive")
    source: TransactionSource
    description: str
    reference_id: Optional[str] = None
    expires_at: Optional[datetime] = None


class DeductPointsRequest(BaseModel):
    customer_id: int
    points: int = Field(gt=0, description="Points must be positive")
    source: TransactionSource
    description: str
    reference_id: Optional[str] = None


class AdjustPointsRequest(BaseModel):
    customer_id: int
    points: int  # Can be negative
    description: str
    reference_id: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    points: int
    transaction_type: str
    source: str
    description: str
    reference_id: Optional[str]
    created_at: str
    expires_at: Optional[str]


class CustomerBalanceResponse(BaseModel):
    customer_id: int
    total_points: int
    lifetime_points: int
    current_tier: str
    next_tier: Optional[str]
    progress_to_next: float
    points_to_next: int
    tier_benefits: List[Dict]


@router.get("/points/{customer_id}", response_model=CustomerBalanceResponse, summary="Get customer loyalty points")
async def get_customer_points(customer_id: int, db: Session = Depends(get_db)):
    """
    Get loyalty points balance and tier information for a customer.

    - **customer_id**: The customer's unique identifier
    """
    loyalty_service = LoyaltyService(db)
    try:
        return loyalty_service.get_customer_balance(customer_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/points/award", summary="Award points to customer")
async def award_points(request: AwardPointsRequest, db: Session = Depends(get_db)):
    """
    Award loyalty points to a customer.

    - **customer_id**: Customer ID to award points to
    - **points**: Number of points to award (must be positive)
    - **source**: Source of points (purchase, referral, birthday, promotion, manual, system)
    - **description**: Description of the transaction
    - **reference_id**: Optional reference ID (order ID, etc.)
    - **expires_at**: Optional expiry date for points
    """
    loyalty_service = LoyaltyService(db)
    try:
        transaction = loyalty_service.award_points(
            customer_id=request.customer_id,
            points=request.points,
            source=request.source,
            description=request.description,
            reference_id=request.reference_id,
            expires_at=request.expires_at
        )

        return {
            "message": "Points awarded successfully",
            "transaction_id": transaction.id,
            "points_awarded": transaction.points,
            "new_balance": loyalty_service.get_customer_balance(request.customer_id)["total_points"]
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/points/deduct", summary="Deduct points from customer")
async def deduct_points(request: DeductPointsRequest, db: Session = Depends(get_db)):
    """
    Deduct loyalty points from a customer.

    - **customer_id**: Customer ID to deduct points from
    - **points**: Number of points to deduct (must be positive)
    - **source**: Source of deduction (purchase, referral, birthday, promotion, manual, system)
    - **description**: Description of the transaction
    - **reference_id**: Optional reference ID
    """
    loyalty_service = LoyaltyService(db)
    try:
        transaction = loyalty_service.deduct_points(
            customer_id=request.customer_id,
            points=request.points,
            source=request.source,
            description=request.description,
            reference_id=request.reference_id
        )

        return {
            "message": "Points deducted successfully",
            "transaction_id": transaction.id,
            "points_deducted": abs(transaction.points),
            "new_balance": loyalty_service.get_customer_balance(request.customer_id)["total_points"]
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/points/adjust", summary="Adjust customer points")
async def adjust_points(request: AdjustPointsRequest, db: Session = Depends(get_db)):
    """
    Adjust customer points (can be positive or negative).

    - **customer_id**: Customer ID to adjust points for
    - **points**: Points adjustment (can be negative)
    - **description**: Description of the adjustment
    - **reference_id**: Optional reference ID
    """
    loyalty_service = LoyaltyService(db)
    try:
        transaction = loyalty_service.adjust_points(
            customer_id=request.customer_id,
            points=request.points,
            description=request.description,
            reference_id=request.reference_id
        )

        return {
            "message": "Points adjusted successfully",
            "transaction_id": transaction.id,
            "points_adjusted": transaction.points,
            "new_balance": loyalty_service.get_customer_balance(request.customer_id)["total_points"]
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/transactions/{customer_id}", response_model=Dict, summary="Get customer point transactions")
async def get_transactions(
    customer_id: int,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    transaction_type: Optional[TransactionType] = None,
    source: Optional[TransactionSource] = None,
    db: Session = Depends(get_db)
):
    """
    Get loyalty point transaction history for a customer.

    - **customer_id**: The customer's unique identifier
    - **limit**: Maximum number of transactions to return (max 100)
    - **offset**: Number of transactions to skip
    - **transaction_type**: Filter by transaction type (optional)
    - **source**: Filter by transaction source (optional)
    """
    loyalty_service = LoyaltyService(db)
    try:
        return loyalty_service.get_transaction_history(
            customer_id=customer_id,
            limit=limit,
            offset=offset,
            transaction_type=transaction_type,
            source=source
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))