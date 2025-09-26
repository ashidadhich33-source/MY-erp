import { useState } from 'react'
import { BarChart3, TrendingUp, FileText, Download, Calendar, Filter } from 'lucide-react'
import AnalyticsDashboard from '../components/analytics/AnalyticsDashboard'
import AnalyticsCharts from '../components/analytics/AnalyticsCharts'
import ReportsGenerator from '../components/analytics/ReportsGenerator'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'

const AnalyticsPage = () => {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [dateRange, setDateRange] = useState('30d')
  const [selectedMetric, setSelectedMetric] = useState('overview')

  const tabs = [
    { id: 'dashboard', name: 'KPI Dashboard', icon: BarChart3 },
    { id: 'charts', name: 'Interactive Charts', icon: TrendingUp },
    { id: 'reports', name: 'Reports Generator', icon: FileText },
  ]

  const metrics = [
    { id: 'overview', name: 'Overview', description: 'Overall performance metrics' },
    { id: 'customers', name: 'Customers', description: 'Customer analytics and segmentation' },
    { id: 'loyalty', name: 'Loyalty Program', description: 'Points and redemption analytics' },
    { id: 'affiliates', name: 'Affiliates', description: 'Affiliate program performance' },
    { id: 'whatsapp', name: 'WhatsApp', description: 'Messaging performance metrics' },
    { id: 'financial', name: 'Financial', description: 'ROI and cost analysis' }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics & Reporting</h1>
        <p className="mt-1 text-sm text-gray-600">
          Comprehensive analytics dashboard with KPI tracking, interactive charts, and custom report generation.
        </p>
      </div>

      {/* Quick Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4 text-center">
          <div className="text-lg font-bold text-blue-600">1,247</div>
          <div className="text-sm text-gray-600">Total Customers</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-lg font-bold text-green-600">45,670</div>
          <div className="text-sm text-gray-600">Points Issued</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-lg font-bold text-purple-600">66.7%</div>
          <div className="text-sm text-gray-600">Conversion Rate</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-lg font-bold text-orange-600">94.5%</div>
          <div className="text-sm text-gray-600">Delivery Rate</div>
        </Card>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4 mr-2" />
                {tab.name}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'dashboard' && <AnalyticsDashboard />}
        {activeTab === 'charts' && <AnalyticsCharts data={null} loading={false} />}
        {activeTab === 'reports' && <ReportsGenerator />}
      </div>

      {/* Metric Selector (for charts) */}
      {activeTab === 'charts' && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Metric to Visualize</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {metrics.map((metric) => (
              <div
                key={metric.id}
                onClick={() => setSelectedMetric(metric.id)}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                  selectedMetric === metric.id
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <h4 className="font-medium text-gray-900">{metric.name}</h4>
                <p className="text-sm text-gray-600">{metric.description}</p>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Button
            variant="outline"
            onClick={() => setActiveTab('dashboard')}
            className="justify-center"
          >
            <BarChart3 className="h-4 w-4 mr-2" />
            View Dashboard
          </Button>
          <Button
            variant="outline"
            onClick={() => setActiveTab('charts')}
            className="justify-center"
          >
            <TrendingUp className="h-4 w-4 mr-2" />
            View Charts
          </Button>
          <Button
            variant="outline"
            onClick={() => setActiveTab('reports')}
            className="justify-center"
          >
            <FileText className="h-4 w-4 mr-2" />
            Generate Report
          </Button>
          <Button
            variant="outline"
            onClick={() => {
              // Export current view
              alert('Export functionality would be implemented here')
            }}
            className="justify-center"
          >
            <Download className="h-4 w-4 mr-2" />
            Export Data
          </Button>
        </div>
      </Card>

      {/* Analytics Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Features</h3>
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-blue-600 text-sm">📊</span>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Real-time KPIs</h4>
                <p className="text-sm text-gray-600">
                  Live dashboard with key performance indicators updated in real-time
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-green-600 text-sm">📈</span>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Interactive Charts</h4>
                <p className="text-sm text-gray-600">
                  Dynamic charts with zoom, pan, and drill-down capabilities
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-purple-600 text-sm">📋</span>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Custom Reports</h4>
                <p className="text-sm text-gray-600">
                  Generate tailored reports with custom date ranges and filters
                </p>
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Export Options</h3>
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-orange-600 text-sm">📄</span>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">CSV Export</h4>
                <p className="text-sm text-gray-600">
                  Export data in CSV format for spreadsheet analysis
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-blue-600 text-sm">📦</span>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">JSON Export</h4>
                <p className="text-sm text-gray-600">
                  Export structured data in JSON format for API integration
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-green-600 text-sm">📊</span>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">PDF Reports</h4>
                <p className="text-sm text-gray-600">
                  Generate formatted PDF reports for presentations and sharing
                </p>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Analytics Tips */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Analytics Tips</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">Monitor Key Metrics</h4>
            <p className="text-sm text-blue-800">
              Keep track of customer retention rates, conversion rates, and engagement scores
              to identify areas for improvement.
            </p>
          </div>

          <div className="p-4 bg-green-50 rounded-lg">
            <h4 className="font-medium text-green-900 mb-2">Analyze Trends</h4>
            <p className="text-sm text-green-800">
              Look for patterns in customer behavior, seasonal trends, and the impact
              of marketing campaigns on your metrics.
            </p>
          </div>

          <div className="p-4 bg-purple-50 rounded-lg">
            <h4 className="font-medium text-purple-900 mb-2">Segment Your Data</h4>
            <p className="text-sm text-purple-800">
              Use customer segmentation to target specific groups with personalized
              offers and communications.
            </p>
          </div>

          <div className="p-4 bg-orange-50 rounded-lg">
            <h4 className="font-medium text-orange-900 mb-2">Track ROI</h4>
            <p className="text-sm text-orange-800">
              Monitor the return on investment for your loyalty program, affiliate
              campaigns, and marketing spend.
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default AnalyticsPage