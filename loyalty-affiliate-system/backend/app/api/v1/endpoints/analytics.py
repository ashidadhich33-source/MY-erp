from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db

router = APIRouter()


@router.get("/dashboard", summary="Get dashboard analytics")
async def get_dashboard_analytics(db: Session = Depends(get_db)):
    """
    Get key metrics for the dashboard.
    """
    # Mock implementation - replace with actual analytics in Phase 8
    return {
        "total_customers": 2350,
        "active_loyalty_members": 1890,
        "active_affiliates": 124,
        "total_whatsapp_messages": 8492,
        "loyalty_points_issued": 45678,
        "commissions_paid": 15420.50
    }


@router.get("/customers", summary="Get customer analytics")
async def get_customer_analytics(db: Session = Depends(get_db)):
    """
    Get customer-related analytics.
    """
    # Mock implementation - replace with actual analytics in Phase 8
    return {
        "new_customers_this_month": 45,
        "customer_retention_rate": 0.85,
        "average_points_per_customer": 194,
        "tier_distribution": {
            "Bronze": 0.45,
            "Silver": 0.30,
            "Gold": 0.20,
            "Platinum": 0.05
        }
    }


@router.get("/loyalty", summary="Get loyalty program analytics")
async def get_loyalty_analytics(db: Session = Depends(get_db)):
    """
    Get loyalty program performance analytics.
    """
    # Mock implementation - replace with actual analytics in Phase 8
    return {
        "points_earned_this_month": 5670,
        "points_redeemed_this_month": 2340,
        "popular_rewards": ["Free Coffee", "Discount Coupon", "Birthday Gift"],
        "redemption_rate": 0.42
    }