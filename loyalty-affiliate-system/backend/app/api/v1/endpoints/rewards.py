from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime

from ...core.database import get_db
from ...services.reward_service import RewardService
from ...models import RewardStatus

router = APIRouter()


# Pydantic models for request/response
class RewardResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    points_required: int
    category: Optional[str]
    image_url: Optional[str]
    status: str
    stock_quantity: int
    max_per_customer: int
    is_featured: bool
    valid_from: Optional[str]
    valid_until: Optional[str]
    created_at: str


class RewardRedemptionResponse(BaseModel):
    id: int
    redemption_code: str
    reward: Dict
    quantity: int
    status: str
    created_at: str
    fulfilled_at: Optional[str]
    fulfilled_by: Optional[int]
    notes: Optional[str]


class RewardStatisticsResponse(BaseModel):
    reward_id: int
    reward_name: str
    total_redemptions: int
    completed_redemptions: int
    stock_remaining: str
    is_available: bool
    total_points_redeemed: int


class CreateRewardRequest(BaseModel):
    name: str
    description: str
    points_required: int = Field(gt=0)
    category: str
    stock_quantity: int = Field(default=-1, ge=-1)
    max_per_customer: int = Field(default=1, gt=0)
    image_url: Optional[str] = None
    terms_conditions: Optional[str] = None
    is_featured: bool = False
    valid_until: Optional[datetime] = None


class RedeemRewardRequest(BaseModel):
    customer_id: int
    reward_id: int
    quantity: int = Field(default=1, gt=0)
    notes: Optional[str] = None


