from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime

from ...core.database import get_db
from ...services.erp_service import (
    ERPIntegrationService, SyncStatus, DataMappingType, DataMapping, SyncResult
)

router = APIRouter()


# Pydantic models for request/response
class ERPConnectionRequest(BaseModel):
    host: str = Field(..., description="ERP server host")
    port: int = Field(..., description="ERP server port")
    database: str = Field(..., description="Database name")
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    api_key: Optional[str] = Field(None, description="API key")
    timeout: Optional[int] = Field(30, description="Connection timeout")


class SyncRequest(BaseModel):
    sync_type: str = Field(..., description="Type of sync (customers, sales, products)")
    full_sync: bool = Field(False, description="Whether to perform full sync")


class DataMappingRequest(BaseModel):
    mapping_type: str = Field(..., description="Type of mapping")
    mappings: List[Dict] = Field(..., description="Mapping configuration")


class SyncStatusResponse(BaseModel):
    connection_status: str
    last_sync: Optional[str]
    recent_syncs: List[Dict]
    pending_syncs: int
    failed_syncs: int


class SyncResultResponse(BaseModel):
    status: str
    records_processed: int
    records_successful: int
    records_failed: int
    errors: List[str]
    duration: float
    timestamp: str


class ERPDataSummaryResponse(BaseModel):
    customers: Dict
    products: Dict
    sales: Dict


class SyncReportResponse(BaseModel):
    summary: Dict
    details: List[Dict]


@router.post("/connect", summary="Test ERP connection")
async def test_erp_connection(
    request: ERPConnectionRequest,
    db: Session = Depends(get_db)
):
    """
    Test connection to Logic ERP system.

    - **host**: ERP server host
    - **port**: ERP server port
    - **database**: Database name
    - **username**: Username for authentication
    - **password**: Password for authentication
    - **api_key**: Optional API key
    - **timeout**: Connection timeout in seconds
    """
    erp_service = ERPIntegrationService(db)

    try:
        # Configure connection
        connection = erp_service.configure_connection(request.dict())

        # Initialize connector
        if await erp_service.initialize_connector():
            # Test connection
            result = await erp_service.test_connection()
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize ERP connector"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection test failed: {str(e)}"
        )


@router.get("/status", response_model=SyncStatusResponse, summary="Get ERP sync status")
async def get_erp_sync_status(
    db: Session = Depends(get_db)
):
    """
    Get current ERP synchronization status and history.
    """
    erp_service = ERPIntegrationService(db)

    try:
        return await erp_service.get_sync_status()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sync status: {str(e)}"
        )


