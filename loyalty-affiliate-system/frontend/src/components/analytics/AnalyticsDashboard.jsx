import { useState, useEffect } from 'react'
import { BarChart3, TrendingUp, Users, DollarSign, MessageCircle, Target, Calendar, Download, RefreshCw } from 'lucide-react'
import { analyticsAPI } from '../../services/api'
import Card from '../ui/Card'
import Button from '../ui/Button'

const AnalyticsDashboard = () => {
  const [kpiData, setKpiData] = useState(null)
  const [trendData, setTrendData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [dateRange, setDateRange] = useState('30d')
  const [selectedMetric, setSelectedMetric] = useState('overview')

  useEffect(() => {
    fetchAnalyticsData()
  }, [dateRange])

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true)

      // Calculate date range
      const endDate = new Date()
      const startDate = new Date()

      switch (dateRange) {
        case '7d':
          startDate.setDate(endDate.getDate() - 7)
          break
        case '30d':
          startDate.setDate(endDate.getDate() - 30)
          break
        case '90d':
          startDate.setDate(endDate.getDate() - 90)
          break
        case '1y':
          startDate.setFullYear(endDate.getFullYear() - 1)
          break
        default:
          startDate.setDate(endDate.getDate() - 30)
      }

      const [kpiResponse, trendsResponse] = await Promise.all([
        analyticsAPI.getKPI({
          date_from: startDate.toISOString().split('T')[0],
          date_to: endDate.toISOString().split('T')[0]
        }),
        analyticsAPI.getTrends({
          date_from: startDate.toISOString().split('T')[0],
          date_to: endDate.toISOString().split('T')[0]
        })
      ])

      setKpiData(kpiResponse)
      setTrendData(trendsResponse)
    } catch (err) {
      setError('Failed to fetch analytics data')
      console.error('Error fetching analytics:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M'
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toLocaleString()
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const formatPercentage = (value) => {
    return `${value.toFixed(1)}%`
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="h-64 bg-gray-200 rounded"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-2xl">⚠️</span>
        </div>
        <p className="text-danger-600 mb-4">{error}</p>
        <Button onClick={fetchAnalyticsData}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Retry
        </Button>
      </div>
    )
  }

  if (!kpiData) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <BarChart3 className="h-8 w-8 text-gray-400" />
        </div>
        <p className="text-gray-600">No analytics data available</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600">
            Performance insights and key metrics for your loyalty program
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          <Button variant="outline" onClick={fetchAnalyticsData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* KPI Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Users className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Customers</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatNumber(kpiData.customer_kpis.total_customers)}
              </p>
              <p className="text-sm text-gray-500">
                {formatNumber(kpiData.customer_kpis.active_customers)} active
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Target className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Loyalty Points</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatNumber(kpiData.loyalty_kpis.total_points_issued)}
              </p>
              <p className="text-sm text-gray-500">
                {formatPercentage((kpiData.loyalty_kpis.total_points_redeemed / kpiData.loyalty_kpis.total_points_issued) * 100)} redeemed
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <TrendingUp className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Conversion Rate</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatPercentage(kpiData.affiliate_kpis.conversion_rate)}
              </p>
              <p className="text-sm text-gray-500">
                {kpiData.affiliate_kpis.successful_referrals} successful referrals
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <DollarSign className="h-8 w-8 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Program ROI</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatPercentage(kpiData.financial_kpis.roi)}
              </p>
              <p className="text-sm text-gray-500">
                {formatCurrency(kpiData.financial_kpis.net_program_cost)} total cost
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Customer Metrics */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Customer Metrics</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Retention Rate</span>
              <span className="font-semibold text-green-600">
                {formatPercentage(kpiData.customer_kpis.retention_rate)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">New Customers</span>
              <span className="font-semibold text-blue-600">
                {formatNumber(kpiData.customer_kpis.new_customers)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Customer Lifetime Value</span>
              <span className="font-semibold text-purple-600">
                {formatCurrency(kpiData.financial_kpis.avg_customer_value)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Average Engagement</span>
              <span className="font-semibold text-orange-600">
                {formatPercentage(75)} {/* This would come from actual data */}
              </span>
            </div>
          </div>
        </Card>

        {/* Loyalty Metrics */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Loyalty Program</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Points Issued</span>
              <span className="font-semibold text-blue-600">
                {formatNumber(kpiData.loyalty_kpis.total_points_issued)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Points Redeemed</span>
              <span className="font-semibold text-green-600">
                {formatNumber(kpiData.loyalty_kpis.total_points_redeemed)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Avg per Transaction</span>
              <span className="font-semibold text-purple-600">
                {kpiData.loyalty_kpis.avg_points_per_transaction.toFixed(1)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Redemption Rate</span>
              <span className="font-semibold text-orange-600">
                {formatPercentage((kpiData.loyalty_kpis.total_points_redeemed / kpiData.loyalty_kpis.total_points_issued) * 100)}
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* WhatsApp Performance */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">WhatsApp Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {formatNumber(kpiData.whatsapp_kpis.total_sent)}
            </div>
            <div className="text-sm text-gray-600">Messages Sent</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {formatPercentage(kpiData.whatsapp_kpis.delivery_rate)}
            </div>
            <div className="text-sm text-gray-600">Delivery Rate</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {formatPercentage(kpiData.whatsapp_kpis.read_rate)}
            </div>
            <div className="text-sm text-gray-600">Read Rate</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">
              {formatPercentage(kpiData.whatsapp_kpis.response_rate)}
            </div>
            <div className="text-sm text-gray-600">Response Rate</div>
          </div>
        </div>
      </Card>

      {/* Affiliate Performance */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Affiliate Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {formatNumber(kpiData.affiliate_kpis.total_affiliates)}
            </div>
            <div className="text-sm text-gray-600">Total Affiliates</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {formatNumber(kpiData.affiliate_kpis.successful_referrals)}
            </div>
            <div className="text-sm text-gray-600">Successful Referrals</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {formatCurrency(kpiData.affiliate_kpis.total_commissions)}
            </div>
            <div className="text-sm text-gray-600">Total Commissions</div>
          </div>
        </div>
      </Card>

      {/* Growth Trends */}
      {trendData && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Growth Trends</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-lg font-bold text-green-600">
                {trendData.growth_rates.customers >= 0 ? '+' : ''}{formatPercentage(trendData.growth_rates.customers)}
              </div>
              <div className="text-sm text-green-700">Customer Growth</div>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-lg font-bold text-blue-600">
                {trendData.growth_rates.transactions >= 0 ? '+' : ''}{formatPercentage(trendData.growth_rates.transactions)}
              </div>
              <div className="text-sm text-blue-700">Transaction Growth</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-lg font-bold text-purple-600">
                {trendData.growth_rates.redemptions >= 0 ? '+' : ''}{formatPercentage(trendData.growth_rates.redemptions)}
              </div>
              <div className="text-sm text-purple-700">Redemption Growth</div>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className="text-lg font-bold text-orange-600">
                {trendData.growth_rates.referrals >= 0 ? '+' : ''}{formatPercentage(trendData.growth_rates.referrals)}
              </div>
              <div className="text-sm text-orange-700">Referral Growth</div>
            </div>
          </div>
        </Card>
      )}

      {/* Customer Segmentation */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Customer Segmentation</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {Object.entries(kpiData.customer_kpis.segmentation).map(([key, segment]) => (
            <div key={key} className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-lg font-bold text-gray-900">{segment.count}</div>
              <div className="text-sm text-gray-600 capitalize">
                {key.replace('_', ' ')}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}

export default AnalyticsDashboard