@router.get("/", response_model=List[RewardResponse], summary="Get all rewards")
async def get_rewards(
    status: Optional[RewardStatus] = None,
    category: Optional[str] = None,
    featured_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all rewards with optional filtering.

    - **status**: Filter by reward status (active, inactive, out_of_stock, discontinued)
    - **category**: Filter by reward category
    - **featured_only**: Show only featured rewards
    """
    from ...models import Reward

    query = db.query(Reward)

    if status:
        query = query.filter(Reward.status == status)

    if category:
        query = query.filter(Reward.category == category)

    if featured_only:
        query = query.filter(Reward.is_featured == True)

    rewards = query.all()

    return [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "points_required": r.points_required,
            "category": r.category,
            "image_url": r.image_url,
            "status": r.status.value,
            "stock_quantity": r.stock_quantity,
            "max_per_customer": r.max_per_customer,
            "is_featured": r.is_featured,
            "valid_from": r.valid_from.isoformat() if r.valid_from else None,
            "valid_until": r.valid_until.isoformat() if r.valid_until else None,
            "created_at": r.created_at.isoformat()
        }
        for r in rewards
    ]


@router.get("/available/{customer_id}", response_model=List[Dict], summary="Get available rewards for customer")
async def get_available_rewards(customer_id: int, db: Session = Depends(get_db)):
    """
    Get rewards available for redemption by a specific customer.

    - **customer_id**: Customer ID to check availability for
    """
    reward_service = RewardService(db)
    try:
        return reward_service.get_available_rewards(customer_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/redeem", summary="Redeem a reward")
async def redeem_reward(request: RedeemRewardRequest, db: Session = Depends(get_db)):
    """
    Redeem a reward for a customer.

    - **customer_id**: Customer ID making the redemption
    - **reward_id**: Reward ID to redeem
    - **quantity**: Quantity to redeem (default: 1)
    - **notes**: Optional redemption notes
    """
    reward_service = RewardService(db)
    try:
        result = reward_service.redeem_reward(
            customer_id=request.customer_id,
            reward_id=request.reward_id,
            quantity=request.quantity,
            notes=request.notes
        )

        return {
            "message": "Reward redeemed successfully",
            **result
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/redeem/{redemption_id}/fulfill", summary="Fulfill a redemption")
async def fulfill_redemption(
    redemption_id: int,
    fulfilled_by: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Mark a redemption as fulfilled.

    - **redemption_id**: Redemption ID to fulfill
    - **fulfilled_by**: User ID who fulfilled the redemption
    - **notes**: Optional fulfillment notes
    """
    reward_service = RewardService(db)
    try:
        success = reward_service.fulfill_redemption(
            redemption_id=redemption_id,
            fulfilled_by=fulfilled_by,
            notes=notes
        )

        if success:
            return {"message": "Redemption fulfilled successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to fulfill redemption")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/redeem/{redemption_id}/cancel", summary="Cancel a redemption")
async def cancel_redemption(
    redemption_id: int,
    cancelled_by: int,
    reason: str,
    db: Session = Depends(get_db)
):
    """
    Cancel a redemption and refund points.

    - **redemption_id**: Redemption ID to cancel
    - **cancelled_by**: User ID who cancelled the redemption
    - **reason**: Reason for cancellation
    """
    reward_service = RewardService(db)
    try:
        result = reward_service.cancel_redemption(
            redemption_id=redemption_id,
            cancelled_by=cancelled_by,
            reason=reason
        )

        return {
            "message": "Redemption cancelled successfully",
            **result
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/history/{customer_id}", response_model=Dict, summary="Get customer redemption history")
async def get_redemption_history(
    customer_id: int,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get redemption history for a customer.

    - **customer_id**: Customer ID
    - **limit**: Maximum number of redemptions to return (max 100)
    - **offset**: Number of redemptions to skip
    """
    reward_service = RewardService(db)
    try:
        return reward_service.get_redemption_history(
            customer_id=customer_id,
            limit=limit,
            offset=offset
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{reward_id}/statistics", response_model=RewardStatisticsResponse, summary="Get reward statistics")
async def get_reward_statistics(reward_id: int, db: Session = Depends(get_db)):
    """
    Get statistics and analytics for a specific reward.

    - **reward_id**: Reward ID to get statistics for
    """
    reward_service = RewardService(db)
    try:
        return reward_service.get_reward_statistics(reward_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/", summary="Create new reward")
async def create_reward(request: CreateRewardRequest, db: Session = Depends(get_db)):
    """
    Create a new reward in the catalog.

    - **name**: Reward name
    - **description**: Reward description
    - **points_required**: Points required for redemption
    - **category**: Reward category
    - **stock_quantity**: Stock quantity (-1 for unlimited)
    - **max_per_customer**: Maximum redemptions per customer
    - **image_url**: Optional image URL
    - **terms_conditions**: Optional terms and conditions
    - **is_featured**: Whether to feature this reward
    - **valid_until**: Optional expiry date
    """
    reward_service = RewardService(db)
    try:
        reward = reward_service.create_reward(
            name=request.name,
            description=request.description,
            points_required=request.points_required,
            category=request.category,
            stock_quantity=request.stock_quantity,
            max_per_customer=request.max_per_customer,
            image_url=request.image_url,
            terms_conditions=request.terms_conditions,
            is_featured=request.is_featured,
            valid_until=request.valid_until,
            created_by=1  # TODO: Get from authenticated user
        )

        return {
            "message": "Reward created successfully",
            "reward": {
                "id": reward.id,
                "name": reward.name,
                "description": reward.description,
                "points_required": reward.points_required,
                "category": reward.category,
                "status": reward.status.value
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{reward_id}", summary="Update reward")
async def update_reward(
    reward_id: int,
    updates: Dict,
    db: Session = Depends(get_db)
):
    """
    Update an existing reward.

    - **reward_id**: Reward ID to update
    """
    reward_service = RewardService(db)
    try:
        reward = reward_service.update_reward(
            reward_id=reward_id,
            updates=updates,
            updated_by=1  # TODO: Get from authenticated user
        )

        return {
            "message": "Reward updated successfully",
            "reward": {
                "id": reward.id,
                "name": reward.name,
                "description": reward.description,
                "points_required": reward.points_required,
                "category": reward.category,
                "status": reward.status.value
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))