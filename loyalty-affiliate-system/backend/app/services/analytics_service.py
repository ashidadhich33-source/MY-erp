"""
Analytics & Reporting Business Logic Service.

Handles KPI calculations, metrics aggregation, report generation, data export,
and advanced analytics for the loyalty and affiliate system.
"""

from typing import List, Optional, Dict, Tuple, Any
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text, case
from collections import defaultdict
import json
import calendar
from dateutil.relativedelta import relativedelta
import logging

from ..models import (
    User, UserRole, UserStatus,
    Customer, CustomerTier, CustomerStatus, CustomerTierHistory,
    CustomerKid,
    LoyaltyTransaction, TransactionType, TransactionSource,
    Reward, RewardRedemption, RedemptionStatus,
    Affiliate, CustomerReferral, AffiliateCommission, PayoutRequest,
    WhatsAppMessage, MessageType, MessageDirection, MessageStatus,
    BirthdayPromotion
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service class for analytics and reporting operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_kpi_dashboard(self, date_from: Optional[date] = None, date_to: Optional[date] = None) -> Dict:
        """
        Get comprehensive KPI dashboard data.

        Args:
            date_from: Start date for analysis period
            date_to: End date for analysis period

        Returns:
            Dictionary with all KPI data
        """
        if not date_from:
            date_from = date.today() - timedelta(days=30)
        if not date_to:
            date_to = date.today()

        # Customer KPIs
        customer_kpis = self._calculate_customer_kpis(date_from, date_to)

        # Loyalty KPIs
        loyalty_kpis = self._calculate_loyalty_kpis(date_from, date_to)

        # Affiliate KPIs
        affiliate_kpis = self._calculate_affiliate_kpis(date_from, date_to)

        # WhatsApp KPIs
        whatsapp_kpis = self._calculate_whatsapp_kpis(date_from, date_to)

        # Financial KPIs
        financial_kpis = self._calculate_financial_kpis(date_from, date_to)

        # Trend analysis
        trends = self._calculate_trends(date_from, date_to)

        return {
            "period": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat(),
                "days": (date_to - date_from).days
            },
            "customer_kpis": customer_kpis,
            "loyalty_kpis": loyalty_kpis,
            "affiliate_kpis": affiliate_kpis,
            "whatsapp_kpis": whatsapp_kpis,
            "financial_kpis": financial_kpis,
            "trends": trends,
            "generated_at": datetime.utcnow().isoformat()
        }

    def _calculate_customer_kpis(self, date_from: date, date_to: date) -> Dict:
        """Calculate customer-related KPIs."""
        # Total customers
        total_customers = self.db.query(func.count(Customer.id)).scalar()

        # Active customers
        active_customers = self.db.query(func.count(Customer.id)).filter(
            Customer.status == CustomerStatus.ACTIVE
        ).scalar()

        # New customers in period
        new_customers = self.db.query(func.count(Customer.id)).filter(
            and_(
                Customer.joined_date >= date_from,
                Customer.joined_date <= date_to
            )
        ).scalar()

        # Customer retention rate
        previous_period_start = date_from - timedelta(days=(date_to - date_from).days)
        customers_at_start = self.db.query(func.count(Customer.id)).filter(
            Customer.joined_date <= date_from
        ).scalar()

        customers_retained = self.db.query(func.count(Customer.id)).filter(
            and_(
                Customer.joined_date <= date_from,
                Customer.status == CustomerStatus.ACTIVE
            )
        ).scalar()

        retention_rate = (customers_retained / customers_at_start * 100) if customers_at_start > 0 else 0

        # Tier distribution
        tier_distribution = {}
        for tier in CustomerTier:
            count = self.db.query(func.count(Customer.id)).filter(
                Customer.tier == tier
            ).scalar()
            tier_distribution[tier.value] = count

        # Customer segmentation
        segmentation = self._calculate_customer_segmentation()

        # Top customers by points
        top_customers = self.db.query(
            Customer, User.name, User.email
        ).join(User).filter(
            Customer.status == CustomerStatus.ACTIVE
        ).order_by(Customer.total_points.desc()).limit(10).all()

        return {
            "total_customers": total_customers,
            "active_customers": active_customers,
            "inactive_customers": total_customers - active_customers,
            "new_customers": new_customers,
            "retention_rate": round(retention_rate, 2),
            "tier_distribution": tier_distribution,
            "segmentation": segmentation,
            "top_customers": [
                {
                    "id": customer.id,
                    "name": name,
                    "email": email,
                    "tier": customer.tier.value,
                    "total_points": customer.total_points,
                    "lifetime_points": customer.lifetime_points
                }
                for customer, name, email in top_customers
            ]
        }

    def _calculate_loyalty_kpis(self, date_from: date, date_to: date) -> Dict:
        """Calculate loyalty program KPIs."""
        # Total points issued
        total_points_issued = self.db.query(func.sum(LoyaltyTransaction.points)).filter(
            and_(
                LoyaltyTransaction.points > 0,
                LoyaltyTransaction.created_at >= datetime.combine(date_from, datetime.min.time()),
                LoyaltyTransaction.created_at <= datetime.combine(date_to, datetime.max.time())
            )
        ).scalar() or 0

        # Total points redeemed
        total_points_redeemed = self.db.query(
            func.sum(RewardRedemption.quantity * Reward.points_required)
        ).join(Reward).filter(
            and_(
                RewardRedemption.created_at >= datetime.combine(date_from, datetime.min.time()),
                RewardRedemption.created_at <= datetime.combine(date_to, datetime.max.time()),
                RewardRedemption.status == RedemptionStatus.COMPLETED
            )
        ).scalar() or 0

        # Net points (issued - redeemed)
        net_points = total_points_issued - total_points_redeemed

        # Transaction breakdown by type
        transaction_types = {}
        for trans_type in TransactionType:
            count = self.db.query(func.count(LoyaltyTransaction.id)).filter(
                and_(
                    LoyaltyTransaction.transaction_type == trans_type,
                    LoyaltyTransaction.created_at >= datetime.combine(date_from, datetime.min.time()),
                    LoyaltyTransaction.created_at <= datetime.combine(date_to, datetime.max.time())
                )
            ).scalar()
            transaction_types[trans_type.value] = count

        # Transaction breakdown by source
        transaction_sources = {}
        for source in TransactionSource:
            count = self.db.query(func.count(LoyaltyTransaction.id)).filter(
                and_(
                    LoyaltyTransaction.source == source,
                    LoyaltyTransaction.created_at >= datetime.combine(date_from, datetime.min.time()),
                    LoyaltyTransaction.created_at <= datetime.combine(date_to, datetime.max.time())
                )
            ).scalar()
            transaction_sources[source.value] = count

        # Popular rewards
        popular_rewards = self.db.query(
            Reward.name,
            Reward.category,
            func.sum(RewardRedemption.quantity).label('total_redeemed'),
            func.count(RewardRedemption.id).label('redemption_count')
        ).join(RewardRedemption).filter(
            and_(
                RewardRedemption.created_at >= datetime.combine(date_from, datetime.min.time()),
                RewardRedemption.created_at <= datetime.combine(date_to, datetime.max.time()),
                RewardRedemption.status == RedemptionStatus.COMPLETED
            )
        ).group_by(Reward.id).order_by(func.sum(RewardRedemption.quantity).desc()).limit(10).all()

        # Average points per transaction
        avg_points_per_transaction = total_points_issued / transaction_types.get('earned', 1) if transaction_types.get('earned', 0) > 0 else 0

        return {
            "total_points_issued": total_points_issued,
            "total_points_redeemed": total_points_redeemed,
            "net_points": net_points,
            "transaction_types": transaction_types,
            "transaction_sources": transaction_sources,
            "popular_rewards": [
                {
                    "name": reward.name,
                    "category": reward.category,
                    "total_redeemed": reward.total_redeemed,
                    "redemption_count": reward.redemption_count
                }
                for reward in popular_rewards
            ],
            "avg_points_per_transaction": round(avg_points_per_transaction, 2)
        }

    def _calculate_affiliate_kpis(self, date_from: date, date_to: date) -> Dict:
        """Calculate affiliate program KPIs."""
        # Total affiliates
        total_affiliates = self.db.query(func.count(Affiliate.id)).scalar()

        # Active affiliates
        active_affiliates = self.db.query(func.count(Affiliate.id)).filter(
            Affiliate.status == "active"
        ).scalar()

        # New affiliates in period
        new_affiliates = self.db.query(func.count(Affiliate.id)).filter(
            and_(
                Affiliate.created_at >= datetime.combine(date_from, datetime.min.time()),
                Affiliate.created_at <= datetime.combine(date_to, datetime.max.time())
            )
        ).scalar()

        # Total referrals
        total_referrals = self.db.query(func.count(CustomerReferral.id)).filter(
            and_(
                CustomerReferral.created_at >= datetime.combine(date_from, datetime.min.time()),
                CustomerReferral.created_at <= datetime.combine(date_to, datetime.max.time())
            )
        ).scalar()

        # Successful referrals (converted to customers)
        successful_referrals = self.db.query(func.count(CustomerReferral.id)).filter(
            and_(
                CustomerReferral.created_at >= datetime.combine(date_from, datetime.min.time()),
                CustomerReferral.created_at <= datetime.combine(date_to, datetime.max.time()),
                CustomerReferral.status == "converted"
            )
        ).scalar()

        # Conversion rate
        conversion_rate = (successful_referrals / total_referrals * 100) if total_referrals > 0 else 0

        # Total commissions earned
        total_commissions = self.db.query(func.sum(AffiliateCommission.amount)).filter(
            and_(
                AffiliateCommission.created_at >= datetime.combine(date_from, datetime.min.time()),
                AffiliateCommission.created_at <= datetime.combine(date_to, datetime.max.time()),
                AffiliateCommission.status == "approved"
            )
        ).scalar() or 0

        # Total commissions paid
        total_commissions_paid = self.db.query(func.sum(PayoutRequest.amount)).filter(
            and_(
                PayoutRequest.created_at >= datetime.combine(date_from, datetime.min.time()),
                PayoutRequest.created_at <= datetime.combine(date_to, datetime.max.time()),
                PayoutRequest.status == "completed"
            )
        ).scalar() or 0

        # Pending commissions
        pending_commissions = total_commissions - total_commissions_paid

        # Top performing affiliates
        top_affiliates = self.db.query(
            Affiliate,
            func.count(CustomerReferral.id).label('referral_count'),
            func.sum(AffiliateCommission.amount).label('total_earnings')
        ).outerjoin(CustomerReferral).outerjoin(AffiliateCommission).filter(
            Affiliate.status == "active"
        ).group_by(Affiliate.id).order_by(func.count(CustomerReferral.id).desc()).limit(10).all()

        return {
            "total_affiliates": total_affiliates,
            "active_affiliates": active_affiliates,
            "new_affiliates": new_affiliates,
            "total_referrals": total_referrals,
            "successful_referrals": successful_referrals,
            "conversion_rate": round(conversion_rate, 2),
            "total_commissions": float(total_commissions),
            "total_commissions_paid": float(total_commissions_paid),
            "pending_commissions": float(pending_commissions),
            "top_affiliates": [
                {
                    "id": affiliate.id,
                    "name": affiliate.name,
                    "email": affiliate.email,
                    "referral_count": referral_count,
                    "total_earnings": float(total_earnings or 0)
                }
                for affiliate, referral_count, total_earnings in top_affiliates
            ]
        }

    def _calculate_whatsapp_kpis(self, date_from: date, date_to: date) -> Dict:
        """Calculate WhatsApp messaging KPIs."""
        # Total messages sent
        total_sent = self.db.query(func.count(WhatsAppMessage.id)).filter(
            and_(
                WhatsAppMessage.direction == MessageDirection.OUTBOUND,
                WhatsAppMessage.created_at >= datetime.combine(date_from, datetime.min.time()),
                WhatsAppMessage.created_at <= datetime.combine(date_to, datetime.max.time())
            )
        ).scalar()

        # Messages by status
        message_statuses = {}
        for status in MessageStatus:
            count = self.db.query(func.count(WhatsAppMessage.id)).filter(
                and_(
                    WhatsAppMessage.direction == MessageDirection.OUTBOUND,
                    WhatsAppMessage.status == status,
                    WhatsAppMessage.created_at >= datetime.combine(date_from, datetime.min.time()),
                    WhatsAppMessage.created_at <= datetime.combine(date_to, datetime.max.time())
                )
            ).scalar()
            message_statuses[status.value] = count

        # Delivery rate
        delivered = message_statuses.get('delivered', 0) + message_statuses.get('read', 0)
        delivery_rate = (delivered / total_sent * 100) if total_sent > 0 else 0

        # Read rate
        read = message_statuses.get('read', 0)
        read_rate = (read / delivered * 100) if delivered > 0 else 0

        # Messages by type
        message_types = {}
        for msg_type in MessageType:
            count = self.db.query(func.count(WhatsAppMessage.id)).filter(
                and_(
                    WhatsAppMessage.message_type == msg_type,
                    WhatsAppMessage.direction == MessageDirection.OUTBOUND,
                    WhatsAppMessage.created_at >= datetime.combine(date_from, datetime.min.time()),
                    WhatsAppMessage.created_at <= datetime.combine(date_to, datetime.max.time())
                )
            ).scalar()
            message_types[msg_type.value] = count

        # Automated vs manual messages
        automated_messages = self.db.query(func.count(WhatsAppMessage.id)).filter(
            and_(
                WhatsAppMessage.direction == MessageDirection.OUTBOUND,
                WhatsAppMessage.is_automated == True,
                WhatsAppMessage.created_at >= datetime.combine(date_from, datetime.min.time()),
                WhatsAppMessage.created_at <= datetime.combine(date_to, datetime.max.time())
            )
        ).scalar()

        manual_messages = total_sent - automated_messages

        # Response rate (incoming messages after outbound)
        # This is a simplified calculation
        incoming_messages = self.db.query(func.count(WhatsAppMessage.id)).filter(
            and_(
                WhatsAppMessage.direction == MessageDirection.INBOUND,
                WhatsAppMessage.created_at >= datetime.combine(date_from, datetime.min.time()),
                WhatsAppMessage.created_at <= datetime.combine(date_to, datetime.max.time())
            )
        ).scalar()

        return {
            "total_sent": total_sent,
            "message_statuses": message_statuses,
            "delivery_rate": round(delivery_rate, 2),
            "read_rate": round(read_rate, 2),
            "message_types": message_types,
            "automated_messages": automated_messages,
            "manual_messages": manual_messages,
            "incoming_messages": incoming_messages,
            "response_rate": round((incoming_messages / total_sent * 100), 2) if total_sent > 0 else 0
        }

    def _calculate_financial_kpis(self, date_from: date, date_to: date) -> Dict:
        """Calculate financial KPIs."""
        # Points value (assuming 1 point = $0.01 for redemption)
        points_redeemed = self.db.query(
            func.sum(RewardRedemption.quantity * Reward.points_required)
        ).join(Reward).filter(
            and_(
                RewardRedemption.created_at >= datetime.combine(date_from, datetime.min.time()),
                RewardRedemption.created_at <= datetime.combine(date_to, datetime.max.time()),
                RewardRedemption.status == RedemptionStatus.COMPLETED
            )
        ).scalar() or 0

        points_value_redeemed = points_redeemed * 0.01  # Convert to dollars

        # Commission costs
        commission_costs = self.db.query(func.sum(AffiliateCommission.amount)).filter(
            and_(
                AffiliateCommission.created_at >= datetime.combine(date_from, datetime.min.time()),
                AffiliateCommission.created_at <= datetime.combine(date_to, datetime.max.time()),
                AffiliateCommission.status == "approved"
            )
        ).scalar() or 0

        # Net program cost
        net_program_cost = points_value_redeemed + commission_costs

        # Customer lifetime value estimation
        avg_customer_value = self._calculate_average_customer_value()

        # ROI calculation (simplified)
        # This would need more sophisticated calculation in real implementation
        total_customers = self.db.query(func.count(Customer.id)).scalar()
        roi = (avg_customer_value * total_customers) / net_program_cost if net_program_cost > 0 else 0

        return {
            "points_value_redeemed": round(points_value_redeemed, 2),
            "commission_costs": round(float(commission_costs), 2),
            "net_program_cost": round(net_program_cost, 2),
            "avg_customer_value": round(avg_customer_value, 2),
            "total_customers": total_customers,
            "roi": round(roi, 2)
        }

    def _calculate_customer_segmentation(self) -> Dict:
        """Calculate customer segmentation based on activity and value."""
        segments = {
            "high_value": {"count": 0, "description": "Gold/Platinum tier with high points"},
            "active": {"count": 0, "description": "Active within last 30 days"},
            "inactive": {"count": 0, "description": "No activity for 90+ days"},
            "new": {"count": 0, "description": "Joined within last 30 days"},
            "at_risk": {"count": 0, "description": "High value but inactive"},
            "engaged": {"count": 0, "description": "High activity and engagement"}
        }

        thirty_days_ago = datetime.now() - timedelta(days=30)
        ninety_days_ago = datetime.now() - timedelta(days=90)

        customers = self.db.query(Customer).all()

        for customer in customers:
            if customer.tier in [CustomerTier.GOLD, CustomerTier.PLATINUM]:
                segments["high_value"]["count"] += 1

            days_since_active = (datetime.now() - customer.last_activity).days

            if days_since_active <= 30:
                segments["active"]["count"] += 1
            elif days_since_active >= 90:
                segments["inactive"]["count"] += 1
                if customer.tier in [CustomerTier.GOLD, CustomerTier.PLATINUM]:
                    segments["at_risk"]["count"] += 1

            days_since_joined = (datetime.now() - customer.joined_date).days
            if days_since_joined <= 30:
                segments["new"]["count"] += 1

            # Calculate engagement score (simplified)
            engagement_score = self._calculate_customer_engagement_score(customer)
            if engagement_score >= 70:
                segments["engaged"]["count"] += 1

        return segments

    def _calculate_customer_engagement_score(self, customer: Customer) -> float:
        """Calculate individual customer engagement score."""
        score = 0

        # Recency score (0-40 points)
        days_since_active = (datetime.now() - customer.last_activity).days
        if days_since_active <= 7:
            score += 40
        elif days_since_active <= 30:
            score += 30
        elif days_since_active <= 90:
            score += 20
        elif days_since_active <= 180:
            score += 10

        # Activity frequency (0-30 points)
        transactions = self.db.query(LoyaltyTransaction).filter(
            LoyaltyTransaction.customer_id == customer.id
        ).all()

        if len(transactions) >= 20:
            score += 30
        elif len(transactions) >= 10:
            score += 20
        elif len(transactions) >= 5:
            score += 10

        # Tier bonus (0-30 points)
        if customer.tier == CustomerTier.PLATINUM:
            score += 30
        elif customer.tier == CustomerTier.GOLD:
            score += 20
        elif customer.tier == CustomerTier.SILVER:
            score += 10

        return min(score, 100)

    def _calculate_average_customer_value(self) -> float:
        """Calculate average customer lifetime value."""
        # Simplified calculation - in real implementation this would be more sophisticated
        total_customers = self.db.query(func.count(Customer.id)).scalar()
        total_points_issued = self.db.query(func.sum(Customer.lifetime_points)).scalar() or 0

        if total_customers == 0:
            return 0

        # Assume average 1% conversion rate of points to actual value
        avg_lifetime_points = total_points_issued / total_customers
        avg_customer_value = avg_lifetime_points * 0.01  # Convert points to value

        return avg_customer_value

    def _calculate_trends(self, date_from: date, date_to: date) -> Dict:
        """Calculate trend data for charts."""
        # Generate daily data for the period
        current_date = date_from
        daily_data = []

        while current_date <= date_to:
            day_start = datetime.combine(current_date, datetime.min.time())
            day_end = datetime.combine(current_date, datetime.max.time())

            # Daily metrics
            daily_customers = self.db.query(func.count(Customer.id)).filter(
                and_(
                    Customer.joined_date >= day_start,
                    Customer.joined_date <= day_end
                )
            ).scalar()

            daily_transactions = self.db.query(func.count(LoyaltyTransaction.id)).filter(
                and_(
                    LoyaltyTransaction.created_at >= day_start,
                    LoyaltyTransaction.created_at <= day_end
                )
            ).scalar()

            daily_redemptions = self.db.query(func.count(RewardRedemption.id)).filter(
                and_(
                    RewardRedemption.created_at >= day_start,
                    RewardRedemption.created_at <= day_end
                )
            ).scalar()

            daily_referrals = self.db.query(func.count(CustomerReferral.id)).filter(
                and_(
                    CustomerReferral.created_at >= day_start,
                    CustomerReferral.created_at <= day_end
                )
            ).scalar()

            daily_data.append({
                "date": current_date.isoformat(),
                "new_customers": daily_customers,
                "transactions": daily_transactions,
                "redemptions": daily_redemptions,
                "referrals": daily_referrals
            })

            current_date += timedelta(days=1)

        # Calculate growth rates
        if len(daily_data) >= 2:
            recent = daily_data[-7:]  # Last 7 days
            previous = daily_data[-14:-7]  # Previous 7 days

            def calculate_growth(current, previous):
                if not previous:
                    return 0
                current_total = sum(current)
                previous_total = sum(previous)
                if previous_total == 0:
                    return 100 if current_total > 0 else 0
                return ((current_total - previous_total) / previous_total * 100)

            growth_rates = {
                "customers": calculate_growth(
                    [d["new_customers"] for d in recent],
                    [d["new_customers"] for d in previous]
                ),
                "transactions": calculate_growth(
                    [d["transactions"] for d in recent],
                    [d["transactions"] for d in previous]
                ),
                "redemptions": calculate_growth(
                    [d["redemptions"] for d in recent],
                    [d["redemptions"] for d in previous]
                ),
                "referrals": calculate_growth(
                    [d["referrals"] for d in recent],
                    [d["referrals"] for d in previous]
                )
            }
        else:
            growth_rates = {"customers": 0, "transactions": 0, "redemptions": 0, "referrals": 0}

        return {
            "daily_data": daily_data,
            "growth_rates": {k: round(v, 2) for k, v in growth_rates.items()}
        }

    def generate_report(self, report_type: str, parameters: Dict) -> Dict:
        """
        Generate custom reports based on type and parameters.

        Args:
            report_type: Type of report (customer, loyalty, affiliate, whatsapp, financial)
            parameters: Report parameters (date range, filters, etc.)

        Returns:
            Report data dictionary
        """
        date_from = parameters.get('date_from', date.today() - timedelta(days=30))
        date_to = parameters.get('date_to', date.today())

        if report_type == "customer":
            return self._generate_customer_report(date_from, date_to, parameters)
        elif report_type == "loyalty":
            return self._generate_loyalty_report(date_from, date_to, parameters)
        elif report_type == "affiliate":
            return self._generate_affiliate_report(date_from, date_to, parameters)
        elif report_type == "whatsapp":
            return self._generate_whatsapp_report(date_from, date_to, parameters)
        elif report_type == "financial":
            return self._generate_financial_report(date_from, date_to, parameters)
        else:
            raise ValueError(f"Unknown report type: {report_type}")

    def _generate_customer_report(self, date_from: date, date_to: date, parameters: Dict) -> Dict:
        """Generate customer analytics report."""
        # This would generate detailed customer reports with charts data
        # For now, return KPI data with additional details
        customer_kpis = self._calculate_customer_kpis(date_from, date_to)

        # Add additional customer-specific metrics
        customers_by_tier = {}
        for tier in CustomerTier:
            customers = self.db.query(Customer).filter(
                and_(
                    Customer.tier == tier,
                    Customer.joined_date >= datetime.combine(date_from, datetime.min.time()),
                    Customer.joined_date <= datetime.combine(date_to, datetime.max.time())
                )
            ).all()

            tier_stats = {
                "count": len(customers),
                "avg_points": sum(c.total_points for c in customers) / len(customers) if customers else 0,
                "total_points": sum(c.total_points for c in customers)
            }
            customers_by_tier[tier.value] = tier_stats

        return {
            "report_type": "customer",
            "period": {"from": date_from.isoformat(), "to": date_to.isoformat()},
            "summary": customer_kpis,
            "tier_breakdown": customers_by_tier,
            "generated_at": datetime.utcnow().isoformat()
        }

    def _generate_loyalty_report(self, date_from: date, date_to: date, parameters: Dict) -> Dict:
        """Generate loyalty program report."""
        loyalty_kpis = self._calculate_loyalty_kpis(date_from, date_to)

        # Add transaction details
        transaction_details = self.db.query(
            LoyaltyTransaction.transaction_type,
            func.sum(LoyaltyTransaction.points).label('total_points'),
            func.count(LoyaltyTransaction.id).label('count')
        ).filter(
            and_(
                LoyaltyTransaction.created_at >= datetime.combine(date_from, datetime.min.time()),
                LoyaltyTransaction.created_at <= datetime.combine(date_to, datetime.max.time())
            )
        ).group_by(LoyaltyTransaction.transaction_type).all()

        return {
            "report_type": "loyalty",
            "period": {"from": date_from.isoformat(), "to": date_to.isoformat()},
            "summary": loyalty_kpis,
            "transaction_details": [
                {
                    "type": trans.transaction_type.value,
                    "total_points": trans.total_points,
                    "count": trans.count
                }
                for trans in transaction_details
            ],
            "generated_at": datetime.utcnow().isoformat()
        }

    def _generate_affiliate_report(self, date_from: date, date_to: date, parameters: Dict) -> Dict:
        """Generate affiliate program report."""
        affiliate_kpis = self._calculate_affiliate_kpis(date_from, date_to)

        # Add affiliate performance details
        affiliate_details = self.db.query(
            Affiliate,
            func.count(CustomerReferral.id).label('referrals'),
            func.sum(AffiliateCommission.amount).label('earnings')
        ).outerjoin(CustomerReferral).outerjoin(AffiliateCommission).filter(
            Affiliate.status == "active"
        ).group_by(Affiliate.id).all()

        return {
            "report_type": "affiliate",
            "period": {"from": date_from.isoformat(), "to": date_to.isoformat()},
            "summary": affiliate_kpis,
            "affiliate_details": [
                {
                    "id": affiliate.id,
                    "name": affiliate.name,
                    "email": affiliate.email,
                    "referrals": referrals,
                    "earnings": float(earnings or 0)
                }
                for affiliate, referrals, earnings in affiliate_details
            ],
            "generated_at": datetime.utcnow().isoformat()
        }

    def _generate_whatsapp_report(self, date_from: date, date_to: date, parameters: Dict) -> Dict:
        """Generate WhatsApp messaging report."""
        whatsapp_kpis = self._calculate_whatsapp_kpis(date_from, date_to)

        # Add message template performance
        template_performance = self.db.query(
            WhatsAppMessage.template_id,
            func.count(WhatsAppMessage.id).label('total_sent'),
            func.sum(case((WhatsAppMessage.status == MessageStatus.DELIVERED, 1), else_=0)).label('delivered'),
            func.sum(case((WhatsAppMessage.status == MessageStatus.READ, 1), else_=0)).label('read')
        ).filter(
            and_(
                WhatsAppMessage.direction == MessageDirection.OUTBOUND,
                WhatsAppMessage.template_id.isnot(None),
                WhatsAppMessage.created_at >= datetime.combine(date_from, datetime.min.time()),
                WhatsAppMessage.created_at <= datetime.combine(date_to, datetime.max.time())
            )
        ).group_by(WhatsAppMessage.template_id).all()

        return {
            "report_type": "whatsapp",
            "period": {"from": date_from.isoformat(), "to": date_to.isoformat()},
            "summary": whatsapp_kpis,
            "template_performance": [
                {
                    "template_id": template.template_id,
                    "total_sent": template.total_sent,
                    "delivered": template.delivered,
                    "read": template.read
                }
                for template in template_performance
            ],
            "generated_at": datetime.utcnow().isoformat()
        }

    def _generate_financial_report(self, date_from: date, date_to: date, parameters: Dict) -> Dict:
        """Generate financial performance report."""
        financial_kpis = self._calculate_financial_kpis(date_from, date_to)

        # Add detailed cost breakdown
        cost_breakdown = {
            "points_redeemed": financial_kpis["points_value_redeemed"],
            "commissions_paid": financial_kpis["commission_costs"],
            "total_costs": financial_kpis["net_program_cost"]
        }

        return {
            "report_type": "financial",
            "period": {"from": date_from.isoformat(), "to": date_to.isoformat()},
            "summary": financial_kpis,
            "cost_breakdown": cost_breakdown,
            "generated_at": datetime.utcnow().isoformat()
        }

    def export_data(self, export_type: str, parameters: Dict) -> Dict:
        """
        Export data in various formats.

        Args:
            export_type: Type of export (customers, transactions, referrals, etc.)
            parameters: Export parameters (filters, date range, format)

        Returns:
            Export data dictionary
        """
        date_from = parameters.get('date_from', date.today() - timedelta(days=30))
        date_to = parameters.get('date_to', date.today())

        if export_type == "customers":
            return self._export_customers(date_from, date_to, parameters)
        elif export_type == "transactions":
            return self._export_transactions(date_from, date_to, parameters)
        elif export_type == "referrals":
            return self._export_referrals(date_from, date_to, parameters)
        elif export_type == "redemptions":
            return self._export_redemptions(date_from, date_to, parameters)
        else:
            raise ValueError(f"Unknown export type: {export_type}")

    def _export_customers(self, date_from: date, date_to: date, parameters: Dict) -> Dict:
        """Export customer data."""
        query = self.db.query(Customer, User).join(User)

        # Apply filters
        if parameters.get('tier'):
            query = query.filter(Customer.tier == parameters['tier'])
        if parameters.get('status'):
            query = query.filter(Customer.status == parameters['status'])

        customers = query.all()

        export_data = []
        for customer, user in customers:
            export_data.append({
                "id": customer.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "tier": customer.tier.value,
                "total_points": customer.total_points,
                "lifetime_points": customer.lifetime_points,
                "status": customer.status.value,
                "joined_date": customer.joined_date.isoformat(),
                "last_activity": customer.last_activity.isoformat()
            })

        return {
            "export_type": "customers",
            "total_records": len(export_data),
            "data": export_data,
            "generated_at": datetime.utcnow().isoformat()
        }

    def _export_transactions(self, date_from: date, date_to: date, parameters: Dict) -> Dict:
        """Export transaction data."""
        query = self.db.query(LoyaltyTransaction).filter(
            and_(
                LoyaltyTransaction.created_at >= datetime.combine(date_from, datetime.min.time()),
                LoyaltyTransaction.created_at <= datetime.combine(date_to, datetime.max.time())
            )
        )

        # Apply filters
        if parameters.get('transaction_type'):
            query = query.filter(LoyaltyTransaction.transaction_type == parameters['transaction_type'])
        if parameters.get('customer_id'):
            query = query.filter(LoyaltyTransaction.customer_id == parameters['customer_id'])

        transactions = query.all()

        export_data = []
        for transaction in transactions:
            export_data.append({
                "id": transaction.id,
                "customer_id": transaction.customer_id,
                "points": transaction.points,
                "transaction_type": transaction.transaction_type.value,
                "source": transaction.source.value,
                "description": transaction.description,
                "created_at": transaction.created_at.isoformat()
            })

        return {
            "export_type": "transactions",
            "total_records": len(export_data),
            "data": export_data,
            "generated_at": datetime.utcnow().isoformat()
        }

    def _export_referrals(self, date_from: date, date_to: date, parameters: Dict) -> Dict:
        """Export referral data."""
        query = self.db.query(CustomerReferral).filter(
            and_(
                CustomerReferral.created_at >= datetime.combine(date_from, datetime.min.time()),
                CustomerReferral.created_at <= datetime.combine(date_to, datetime.max.time())
            )
        )

        # Apply filters
        if parameters.get('status'):
            query = query.filter(CustomerReferral.status == parameters['status'])
        if parameters.get('affiliate_id'):
            query = query.filter(CustomerReferral.affiliate_id == parameters['affiliate_id'])

        referrals = query.all()

        export_data = []
        for referral in referrals:
            export_data.append({
                "id": referral.id,
                "affiliate_id": referral.affiliate_id,
                "customer_name": referral.customer_name,
                "customer_email": referral.customer_email,
                "customer_phone": referral.customer_phone,
                "status": referral.status,
                "commission_amount": float(referral.commission_amount) if referral.commission_amount else 0,
                "created_at": referral.created_at.isoformat()
            })

        return {
            "export_type": "referrals",
            "total_records": len(export_data),
            "data": export_data,
            "generated_at": datetime.utcnow().isoformat()
        }

    def _export_redemptions(self, date_from: date, date_to: date, parameters: Dict) -> Dict:
        """Export redemption data."""
        query = self.db.query(RewardRedemption, Reward).join(Reward).filter(
            and_(
                RewardRedemption.created_at >= datetime.combine(date_from, datetime.min.time()),
                RewardRedemption.created_at <= datetime.combine(date_to, datetime.max.time())
            )
        )

        # Apply filters
        if parameters.get('status'):
            query = query.filter(RewardRedemption.status == parameters['status'])
        if parameters.get('customer_id'):
            query = query.filter(RewardRedemption.customer_id == parameters['customer_id'])

        redemptions = query.all()

        export_data = []
        for redemption, reward in redemptions:
            export_data.append({
                "id": redemption.id,
                "customer_id": redemption.customer_id,
                "reward_name": reward.name,
                "reward_category": reward.category,
                "points_required": reward.points_required,
                "quantity": redemption.quantity,
                "total_points": redemption.quantity * reward.points_required,
                "status": redemption.status.value,
                "created_at": redemption.created_at.isoformat()
            })

        return {
            "export_type": "redemptions",
            "total_records": len(export_data),
            "data": export_data,
            "generated_at": datetime.utcnow().isoformat()
        }