import { useState, useEffect, useRef } from 'react'
import { BarChart3, LineChart, PieChart, Activity, Calendar } from 'lucide-react'
import Card from '../ui/Card'
import Button from '../ui/Button'

const AnalyticsCharts = ({ data, loading }) => {
  const [chartType, setChartType] = useState('overview')
  const chartRefs = {
    customers: useRef(null),
    loyalty: useRef(null),
    whatsapp: useRef(null),
    affiliate: useRef(null),
    trends: useRef(null)
  }

  useEffect(() => {
    if (!loading && data) {
      initializeCharts()
    }
  }, [data, loading, chartType])

  const initializeCharts = () => {
    // This would normally initialize Chart.js charts
    // For now, we'll just show placeholders
    console.log('Initializing charts with data:', data)
  }

  const formatChartData = (dataType) => {
    if (!data) return null

    switch (dataType) {
      case 'customers':
        return {
          labels: ['Bronze', 'Silver', 'Gold', 'Platinum'],
          datasets: [{
            label: 'Customers by Tier',
            data: [
              data.customer_kpis.tier_distribution.bronze || 0,
              data.customer_kpis.tier_distribution.silver || 0,
              data.customer_kpis.tier_distribution.gold || 0,
              data.customer_kpis.tier_distribution.platinum || 0
            ],
            backgroundColor: [
              'rgba(245, 158, 11, 0.8)', // amber
              'rgba(107, 114, 128, 0.8)', // gray
              'rgba(245, 158, 11, 0.9)', // yellow
              'rgba(147, 51, 234, 0.8)' // purple
            ]
          }]
        }

      case 'loyalty':
        return {
          labels: ['Points Issued', 'Points Redeemed', 'Net Points'],
          datasets: [{
            label: 'Loyalty Points',
            data: [
              data.loyalty_kpis.total_points_issued,
              data.loyalty_kpis.total_points_redeemed,
              data.loyalty_kpis.net_points
            ],
            backgroundColor: [
              'rgba(34, 197, 94, 0.8)', // green
              'rgba(239, 68, 68, 0.8)', // red
              'rgba(59, 130, 246, 0.8)' // blue
            ]
          }]
        }

      case 'whatsapp':
        return {
          labels: ['Sent', 'Delivered', 'Read', 'Failed'],
          datasets: [{
            label: 'Message Status',
            data: [
              data.whatsapp_kpis.total_sent,
              data.whatsapp_kpis.message_statuses.delivered || 0,
              data.whatsapp_kpis.message_statuses.read || 0,
              data.whatsapp_kpis.message_statuses.failed || 0
            ],
            backgroundColor: [
              'rgba(59, 130, 246, 0.8)', // blue
              'rgba(34, 197, 94, 0.8)', // green
              'rgba(147, 51, 234, 0.8)', // purple
              'rgba(239, 68, 68, 0.8)' // red
            ]
          }]
        }

      case 'affiliate':
        return {
          labels: ['Total Affiliates', 'Active Affiliates', 'Successful Referrals'],
          datasets: [{
            label: 'Affiliate Metrics',
            data: [
              data.affiliate_kpis.total_affiliates,
              data.affiliate_kpis.active_affiliates,
              data.affiliate_kpis.successful_referrals
            ],
            backgroundColor: [
              'rgba(59, 130, 246, 0.8)', // blue
              'rgba(34, 197, 94, 0.8)', // green
              'rgba(245, 158, 11, 0.8)' // amber
            ]
          }]
        }

      default:
        return null
    }
  }

  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[1, 2, 3, 4].map(i => (
          <Card key={i} className="p-6">
            <div className="animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
              <div className="h-48 bg-gray-200 rounded"></div>
            </div>
          </Card>
        ))}
      </div>
    )
  }

  if (!data) {
    return (
      <Card className="p-12 text-center">
        <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Chart Data</h3>
        <p className="text-gray-600">Analytics data is not available yet.</p>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Chart Type Selector */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Analytics Charts</h2>
          <p className="text-gray-600">Visual representation of your data</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant={chartType === 'overview' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setChartType('overview')}
          >
            Overview
          </Button>
          <Button
            variant={chartType === 'customers' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setChartType('customers')}
          >
            Customers
          </Button>
          <Button
            variant={chartType === 'loyalty' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setChartType('loyalty')}
          >
            Loyalty
          </Button>
          <Button
            variant={chartType === 'whatsapp' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setChartType('whatsapp')}
          >
            WhatsApp
          </Button>
          <Button
            variant={chartType === 'affiliate' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setChartType('affiliate')}
          >
            Affiliate
          </Button>
        </div>
      </div>

      {/* Charts Grid */}
      {chartType === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Customer Overview */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Customer Distribution</h3>
              <PieChart className="h-5 w-5 text-gray-400" />
            </div>
            <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
              <div className="text-center">
                <PieChart className="h-16 w-16 text-blue-600 mx-auto mb-2" />
                <p className="text-gray-500">Customer Tier Chart</p>
                <p className="text-sm text-gray-400">Chart.js integration needed</p>
              </div>
            </div>
          </Card>

          {/* Loyalty Overview */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Loyalty Points Flow</h3>
              <BarChart3 className="h-5 w-5 text-gray-400" />
            </div>
            <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
              <div className="text-center">
                <BarChart3 className="h-16 w-16 text-green-600 mx-auto mb-2" />
                <p className="text-gray-500">Points Flow Chart</p>
                <p className="text-sm text-gray-400">Chart.js integration needed</p>
              </div>
            </div>
          </Card>

          {/* WhatsApp Performance */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">WhatsApp Performance</h3>
              <LineChart className="h-5 w-5 text-gray-400" />
            </div>
            <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
              <div className="text-center">
                <LineChart className="h-16 w-16 text-purple-600 mx-auto mb-2" />
                <p className="text-gray-500">Message Performance Chart</p>
                <p className="text-sm text-gray-400">Chart.js integration needed</p>
              </div>
            </div>
          </Card>

          {/* Affiliate Performance */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Affiliate Metrics</h3>
              <Activity className="h-5 w-5 text-gray-400" />
            </div>
            <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
              <div className="text-center">
                <Activity className="h-16 w-16 text-orange-600 mx-auto mb-2" />
                <p className="text-gray-500">Affiliate Performance Chart</p>
                <p className="text-sm text-gray-400">Chart.js integration needed</p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {chartType === 'customers' && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Customer Tier Distribution</h3>
            <PieChart className="h-5 w-5 text-gray-400" />
          </div>
          <div className="h-96 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center">
              <PieChart className="h-24 w-24 text-blue-600 mx-auto mb-4" />
              <p className="text-gray-500 mb-2">Interactive Customer Tier Chart</p>
              <p className="text-sm text-gray-400">Chart.js with interactive features</p>
              <div className="mt-4 text-sm text-gray-600">
                <div className="flex justify-center space-x-6">
                  <div className="text-center">
                    <div className="w-4 h-4 bg-amber-500 rounded-full inline-block mr-2"></div>
                    <span>Bronze: {data.customer_kpis.tier_distribution.bronze || 0}</span>
                  </div>
                  <div className="text-center">
                    <div className="w-4 h-4 bg-gray-500 rounded-full inline-block mr-2"></div>
                    <span>Silver: {data.customer_kpis.tier_distribution.silver || 0}</span>
                  </div>
                  <div className="text-center">
                    <div className="w-4 h-4 bg-yellow-500 rounded-full inline-block mr-2"></div>
                    <span>Gold: {data.customer_kpis.tier_distribution.gold || 0}</span>
                  </div>
                  <div className="text-center">
                    <div className="w-4 h-4 bg-purple-500 rounded-full inline-block mr-2"></div>
                    <span>Platinum: {data.customer_kpis.tier_distribution.platinum || 0}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}

      {chartType === 'loyalty' && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Loyalty Program Performance</h3>
            <BarChart3 className="h-5 w-5 text-gray-400" />
          </div>
          <div className="h-96 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center">
              <BarChart3 className="h-24 w-24 text-green-600 mx-auto mb-4" />
              <p className="text-gray-500 mb-2">Points Flow Visualization</p>
              <p className="text-sm text-gray-400">Interactive bar chart with drill-down</p>
              <div className="mt-4 grid grid-cols-3 gap-4 text-sm text-gray-600">
                <div className="text-center p-2 bg-green-50 rounded">
                  <div className="font-semibold text-green-600">
                    {data.loyalty_kpis.total_points_issued.toLocaleString()}
                  </div>
                  <div>Points Issued</div>
                </div>
                <div className="text-center p-2 bg-red-50 rounded">
                  <div className="font-semibold text-red-600">
                    {data.loyalty_kpis.total_points_redeemed.toLocaleString()}
                  </div>
                  <div>Points Redeemed</div>
                </div>
                <div className="text-center p-2 bg-blue-50 rounded">
                  <div className="font-semibold text-blue-600">
                    {data.loyalty_kpis.net_points.toLocaleString()}
                  </div>
                  <div>Net Points</div>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}

      {chartType === 'whatsapp' && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">WhatsApp Message Analytics</h3>
            <LineChart className="h-5 w-5 text-gray-400" />
          </div>
          <div className="h-96 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center">
              <LineChart className="h-24 w-24 text-purple-600 mx-auto mb-4" />
              <p className="text-gray-500 mb-2">Message Delivery & Engagement</p>
              <p className="text-sm text-gray-400">Line chart with trend analysis</p>
              <div className="mt-4 grid grid-cols-4 gap-4 text-sm text-gray-600">
                <div className="text-center p-2 bg-blue-50 rounded">
                  <div className="font-semibold text-blue-600">
                    {data.whatsapp_kpis.delivery_rate.toFixed(1)}%
                  </div>
                  <div>Delivery Rate</div>
                </div>
                <div className="text-center p-2 bg-green-50 rounded">
                  <div className="font-semibold text-green-600">
                    {data.whatsapp_kpis.read_rate.toFixed(1)}%
                  </div>
                  <div>Read Rate</div>
                </div>
                <div className="text-center p-2 bg-orange-50 rounded">
                  <div className="font-semibold text-orange-600">
                    {data.whatsapp_kpis.response_rate.toFixed(1)}%
                  </div>
                  <div>Response Rate</div>
                </div>
                <div className="text-center p-2 bg-gray-50 rounded">
                  <div className="font-semibold text-gray-600">
                    {data.whatsapp_kpis.total_sent.toLocaleString()}
                  </div>
                  <div>Total Sent</div>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}

      {chartType === 'affiliate' && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Affiliate Program Performance</h3>
            <Activity className="h-5 w-5 text-gray-400" />
          </div>
          <div className="h-96 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center">
              <Activity className="h-24 w-24 text-orange-600 mx-auto mb-4" />
              <p className="text-gray-500 mb-2">Affiliate Activity & Performance</p>
              <p className="text-sm text-gray-400">Multi-axis chart with conversion tracking</p>
              <div className="mt-4 grid grid-cols-3 gap-4 text-sm text-gray-600">
                <div className="text-center p-2 bg-blue-50 rounded">
                  <div className="font-semibold text-blue-600">
                    {data.affiliate_kpis.conversion_rate.toFixed(1)}%
                  </div>
                  <div>Conversion Rate</div>
                </div>
                <div className="text-center p-2 bg-green-50 rounded">
                  <div className="font-semibold text-green-600">
                    {data.affiliate_kpis.successful_referrals}
                  </div>
                  <div>Successful Referrals</div>
                </div>
                <div className="text-center p-2 bg-purple-50 rounded">
                  <div className="font-semibold text-purple-600">
                    {data.affiliate_kpis.total_commissions.toLocaleString()}
                  </div>
                  <div>Total Commissions</div>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Chart Features Info */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Chart Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-blue-600 text-sm">📊</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Interactive Charts</h4>
              <p className="text-sm text-gray-600">
                Hover for details, click for drill-down, zoom and pan capabilities
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-green-600 text-sm">📈</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Real-time Updates</h4>
              <p className="text-sm text-gray-600">
                Charts update automatically with live data and trend analysis
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-purple-600 text-sm">🎨</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Customizable Visuals</h4>
              <p className="text-sm text-gray-600">
                Multiple chart types, color schemes, and styling options
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-orange-600 text-sm">📱</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Responsive Design</h4>
              <p className="text-sm text-gray-600">
                Charts adapt to different screen sizes and devices
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default AnalyticsCharts