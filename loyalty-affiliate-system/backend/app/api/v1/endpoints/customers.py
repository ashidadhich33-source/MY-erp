from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_db

router = APIRouter()


@router.get("/", summary="Get all customers")
async def get_customers(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db)
):
    """
    Get all customers with optional filtering and pagination.

    - **skip**: Number of customers to skip
    - **limit**: Maximum number of customers to return
    - **search**: Search term for customer name or email
    """
    # Mock implementation - replace with database queries in Phase 3
    return {
        "data": [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "loyalty_points": 150,
                "tier": "Gold"
            }
        ],
        "total": 1,
        "page": 1,
        "limit": limit
    }


@router.post("/", summary="Create new customer")
async def create_customer(customer_data: dict, db: Session = Depends(get_db)):
    """
    Create a new customer account.
    """
    # Mock implementation - replace with database insertion in Phase 3
    return {"id": 1, "message": "Customer created successfully", **customer_data}


@router.get("/{customer_id}", summary="Get customer by ID")
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Get a specific customer by their ID.
    """
    # Mock implementation - replace with database query in Phase 3
    if customer_id == 1:
        return {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "loyalty_points": 150,
            "tier": "Gold",
            "created_at": "2024-01-01T00:00:00Z"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )


@router.put("/{customer_id}", summary="Update customer")
async def update_customer(customer_id: int, customer_data: dict, db: Session = Depends(get_db)):
    """
    Update customer information.
    """
    # Mock implementation - replace with database update in Phase 3
    return {"id": customer_id, "message": "Customer updated successfully", **customer_data}


@router.delete("/{customer_id}", summary="Delete customer")
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Delete a customer account.
    """
    # Mock implementation - replace with database deletion in Phase 3
    return {"message": "Customer deleted successfully"}