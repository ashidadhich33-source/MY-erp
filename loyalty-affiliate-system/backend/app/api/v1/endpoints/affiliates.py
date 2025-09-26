from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime

from ...core.database import get_db
from ...services.affiliate_service import AffiliateService
from ...models import AffiliateStatus, CommissionStatus

router = APIRouter()


# Pydantic models for request/response
class AffiliateRegisterRequest(BaseModel):
    user_id: int
    website_url: Optional[str] = None
    marketing_channels: Optional[List[str]] = None
    payment_method: Optional[str] = None
    payment_details: Optional[Dict] = None
    notes: Optional[str] = None


class AffiliateUpdateRequest(BaseModel):
    website_url: Optional[str] = None
    marketing_channels: Optional[List[str]] = None
    payment_method: Optional[str] = None
    payment_details: Optional[Dict] = None
    notes: Optional[str] = None


class TrackReferralRequest(BaseModel):
    affiliate_code: str
    customer_id: int
    referral_source: str = "direct"
    metadata: Optional[Dict] = None


class CalculateCommissionRequest(BaseModel):
    referral_id: int
    purchase_amount: float = Field(gt=0)
    commission_rate: Optional[float] = Field(None, ge=0, le=100)


class AffiliateResponse(BaseModel):
    id: int
    affiliate_code: str
    referral_link: str
    status: str
    commission_rate: float
    total_earnings: float
    total_paid: float
    unpaid_balance: float
    website_url: Optional[str]
    joined_date: str
    last_activity: str


class ReferralResponse(BaseModel):
    id: int
    customer_id: int
    referral_code_used: str
    referral_source: str
    conversion_value: float
    commission_amount: float
    status: str
    created_at: str


class CommissionResponse(BaseModel):
    id: int
    commission_amount: float
    commission_rate: float
    status: str
    description: str
    approved_at: Optional[str]
    paid_at: Optional[str]
    payment_reference: Optional[str]
    created_at: str


class PerformanceResponse(BaseModel):
    affiliate_id: int
    affiliate_code: str
    period_days: int
    total_referrals: int
    converted_referrals: int
    conversion_rate: float
    total_conversion_value: float
    total_commission_earned: float
    total_commission_pending: float
    total_commission_paid: float
    average_commission_per_referral: float


class AffiliateDashboardResponse(BaseModel):
    affiliate: Dict
    performance: Dict
    recent_referrals: List[Dict]
    recent_commissions: List[Dict]
    summary_stats: Dict