@router.post("/sync/customers", response_model=SyncResultResponse, summary="Sync customers from ERP")
async def sync_customers(
    request: SyncRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Synchronize customer data from ERP system.

    - **sync_type**: Type of sync operation
    - **full_sync**: Whether to perform full sync (true) or incremental sync (false)
    """
    erp_service = ERPIntegrationService(db)

    try:
        # For background processing
        if request.full_sync:
            background_tasks.add_task(erp_service.sync_customers, True)
            return {
                "status": SyncStatus.PENDING.value,
                "records_processed": 0,
                "records_successful": 0,
                "records_failed": 0,
                "errors": [],
                "duration": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Customer sync started in background"
            }
        else:
            result = await erp_service.sync_customers(False)
            return SyncResultResponse(
                status=result.status.value,
                records_processed=result.records_processed,
                records_successful=result.records_successful,
                records_failed=result.records_failed,
                errors=result.errors,
                duration=result.duration,
                timestamp=result.timestamp.isoformat()
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Customer sync failed: {str(e)}"
        )


@router.post("/sync/sales", response_model=SyncResultResponse, summary="Sync sales from ERP")
async def sync_sales(
    request: SyncRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Synchronize sales data from ERP system.

    - **sync_type**: Type of sync operation
    - **full_sync**: Whether to perform full sync (true) or incremental sync (false)
    """
    erp_service = ERPIntegrationService(db)

    try:
        if request.full_sync:
            background_tasks.add_task(erp_service.sync_sales, True)
            return {
                "status": SyncStatus.PENDING.value,
                "records_processed": 0,
                "records_successful": 0,
                "records_failed": 0,
                "errors": [],
                "duration": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Sales sync started in background"
            }
        else:
            result = await erp_service.sync_sales(False)
            return SyncResultResponse(
                status=result.status.value,
                records_processed=result.records_processed,
                records_successful=result.records_successful,
                records_failed=result.records_failed,
                errors=result.errors,
                duration=result.duration,
                timestamp=result.timestamp.isoformat()
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sales sync failed: {str(e)}"
        )


@router.post("/sync/all", summary="Sync all data from ERP")
async def sync_all_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Synchronize all data types from ERP system (customers, sales, products).
    """
    erp_service = ERPIntegrationService(db)

    try:
        # Start all sync operations in background
        background_tasks.add_task(erp_service.sync_customers, True)
        background_tasks.add_task(erp_service.sync_sales, True)

        return {
            "message": "Full synchronization started in background",
            "sync_types": ["customers", "sales"],
            "status": SyncStatus.PENDING.value,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Full sync failed: {str(e)}"
        )


@router.get("/data-summary", response_model=ERPDataSummaryResponse, summary="Get ERP data summary")
async def get_erp_data_summary(
    db: Session = Depends(get_db)
):
    """
    Get summary of data available in ERP system.
    """
    erp_service = ERPIntegrationService(db)

    try:
        return await erp_service.get_erp_data_summary()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ERP data summary: {str(e)}"
        )


@router.post("/mappings", summary="Configure data mappings")
async def configure_data_mappings(
    request: DataMappingRequest,
    db: Session = Depends(get_db)
):
    """
    Configure data mappings between loyalty system and ERP.

    - **mapping_type**: Type of mapping (customer, product, sale, etc.)
    - **mappings**: List of mapping configurations
    """
    erp_service = ERPIntegrationService(db)

    try:
        # Convert mapping dictionaries to DataMapping objects
        mappings = [
            DataMapping(
                source_field=m.get("source_field"),
                target_field=m.get("target_field"),
                mapping_type=DataMappingType(m.get("mapping_type")),
                transformation=m.get("transformation"),
                validation_rules=m.get("validation_rules"),
                is_required=m.get("is_required", False)
            )
            for m in request.mappings
        ]

        await erp_service.configure_data_mapping(
            DataMappingType(request.mapping_type),
            mappings
        )

        return {
            "message": f"Configured {len(mappings)} mappings for {request.mapping_type}",
            "mapping_type": request.mapping_type,
            "mappings_count": len(mappings)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to configure mappings: {str(e)}"
        )


@router.get("/mappings/{mapping_type}", summary="Get data mappings")
async def get_data_mappings(
    mapping_type: str,
    db: Session = Depends(get_db)
):
    """
    Get data mapping configuration for a specific type.

    - **mapping_type**: Type of mapping to retrieve
    """
    erp_service = ERPIntegrationService(db)

    try:
        mappings = erp_service.get_data_mapping(
            DataMappingType(mapping_type)
        )

        return {
            "mapping_type": mapping_type,
            "mappings": [
                {
                    "source_field": m.source_field,
                    "target_field": m.target_field,
                    "mapping_type": m.mapping_type.value,
                    "transformation": m.transformation,
                    "validation_rules": m.validation_rules,
                    "is_required": m.is_required
                }
                for m in mappings
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get mappings: {str(e)}"
        )


@router.post("/mappings/{mapping_type}/validate", summary="Validate data mappings")
async def validate_data_mappings(
    mapping_type: str,
    db: Session = Depends(get_db)
):
    """
    Validate data mapping configuration.

    - **mapping_type**: Type of mapping to validate
    """
    erp_service = ERPIntegrationService(db)

    try:
        validation_result = await erp_service.validate_data_mapping(
            DataMappingType(mapping_type)
        )

        return {
            "mapping_type": mapping_type,
            "is_valid": validation_result["is_valid"],
            "errors": validation_result["errors"],
            "warnings": validation_result["warnings"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate mappings: {str(e)}"
        )


@router.get("/sync-history", summary="Get sync history")
async def get_sync_history(
    limit: int = Query(default=50, le=100),
    db: Session = Depends(get_db)
):
    """
    Get synchronization history.

    - **limit**: Maximum number of records to return
    """
    erp_service = ERPIntegrationService(db)

    try:
        # This would typically query a sync history table
        # For now, return mock data
        sync_history = [
            {
                "id": "sync_1",
                "sync_type": "customers",
                "status": SyncStatus.COMPLETED.value,
                "records_processed": 150,
                "records_successful": 148,
                "records_failed": 2,
                "duration": 45.2,
                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "errors": ["Customer email missing", "Phone number invalid"]
            },
            {
                "id": "sync_2",
                "sync_type": "sales",
                "status": SyncStatus.COMPLETED.value,
                "records_processed": 45,
                "records_successful": 45,
                "records_failed": 0,
                "duration": 12.8,
                "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "errors": []
            }
        ]

        return {
            "sync_history": sync_history[:limit],
            "total_count": len(sync_history)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sync history: {str(e)}"
        )


@router.post("/sync-report", response_model=SyncReportResponse, summary="Generate sync report")
async def generate_sync_report(
    sync_results: List[Dict],
    db: Session = Depends(get_db)
):
    """
    Generate synchronization report from sync results.

    - **sync_results**: List of sync result dictionaries
    """
    erp_service = ERPIntegrationService(db)

    try:
        # Convert dictionaries to SyncResult objects
        results = [
            SyncResult(
                status=SyncStatus(r.get("status", "completed")),
                records_processed=r.get("records_processed", 0),
                records_successful=r.get("records_successful", 0),
                records_failed=r.get("records_failed", 0),
                errors=r.get("errors", []),
                duration=r.get("duration", 0),
                timestamp=datetime.fromisoformat(r.get("timestamp"))
            )
            for r in sync_results
        ]

        report = erp_service.generate_sync_report(results)

        return SyncReportResponse(
            summary=report["summary"],
            details=report["details"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate sync report: {str(e)}"
        )


@router.get("/integration-health", summary="Get integration health status")
async def get_integration_health(
    db: Session = Depends(get_db)
):
    """
    Get comprehensive integration health status.
    """
    erp_service = ERPIntegrationService(db)

    try:
        connection_status = await erp_service.test_connection()
        sync_status = await erp_service.get_sync_status()
        data_summary = await erp_service.get_erp_data_summary()

        return {
            "connection": connection_status,
            "sync": sync_status,
            "data": data_summary,
            "overall_health": "healthy" if connection_status["status"] == "connected" else "unhealthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "connection": {"status": "failed", "message": str(e)},
            "sync": {"status": "unknown"},
            "data": {"error": str(e)},
            "overall_health": "unhealthy",
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/sync-schedule", summary="Configure sync schedule")
async def configure_sync_schedule(
    schedule_config: Dict,
    db: Session = Depends(get_db)
):
    """
    Configure automated synchronization schedule.

    - **schedule_config**: Schedule configuration including intervals and sync types
    """
    # This would configure a scheduler (like Celery or APScheduler)
    # For now, return success response

    return {
        "message": "Sync schedule configured successfully",
        "schedule": schedule_config,
        "next_run": (datetime.utcnow() + timedelta(hours=1)).isoformat()
    }


@router.get("/sync-schedule", summary="Get sync schedule")
async def get_sync_schedule(
    db: Session = Depends(get_db)
):
    """
    Get current synchronization schedule configuration.
    """
    # This would retrieve schedule from scheduler configuration
    # For now, return mock data

    return {
        "customers_sync": {
            "enabled": True,
            "interval_hours": 6,
            "next_run": (datetime.utcnow() + timedelta(hours=6)).isoformat()
        },
        "sales_sync": {
            "enabled": True,
            "interval_hours": 1,
            "next_run": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        },
        "products_sync": {
            "enabled": False,
            "interval_hours": 24,
            "next_run": None
        }
    }