from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime

from ...core.database import get_db
from ...services.loyalty_service import LoyaltyService
from ...models import CustomerTier, TierBenefit

router = APIRouter()


class TierBenefitResponse(BaseModel):
    id: int
    tier: str
    benefit_type: str
    benefit_value: str
    description: str
    is_active: bool
    valid_from: str
    valid_until: Optional[str]


@router.get("/", summary="Get all customer tiers")
async def get_tiers(db: Session = Depends(get_db)):
    """
    Get all available customer tiers with their benefits.
    """
    loyalty_service = LoyaltyService(db)

    tiers_data = []
    for tier in [CustomerTier.BRONZE, CustomerTier.SILVER, CustomerTier.GOLD, CustomerTier.PLATINUM]:
        benefits = loyalty_service.get_tier_benefits(tier)
        tiers_data.append({
            "tier": tier.value,
            "name": tier.value.title(),
            "benefits": benefits,
            "threshold": {
                "bronze": 0,
                "silver": 200,
                "gold": 500,
                "platinum": 1000
            }.get(tier.value, 0)
        })

    return tiers_data


@router.get("/benefits", response_model=List[TierBenefitResponse], summary="Get all tier benefits")
async def get_tier_benefits(db: Session = Depends(get_db)):
    """
    Get all tier benefits configuration.
    """
    benefits = db.query(TierBenefit).filter(TierBenefit.is_active == True).all()

    return [
        {
            "id": b.id,
            "tier": b.tier.value,
            "benefit_type": b.benefit_type,
            "benefit_value": b.benefit_value,
            "description": b.description,
            "is_active": b.is_active,
            "valid_from": b.valid_from.isoformat(),
            "valid_until": b.valid_until.isoformat() if b.valid_until else None
        }
        for b in benefits
    ]


@router.get("/customer/{customer_id}", summary="Get customer tier information")
async def get_customer_tier(customer_id: int, db: Session = Depends(get_db)):
    """
    Get tier information for a specific customer.

    - **customer_id**: Customer ID
    """
    loyalty_service = LoyaltyService(db)
    try:
        balance = loyalty_service.get_customer_balance(customer_id)
        return {
            "customer_id": customer_id,
            "current_tier": balance["current_tier"],
            "total_points": balance["total_points"],
            "next_tier": balance["next_tier"],
            "progress_to_next": balance["progress_to_next"],
            "points_to_next": balance["points_to_next"],
            "tier_benefits": balance["tier_benefits"]
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/upgrade", summary="Manually upgrade customer tier")
async def upgrade_customer_tier(
    customer_id: int,
    target_tier: CustomerTier,
    reason: str = "manual_upgrade",
    db: Session = Depends(get_db)
):
    """
    Manually upgrade a customer's tier.

    - **customer_id**: Customer ID to upgrade
    - **target_tier**: Target tier to upgrade to
    - **reason**: Reason for manual upgrade
    """
    loyalty_service = LoyaltyService(db)

    # Get customer
    from ...models import Customer
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    # Update tier
    previous_tier = customer.tier
    customer.tier = target_tier

    # Create tier history record
    from ...models import CustomerTierHistory
    history = CustomerTierHistory(
        customer_id=customer_id,
        previous_tier=previous_tier,
        new_tier=target_tier,
        points_at_upgrade=customer.total_points,
        reason=reason,
        changed_by=1  # TODO: Get from authenticated user
    )

    db.add(history)
    db.commit()

    return {
        "message": "Customer tier upgraded successfully",
        "customer_id": customer_id,
        "previous_tier": previous_tier.value,
        "new_tier": target_tier.value,
        "reason": reason
    }