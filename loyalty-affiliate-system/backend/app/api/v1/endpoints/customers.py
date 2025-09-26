from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime

from ...core.database import get_db
from ...services.customer_service import CustomerService
from ...models import CustomerTier, CustomerStatus

router = APIRouter()


# Pydantic models for request/response
class CustomerCreateRequest(BaseModel):
    name: str = Field(..., description="Customer full name")
    email: str = Field(..., description="Customer email address")
    phone: str = Field(..., description="Customer phone number")
    tier: Optional[CustomerTier] = Field(CustomerTier.BRONZE, description="Initial customer tier")
    notes: Optional[str] = Field(None, description="Optional notes about the customer")


class CustomerUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    tier: Optional[CustomerTier] = None
    status: Optional[CustomerStatus] = None


class CustomerListResponse(BaseModel):
    customers: List[Dict]
    pagination: Dict


class CustomerDetailsResponse(BaseModel):
    customer: Dict
    analytics: Dict
    recent_transactions: List[Dict]
    recent_redemptions: List[Dict]
    kids: List[Dict]
    tier_history: List[Dict]


class CustomerSegmentationResponse(BaseModel):
    segments: Dict
    total_customers: int


class KidsManagementRequest(BaseModel):
    kids_data: List[Dict] = Field(..., description="List of kids information")


@router.get("/", response_model=CustomerListResponse, summary="Get all customers")
async def get_customers(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=100),
    search: Optional[str] = Query(None, description="Search by name, email, or phone"),
    tier: Optional[CustomerTier] = Query(None, description="Filter by tier"),
    status: Optional[CustomerStatus] = Query(None, description="Filter by status"),
    sort_by: str = Query(default="created_at", description="Sort field"),
    sort_order: str = Query(default="desc", description="Sort order (asc/desc)"),
    db: Session = Depends(get_db)
):
    """
    Get all customers with optional filtering and pagination.

    - **skip**: Number of customers to skip
    - **limit**: Maximum number of customers to return (max 100)
    - **search**: Search term for customer name, email, or phone
    - **tier**: Filter by customer tier
    - **status**: Filter by customer status
    - **sort_by**: Field to sort by (name, email, phone, tier, total_points, created_at, last_activity)
    - **sort_order**: Sort order (asc/desc)
    """
    customer_service = CustomerService(db)
    try:
        return customer_service.get_customer_list(
            skip=skip,
            limit=limit,
            search=search,
            tier=tier,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/", summary="Create new customer")
async def create_customer(
    request: CustomerCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new customer account.

    - **name**: Customer full name
    - **email**: Customer email address
    - **phone**: Customer phone number
    - **tier**: Initial customer tier (optional, defaults to Bronze)
    - **notes**: Optional notes about the customer
    """
    customer_service = CustomerService(db)
    try:
        customer = customer_service.create_customer(
            name=request.name,
            email=request.email,
            phone=request.phone,
            tier=request.tier,
            notes=request.notes
        )

        return {
            "message": "Customer created successfully",
            "customer": {
                "id": customer.id,
                "user_id": customer.user_id,
                "name": customer.user.name,
                "email": customer.user.email,
                "phone": customer.user.phone,
                "tier": customer.tier.value,
                "status": customer.status.value,
                "created_at": customer.created_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{customer_id}", response_model=CustomerDetailsResponse, summary="Get customer by ID")
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed customer information including analytics, transactions, and kids.

    - **customer_id**: The customer's unique identifier
    """
    customer_service = CustomerService(db)
    try:
        return customer_service.get_customer_details(customer_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{customer_id}", summary="Update customer")
async def update_customer(
    customer_id: int,
    request: CustomerUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update customer information.

    - **customer_id**: The customer's unique identifier
    - **name**: Updated customer name (optional)
    - **email**: Updated email address (optional)
    - **phone**: Updated phone number (optional)
    - **tier**: Updated customer tier (optional)
    - **status**: Updated customer status (optional)
    """
    customer_service = CustomerService(db)
    try:
        customer = customer_service.update_customer(
            customer_id=customer_id,
            name=request.name,
            email=request.email,
            phone=request.phone,
            tier=request.tier,
            status=request.status
        )

        return {
            "message": "Customer updated successfully",
            "customer": {
                "id": customer.id,
                "name": customer.user.name,
                "email": customer.user.email,
                "phone": customer.user.phone,
                "tier": customer.tier.value,
                "status": customer.status.value,
                "updated_at": customer.updated_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{customer_id}", summary="Delete customer")
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a customer account (soft delete - marks as inactive).

    - **customer_id**: The customer's unique identifier
    """
    customer_service = CustomerService(db)
    try:
        customer_service.delete_customer(customer_id)
        return {"message": "Customer deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{customer_id}/kids", summary="Manage customer kids")
async def manage_customer_kids(
    customer_id: int,
    request: KidsManagementRequest,
    db: Session = Depends(get_db)
):
    """
    Manage customer's kids information (add, update, remove kids).

    - **customer_id**: Customer ID
    - **kids_data**: List of kids information dictionaries
    """
    customer_service = CustomerService(db)
    try:
        kids = customer_service.manage_customer_kids(
            customer_id=customer_id,
            kids_data=request.kids_data
        )

        return {
            "message": "Kids information updated successfully",
            "kids": [
                {
                    "id": kid.id,
                    "name": kid.name,
                    "date_of_birth": kid.date_of_birth.isoformat(),
                    "gender": kid.gender,
                    "age": customer_service._calculate_age(kid.date_of_birth),
                    "is_active": kid.is_active
                }
                for kid in kids
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{customer_id}/kids", summary="Get customer kids")
async def get_customer_kids(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Get customer's kids information.

    - **customer_id**: Customer ID
    """
    customer_service = CustomerService(db)

    try:
        customer = customer_service.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found")

        kids = customer_service.db.query(CustomerKid).filter(
            CustomerKid.customer_id == customer_id,
            CustomerKid.is_active == True
        ).all()

        return {
            "customer_id": customer_id,
            "kids": [
                {
                    "id": kid.id,
                    "name": kid.name,
                    "date_of_birth": kid.date_of_birth.isoformat(),
                    "gender": kid.gender,
                    "age": customer_service._calculate_age(kid.date_of_birth),
                    "notes": kid.notes,
                    "is_active": kid.is_active
                }
                for kid in kids
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{customer_id}/analytics", summary="Get customer analytics")
async def get_customer_analytics(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Get customer analytics and insights.

    - **customer_id**: Customer ID
    """
    customer_service = CustomerService(db)

    try:
        customer = customer_service.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found")

        analytics = customer_service._calculate_customer_analytics(customer_id)

        return {
            "customer_id": customer_id,
            "analytics": analytics
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/segmentation", response_model=CustomerSegmentationResponse, summary="Get customer segmentation")
async def get_customer_segmentation(
    segment_criteria: Optional[Dict] = None,
    db: Session = Depends(get_db)
):
    """
    Get customer segmentation based on various criteria.

    - **segment_criteria**: Optional segmentation criteria
    """
    customer_service = CustomerService(db)

    try:
        return customer_service.get_customer_segmentation(segment_criteria or {})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{customer_id}/timeline", summary="Get customer activity timeline")
async def get_customer_timeline(
    customer_id: int,
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db)
):
    """
    Get customer activity timeline including transactions, redemptions, and tier changes.

    - **customer_id**: Customer ID
    - **limit**: Maximum number of activities to return (max 100)
    """
    customer_service = CustomerService(db)

    try:
        activities = customer_service.get_customer_activity_timeline(customer_id, limit)
        return {"activities": activities}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))