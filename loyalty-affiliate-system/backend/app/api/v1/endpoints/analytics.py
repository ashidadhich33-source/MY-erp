from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from datetime import date
from pydantic import BaseModel

from ...core.database import get_db
from ...services.analytics_service import AnalyticsService
from ...models import Customer

router = APIRouter()


# Pydantic models for request/response
class DateRangeRequest(BaseModel):
    date_from: Optional[date] = None
    date_to: Optional[date] = None


class ReportRequest(BaseModel):
    report_type: str
    parameters: Dict


class ExportRequest(BaseModel):
    export_type: str
    parameters: Dict


class KPIDashboardResponse(BaseModel):
    period: Dict
    customer_kpis: Dict
    loyalty_kpis: Dict
    affiliate_kpis: Dict
    whatsapp_kpis: Dict
    financial_kpis: Dict
    trends: Dict
    generated_at: str


class TrendDataResponse(BaseModel):
    daily_data: List[Dict]
    growth_rates: Dict[str, float]


class ReportResponse(BaseModel):
    report_type: str
    period: Dict
    summary: Dict
    details: Optional[Dict] = None
    generated_at: str


class ExportResponse(BaseModel):
    export_type: str
    total_records: int
    data: List[Dict]
    generated_at: str


@router.get("/kpi", response_model=KPIDashboardResponse, summary="Get KPI dashboard data")
async def get_kpi_dashboard(
    date_from: Optional[date] = Query(None, description="Start date for analysis"),
    date_to: Optional[date] = Query(None, description="End date for analysis"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive KPI dashboard data.

    - **date_from**: Start date for analysis (optional, defaults to 30 days ago)
    - **date_to**: End date for analysis (optional, defaults to today)
    """
    analytics_service = AnalyticsService(db)
    try:
        return analytics_service.get_kpi_dashboard(date_from, date_to)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/trends", response_model=TrendDataResponse, summary="Get trend data for charts")
async def get_trend_data(
    date_from: Optional[date] = Query(None, description="Start date for trend analysis"),
    date_to: Optional[date] = Query(None, description="End date for trend analysis"),
    db: Session = Depends(get_db)
):
    """
    Get trend data for visualization charts.

    - **date_from**: Start date for trend analysis
    - **date_to**: End date for trend analysis
    """
    analytics_service = AnalyticsService(db)
    try:
        kpi_data = analytics_service.get_kpi_dashboard(date_from, date_to)
        return {
            "daily_data": kpi_data["trends"]["daily_data"],
            "growth_rates": kpi_data["trends"]["growth_rates"]
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/reports", response_model=ReportResponse, summary="Generate custom reports")
async def generate_report(
    request: ReportRequest,
    db: Session = Depends(get_db)
):
    """
    Generate custom reports by type.

    - **report_type**: Type of report (customer, loyalty, affiliate, whatsapp, financial)
    - **parameters**: Report parameters including date range and filters
    """
    analytics_service = AnalyticsService(db)
    try:
        report_data = analytics_service.generate_report(
            report_type=request.report_type,
            parameters=request.parameters
        )

        return ReportResponse(
            report_type=report_data["report_type"],
            period=report_data["period"],
            summary=report_data["summary"],
            details=report_data.get("tier_breakdown") or report_data.get("transaction_details"),
            generated_at=report_data["generated_at"]
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/export", response_model=ExportResponse, summary="Export data")
async def export_data(
    request: ExportRequest,
    db: Session = Depends(get_db)
):
    """
    Export data in various formats.

    - **export_type**: Type of data to export (customers, transactions, referrals, redemptions)
    - **parameters**: Export parameters including date range and filters
    """
    analytics_service = AnalyticsService(db)
    try:
        export_data = analytics_service.export_data(
            export_type=request.export_type,
            parameters=request.parameters
        )

        return ExportResponse(
            export_type=export_data["export_type"],
            total_records=export_data["total_records"],
            data=export_data["data"],
            generated_at=export_data["generated_at"]
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/customer-segmentation", summary="Get customer segmentation data")
async def get_customer_segmentation(
    db: Session = Depends(get_db)
):
    """
    Get customer segmentation data for analytics.
    """
    analytics_service = AnalyticsService(db)
    try:
        kpi_data = analytics_service.get_kpi_dashboard()
        return kpi_data["customer_kpis"]["segmentation"]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/customer-analytics", summary="Get detailed customer analytics")
async def get_customer_analytics(
    customer_id: Optional[int] = Query(None, description="Specific customer ID"),
    db: Session = Depends(get_db)
):
    """
    Get detailed customer analytics.

    - **customer_id**: Optional specific customer ID for individual analytics
    """
    analytics_service = AnalyticsService(db)
    try:
        if customer_id:
            # Get individual customer analytics
            customer = analytics_service.db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                raise ValueError(f"Customer with ID {customer_id} not found")

            engagement_score = analytics_service._calculate_customer_engagement_score(customer)
            return {
                "customer_id": customer_id,
                "engagement_score": engagement_score,
                "tier": customer.tier.value,
                "total_points": customer.total_points,
                "lifetime_points": customer.lifetime_points,
                "last_activity": customer.last_activity.isoformat(),
                "segment": "high_value" if customer.tier.value in ["gold", "platinum"] else "standard"
            }
        else:
            # Get overall customer analytics
            kpi_data = analytics_service.get_kpi_dashboard()
            return kpi_data["customer_kpis"]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/loyalty-analytics", summary="Get loyalty program analytics")
async def get_loyalty_analytics(
    date_from: Optional[date] = Query(None, description="Start date for analysis"),
    date_to: Optional[date] = Query(None, description="End date for analysis"),
    db: Session = Depends(get_db)
):
    """
    Get detailed loyalty program analytics.

    - **date_from**: Start date for analysis
    - **date_to**: End date for analysis
    """
    analytics_service = AnalyticsService(db)
    try:
        kpi_data = analytics_service.get_kpi_dashboard(date_from, date_to)
        return kpi_data["loyalty_kpis"]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/affiliate-analytics", summary="Get affiliate program analytics")
async def get_affiliate_analytics(
    date_from: Optional[date] = Query(None, description="Start date for analysis"),
    date_to: Optional[date] = Query(None, description="End date for analysis"),
    db: Session = Depends(get_db)
):
    """
    Get detailed affiliate program analytics.

    - **date_from**: Start date for analysis
    - **date_to**: End date for analysis
    """
    analytics_service = AnalyticsService(db)
    try:
        kpi_data = analytics_service.get_kpi_dashboard(date_from, date_to)
        return kpi_data["affiliate_kpis"]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/whatsapp-analytics", summary="Get WhatsApp messaging analytics")
async def get_whatsapp_analytics(
    date_from: Optional[date] = Query(None, description="Start date for analysis"),
    date_to: Optional[date] = Query(None, description="End date for analysis"),
    db: Session = Depends(get_db)
):
    """
    Get detailed WhatsApp messaging analytics.

    - **date_from**: Start date for analysis
    - **date_to**: End date for analysis
    """
    analytics_service = AnalyticsService(db)
    try:
        kpi_data = analytics_service.get_kpi_dashboard(date_from, date_to)
        return kpi_data["whatsapp_kpis"]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/financial-analytics", summary="Get financial performance analytics")
async def get_financial_analytics(
    date_from: Optional[date] = Query(None, description="Start date for analysis"),
    date_to: Optional[date] = Query(None, description="End date for analysis"),
    db: Session = Depends(get_db)
):
    """
    Get detailed financial performance analytics.

    - **date_from**: Start date for analysis
    - **date_to**: End date for analysis
    """
    analytics_service = AnalyticsService(db)
    try:
        kpi_data = analytics_service.get_kpi_dashboard(date_from, date_to)
        return kpi_data["financial_kpis"]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/performance-metrics", summary="Get key performance metrics")
async def get_performance_metrics(
    db: Session = Depends(get_db)
):
    """
    Get key performance metrics for quick overview.
    """
    analytics_service = AnalyticsService(db)
    try:
        kpi_data = analytics_service.get_kpi_dashboard()

        # Extract key metrics for quick overview
        metrics = {
            "customers": {
                "total": kpi_data["customer_kpis"]["total_customers"],
                "active": kpi_data["customer_kpis"]["active_customers"],
                "retention_rate": kpi_data["customer_kpis"]["retention_rate"]
            },
            "loyalty": {
                "points_issued": kpi_data["loyalty_kpis"]["total_points_issued"],
                "points_redeemed": kpi_data["loyalty_kpis"]["total_points_redeemed"],
                "avg_per_transaction": kpi_data["loyalty_kpis"]["avg_points_per_transaction"]
            },
            "affiliates": {
                "total": kpi_data["affiliate_kpis"]["total_affiliates"],
                "conversion_rate": kpi_data["affiliate_kpis"]["conversion_rate"],
                "total_commissions": kpi_data["affiliate_kpis"]["total_commissions"]
            },
            "whatsapp": {
                "delivery_rate": kpi_data["whatsapp_kpis"]["delivery_rate"],
                "read_rate": kpi_data["whatsapp_kpis"]["read_rate"],
                "total_sent": kpi_data["whatsapp_kpis"]["total_sent"]
            },
            "financial": {
                "program_cost": kpi_data["financial_kpis"]["net_program_cost"],
                "roi": kpi_data["financial_kpis"]["roi"]
            }
        }

        return metrics
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))