@router.post("/register", response_model=Dict, summary="Register new affiliate")
async def register_affiliate(request: AffiliateRegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new affiliate account.

    - **user_id**: User ID to register as affiliate
    - **website_url**: Affiliate's website URL (optional)
    - **marketing_channels**: Marketing channels (optional)
    - **payment_method**: Preferred payment method (optional)
    - **payment_details**: Payment details dictionary (optional)
    - **notes**: Additional notes (optional)
    """
    affiliate_service = AffiliateService(db)
    try:
        affiliate = affiliate_service.register_affiliate(
            user_id=request.user_id,
            website_url=request.website_url,
            marketing_channels=request.marketing_channels,
            payment_method=request.payment_method,
            payment_details=request.payment_details,
            notes=request.notes
        )

        return {
            "message": "Affiliate registered successfully",
            "affiliate": {
                "id": affiliate.id,
                "affiliate_code": affiliate.affiliate_code,
                "referral_link": affiliate.referral_link,
                "status": affiliate.status.value,
                "commission_rate": affiliate.commission_rate,
                "joined_date": affiliate.joined_date.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/approve/{affiliate_id}", summary="Approve affiliate application")
async def approve_affiliate(affiliate_id: int, approved_by: int, db: Session = Depends(get_db)):
    """
    Approve an affiliate application.

    - **affiliate_id**: Affiliate ID to approve
    - **approved_by**: User ID who approved the application
    """
    affiliate_service = AffiliateService(db)
    try:
        affiliate = affiliate_service.approve_affiliate(affiliate_id, approved_by)

        return {
            "message": "Affiliate approved successfully",
            "affiliate": {
                "id": affiliate.id,
                "affiliate_code": affiliate.affiliate_code,
                "status": affiliate.status.value,
                "approved_at": affiliate.approved_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[AffiliateResponse], summary="Get all affiliates")
async def get_affiliates(
    status: Optional[AffiliateStatus] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all registered affiliates with optional filtering.

    - **status**: Filter by affiliate status
    - **skip**: Number of affiliates to skip
    - **limit**: Maximum number of affiliates to return
    """
    from ...models import Affiliate

    query = db.query(Affiliate)

    if status:
        query = query.filter(Affiliate.status == status)

    affiliates = query.offset(skip).limit(limit).all()

    return [
        {
            "id": a.id,
            "affiliate_code": a.affiliate_code,
            "referral_link": a.referral_link,
            "status": a.status.value,
            "commission_rate": a.commission_rate,
            "total_earnings": a.total_earnings,
            "total_paid": a.total_paid,
            "unpaid_balance": a.unpaid_balance,
            "website_url": a.website_url,
            "joined_date": a.joined_date.isoformat(),
            "last_activity": a.last_activity.isoformat()
        }
        for a in affiliates
    ]


@router.get("/{affiliate_id}", response_model=AffiliateResponse, summary="Get affiliate by ID")
async def get_affiliate(affiliate_id: int, db: Session = Depends(get_db)):
    """
    Get a specific affiliate by their ID.

    - **affiliate_id**: The affiliate's unique identifier
    """
    affiliate_service = AffiliateService(db)
    try:
        affiliate = affiliate_service.db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
        if not affiliate:
            raise ValueError(f"Affiliate with ID {affiliate_id} not found")

        return {
            "id": affiliate.id,
            "affiliate_code": affiliate.affiliate_code,
            "referral_link": affiliate.referral_link,
            "status": affiliate.status.value,
            "commission_rate": affiliate.commission_rate,
            "total_earnings": affiliate.total_earnings,
            "total_paid": affiliate.total_paid,
            "unpaid_balance": affiliate.unpaid_balance,
            "website_url": affiliate.website_url,
            "joined_date": affiliate.joined_date.isoformat(),
            "last_activity": affiliate.last_activity.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{affiliate_id}", summary="Update affiliate profile")
async def update_affiliate(
    affiliate_id: int,
    request: AffiliateUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update affiliate profile information.

    - **affiliate_id**: Affiliate ID to update
    """
    affiliate_service = AffiliateService(db)
    try:
        affiliate = affiliate_service.update_affiliate_profile(
            affiliate_id=affiliate_id,
            website_url=request.website_url,
            marketing_channels=request.marketing_channels,
            payment_method=request.payment_method,
            payment_details=request.payment_details,
            notes=request.notes
        )

        return {
            "message": "Affiliate profile updated successfully",
            "affiliate": {
                "id": affiliate.id,
                "affiliate_code": affiliate.affiliate_code,
                "website_url": affiliate.website_url,
                "marketing_channels": affiliate.marketing_channels,
                "payment_method": affiliate.payment_method,
                "notes": affiliate.notes
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/track-referral", summary="Track customer referral")
async def track_referral(request: TrackReferralRequest, db: Session = Depends(get_db)):
    """
    Track a customer referral by an affiliate.

    - **affiliate_code**: Affiliate code used for referral
    - **customer_id**: Customer who was referred
    - **referral_source**: Source of the referral
    - **metadata**: Additional referral metadata
    """
    affiliate_service = AffiliateService(db)
    try:
        referral = affiliate_service.track_referral(
            affiliate_code=request.affiliate_code,
            customer_id=request.customer_id,
            referral_source=request.referral_source,
            metadata=request.metadata
        )

        if referral:
            return {
                "message": "Referral tracked successfully",
                "referral": {
                    "id": referral.id,
                    "affiliate_id": referral.affiliate_id,
                    "customer_id": referral.customer_id,
                    "referral_code_used": referral.referral_code_used,
                    "status": referral.status,
                    "created_at": referral.created_at.isoformat()
                }
            }
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Affiliate code not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/calculate-commission", summary="Calculate commission for referral")
async def calculate_commission(request: CalculateCommissionRequest, db: Session = Depends(get_db)):
    """
    Calculate commission for a customer referral.

    - **referral_id**: Referral ID
    - **purchase_amount**: Amount of the purchase
    - **commission_rate**: Commission rate (optional, uses affiliate's default if not provided)
    """
    affiliate_service = AffiliateService(db)
    try:
        commission = affiliate_service.calculate_commission(
            referral_id=request.referral_id,
            purchase_amount=request.purchase_amount,
            commission_rate=request.commission_rate
        )

        return {
            "message": "Commission calculated successfully",
            "commission": {
                "id": commission.id,
                "affiliate_id": commission.affiliate_id,
                "commission_amount": commission.commission_amount,
                "commission_rate": commission.commission_rate,
                "status": commission.status.value,
                "description": commission.description,
                "created_at": commission.created_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/commissions/{commission_id}/approve", summary="Approve commission")
async def approve_commission(commission_id: int, approved_by: int, db: Session = Depends(get_db)):
    """
    Approve a commission for payout.

    - **commission_id**: Commission ID to approve
    - **approved_by**: User ID who approved the commission
    """
    affiliate_service = AffiliateService(db)
    try:
        commission = affiliate_service.approve_commission(commission_id, approved_by)

        return {
            "message": "Commission approved successfully",
            "commission": {
                "id": commission.id,
                "status": commission.status.value,
                "approved_at": commission.approved_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/performance/{affiliate_id}", response_model=PerformanceResponse, summary="Get affiliate performance")
async def get_affiliate_performance(
    affiliate_id: int,
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get affiliate performance metrics.

    - **affiliate_id**: Affiliate ID
    - **days**: Number of days to look back (default: 30)
    """
    affiliate_service = AffiliateService(db)
    try:
        return affiliate_service.get_affiliate_performance(affiliate_id, days)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/referrals/{affiliate_id}", response_model=Dict, summary="Get affiliate referrals")
async def get_affiliate_referrals(
    affiliate_id: int,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get referrals for an affiliate.

    - **affiliate_id**: Affiliate ID
    - **limit**: Maximum number of referrals to return
    - **offset**: Number of referrals to skip
    - **status**: Filter by referral status
    """
    affiliate_service = AffiliateService(db)
    try:
        return affiliate_service.get_affiliate_referrals(
            affiliate_id=affiliate_id,
            limit=limit,
            offset=offset,
            status=status
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/commissions/{affiliate_id}", response_model=Dict, summary="Get affiliate commissions")
async def get_affiliate_commissions(
    affiliate_id: int,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    status: Optional[CommissionStatus] = None,
    db: Session = Depends(get_db)
):
    """
    Get commissions for an affiliate.

    - **affiliate_id**: Affiliate ID
    - **limit**: Maximum number of commissions to return
    - **offset**: Number of commissions to skip
    - **status**: Filter by commission status
    """
    affiliate_service = AffiliateService(db)
    try:
        return affiliate_service.get_affiliate_commissions(
            affiliate_id=affiliate_id,
            limit=limit,
            offset=offset,
            status=status
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/dashboard/{affiliate_id}", response_model=AffiliateDashboardResponse, summary="Get affiliate dashboard")
async def get_affiliate_dashboard(affiliate_id: int, db: Session = Depends(get_db)):
    """
    Get comprehensive dashboard data for an affiliate.

    - **affiliate_id**: Affiliate ID
    """
    affiliate_service = AffiliateService(db)
    try:
        return affiliate_service.get_affiliate_dashboard(affiliate_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))