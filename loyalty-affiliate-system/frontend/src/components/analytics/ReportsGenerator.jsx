import { useState, useEffect } from 'react'
import { FileText, Download, Calendar, Filter, BarChart3, Users, Target, MessageCircle } from 'lucide-react'
import { analyticsAPI } from '../../services/api'
import Card from '../ui/Card'
import Button from '../ui/Button'

const ReportsGenerator = () => {
  const [reportType, setReportType] = useState('customer')
  const [dateRange, setDateRange] = useState('30d')
  const [loading, setLoading] = useState(false)
  const [reportData, setReportData] = useState(null)
  const [availableReports, setAvailableReports] = useState([])
  const [filters, setFilters] = useState({})

  const reportTypes = [
    {
      id: 'customer',
      name: 'Customer Analytics Report',
      description: 'Detailed customer behavior, segmentation, and engagement metrics',
      icon: Users,
      color: 'blue'
    },
    {
      id: 'loyalty',
      name: 'Loyalty Program Report',
      description: 'Points activity, redemption patterns, and program performance',
      icon: Target,
      color: 'green'
    },
    {
      id: 'affiliate',
      name: 'Affiliate Program Report',
      description: 'Referral tracking, commission analysis, and affiliate performance',
      icon: BarChart3,
      color: 'purple'
    },
    {
      id: 'whatsapp',
      name: 'WhatsApp Messaging Report',
      description: 'Message delivery rates, engagement metrics, and automation performance',
      icon: MessageCircle,
      color: 'teal'
    },
    {
      id: 'financial',
      name: 'Financial Performance Report',
      description: 'ROI analysis, cost breakdown, and revenue impact assessment',
      icon: FileText,
      color: 'orange'
    }
  ]

  const dateRanges = [
    { id: '7d', name: 'Last 7 days', days: 7 },
    { id: '30d', name: 'Last 30 days', days: 30 },
    { id: '90d', name: 'Last 90 days', days: 90 },
    { id: '1y', name: 'Last year', days: 365 },
    { id: 'custom', name: 'Custom range', days: null }
  ]

  useEffect(() => {
    generateReport()
  }, [reportType, dateRange])

  const generateReport = async () => {
    try {
      setLoading(true)

      // Calculate date range
      const endDate = new Date()
      let startDate = new Date()

      if (dateRange === 'custom') {
        // Use default to last 30 days for custom
        startDate.setDate(endDate.getDate() - 30)
      } else {
        const range = dateRanges.find(r => r.id === dateRange)
        startDate.setDate(endDate.getDate() - range.days)
      }

      const parameters = {
        report_type: reportType,
        date_from: startDate.toISOString().split('T')[0],
        date_to: endDate.toISOString().split('T')[0],
        ...filters
      }

      const response = await analyticsAPI.generateReport(parameters)
      setReportData(response)
    } catch (err) {
      console.error('Error generating report:', err)
      setReportData(null)
    } finally {
      setLoading(false)
    }
  }

  const exportReport = async (format) => {
    try {
      const parameters = {
        export_type: reportType,
        date_from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        date_to: new Date().toISOString().split('T')[0],
        format: format,
        ...filters
      }

      const response = await analyticsAPI.exportData(parameters)

      // Create and download file
      const blob = new Blob([JSON.stringify(response.data, null, 2)], {
        type: 'application/json'
      })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${reportType}_report_${new Date().toISOString().split('T')[0]}.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Error exporting report:', err)
      alert('Failed to export report. Please try again.')
    }
  }

  const handleFilterChange = (filterKey, value) => {
    setFilters(prev => ({
      ...prev,
      [filterKey]: value
    }))
  }

  const getReportIcon = (type) => {
    const report = reportTypes.find(r => r.id === type)
    return report ? report.icon : FileText
  }

  const getReportColor = (type) => {
    const report = reportTypes.find(r => r.id === type)
    return report ? report.color : 'gray'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Reports Generator</h2>
          <p className="text-gray-600">
            Generate custom reports and export data for analysis
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={() => exportReport('csv')}
          >
            <Download className="h-4 w-4 mr-2" />
            Export CSV
          </Button>
          <Button
            variant="outline"
            onClick={() => exportReport('json')}
          >
            <Download className="h-4 w-4 mr-2" />
            Export JSON
          </Button>
        </div>
      </div>

      {/* Report Type Selection */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Report Type</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reportTypes.map((report) => {
            const Icon = report.icon
            return (
              <div
                key={report.id}
                onClick={() => setReportType(report.id)}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                  reportType === report.id
                    ? `border-${report.color}-500 bg-${report.color}-50`
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-10 h-10 bg-${report.color}-100 rounded-full flex items-center justify-center`}>
                    <Icon className={`h-5 w-5 text-${report.color}-600`} />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">{report.name}</h4>
                    <p className="text-sm text-gray-600">{report.description}</p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </Card>

      {/* Date Range and Filters */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Report Configuration</h3>
          <Button
            onClick={generateReport}
            loading={loading}
            disabled={loading}
          >
            {loading ? 'Generating...' : 'Generate Report'}
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Date Range */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Date Range
            </label>
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {dateRanges.map((range) => (
                <option key={range.id} value={range.id}>
                  {range.name}
                </option>
              ))}
            </select>
          </div>

          {/* Report-specific filters */}
          {reportType === 'customer' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Customer Tier
              </label>
              <select
                value={filters.tier || 'all'}
                onChange={(e) => handleFilterChange('tier', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">All Tiers</option>
                <option value="bronze">Bronze</option>
                <option value="silver">Silver</option>
                <option value="gold">Gold</option>
                <option value="platinum">Platinum</option>
              </select>
            </div>
          )}

          {reportType === 'loyalty' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Transaction Type
              </label>
              <select
                value={filters.transaction_type || 'all'}
                onChange={(e) => handleFilterChange('transaction_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">All Types</option>
                <option value="earned">Points Earned</option>
                <option value="spent">Points Spent</option>
                <option value="transferred">Points Transferred</option>
              </select>
            </div>
          )}

          {reportType === 'affiliate' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Affiliate Status
              </label>
              <select
                value={filters.affiliate_status || 'all'}
                onChange={(e) => handleFilterChange('affiliate_status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="pending">Pending</option>
              </select>
            </div>
          )}
        </div>
      </Card>

      {/* Report Preview */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Report Preview</h3>
          <div className="flex items-center space-x-2">
            <Calendar className="h-4 w-4 text-gray-400" />
            <span className="text-sm text-gray-600">
              Generated: {new Date().toLocaleDateString()}
            </span>
          </div>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            <span className="ml-3 text-gray-600">Generating report...</span>
          </div>
        )}

        {!loading && !reportData && (
          <div className="text-center py-12">
            <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Report Generated</h3>
            <p className="text-gray-600 mb-4">
              Click "Generate Report" to create your {reportTypes.find(r => r.id === reportType)?.name}
            </p>
            <Button onClick={generateReport}>
              Generate Report
            </Button>
          </div>
        )}

        {!loading && reportData && (
          <div className="space-y-6">
            {/* Report Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {reportData.summary.total_customers || reportData.summary.total_points_issued || reportData.summary.total_affiliates || 'N/A'}
                </div>
                <div className="text-sm text-blue-700">
                  {reportType === 'customer' ? 'Total Customers' :
                   reportType === 'loyalty' ? 'Points Issued' :
                   reportType === 'affiliate' ? 'Total Affiliates' : 'Key Metric'}
                </div>
              </div>

              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {reportData.summary.active_customers || reportData.summary.total_points_redeemed || reportData.summary.conversion_rate || 'N/A'}
                </div>
                <div className="text-sm text-green-700">
                  {reportType === 'customer' ? 'Active Customers' :
                   reportType === 'loyalty' ? 'Points Redeemed' :
                   reportType === 'affiliate' ? 'Conversion Rate' : 'Secondary Metric'}
                </div>
              </div>

              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {reportData.summary.retention_rate || reportData.summary.total_commissions || reportData.summary.delivery_rate || 'N/A'}
                </div>
                <div className="text-sm text-purple-700">
                  {reportType === 'customer' ? 'Retention Rate' :
                   reportType === 'affiliate' ? 'Total Commissions' :
                   reportType === 'whatsapp' ? 'Delivery Rate' : 'Tertiary Metric'}
                </div>
              </div>
            </div>

            {/* Report Details */}
            {reportData.details && (
              <div className="mt-6">
                <h4 className="font-medium text-gray-900 mb-3">Detailed Breakdown</h4>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          {reportType === 'customer' ? 'Tier' :
                           reportType === 'loyalty' ? 'Transaction Type' :
                           reportType === 'affiliate' ? 'Affiliate' : 'Category'}
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Count
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Total
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Average
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {reportData.details.map((item, index) => (
                        <tr key={index}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {item.name || item.tier || item.type || 'N/A'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {item.count || item.total_redeemed || 'N/A'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {item.total_points || item.total_earnings || item.total_sent || 'N/A'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {item.avg_points || item.avg_earnings || 'N/A'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </Card>

      {/* Report Templates */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Report Templates</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-4 border border-gray-200 rounded-lg">
            <h4 className="font-medium text-gray-900">Monthly Performance</h4>
            <p className="text-sm text-gray-600 mb-3">Complete monthly business performance report</p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setReportType('customer')
                setDateRange('30d')
                generateReport()
              }}
            >
              Generate
            </Button>
          </div>

          <div className="p-4 border border-gray-200 rounded-lg">
            <h4 className="font-medium text-gray-900">Quarterly Review</h4>
            <p className="text-sm text-gray-600 mb-3">Quarterly business review with trends</p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setReportType('financial')
                setDateRange('90d')
                generateReport()
              }}
            >
              Generate
            </Button>
          </div>

          <div className="p-4 border border-gray-200 rounded-lg">
            <h4 className="font-medium text-gray-900">Campaign Analysis</h4>
            <p className="text-sm text-gray-600 mb-3">Marketing campaign performance analysis</p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setReportType('whatsapp')
                setDateRange('30d')
                generateReport()
              }}
            >
              Generate
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default ReportsGenerator