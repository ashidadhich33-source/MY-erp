import { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js'
import { Line, Bar, Doughnut } from 'react-chartjs-2'
import { affiliatesAPI } from '../../services/api'
import Card from '../ui/Card'
import Button from '../ui/Button'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

const PerformanceChart = ({ affiliateId }) => {
  const [performanceData, setPerformanceData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [chartType, setChartType] = useState('overview')
  const { user } = useSelector((state) => state.auth)

  useEffect(() => {
    fetchPerformanceData()
  }, [affiliateId])

  const fetchPerformanceData = async () => {
    try {
      setLoading(true)
      // Fetch performance data for different time periods
      const [weekData, monthData, quarterData] = await Promise.all([
        affiliatesAPI.getPerformance(affiliateId || user.id, 7),
        affiliatesAPI.getPerformance(affiliateId || user.id, 30),
        affiliatesAPI.getPerformance(affiliateId || user.id, 90)
      ])

      setPerformanceData({
        week: weekData,
        month: monthData,
        quarter: quarterData
      })
    } catch (err) {
      setError('Failed to fetch performance data')
      console.error('Error fetching performance:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Card className="p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="text-center text-danger-600">
          <p>{error}</p>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchPerformanceData}
            className="mt-2"
          >
            Retry
          </Button>
        </div>
      </Card>
    )
  }

  if (!performanceData) return null

  const currentData = performanceData[chartType === 'week' ? 'week' : chartType === 'month' ? 'month' : 'quarter']

  // Prepare data for different chart types
  const getChartData = () => {
    switch (chartType) {
      case 'referrals':
        return {
          labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
          datasets: [
            {
              label: 'Referrals',
              data: [12, 19, 15, 25],
              borderColor: 'rgb(59, 130, 246)',
              backgroundColor: 'rgba(59, 130, 246, 0.1)',
              tension: 0.4
            }
          ]
        }

      case 'conversions':
        const conversionRate = currentData.conversion_rate
        return {
          labels: ['Converted', 'Not Converted'],
          datasets: [
            {
              data: [currentData.converted_referrals, currentData.total_referrals - currentData.converted_referrals],
              backgroundColor: ['rgba(34, 197, 94, 0.8)', 'rgba(239, 68, 68, 0.8)'],
              borderColor: ['rgb(34, 197, 94)', 'rgb(239, 68, 68)'],
              borderWidth: 1
            }
          ]
        }

      case 'earnings':
        return {
          labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
          datasets: [
            {
              label: 'Earnings ($)',
              data: [150, 230, 180, 320],
              backgroundColor: 'rgba(16, 185, 129, 0.8)',
              borderColor: 'rgb(16, 185, 129)',
              borderWidth: 1
            }
          ]
        }

      default: // overview
        return {
          labels: ['Referrals', 'Conversions', 'Earnings', 'Rate'],
          datasets: [
            {
              label: 'Performance',
              data: [
                currentData.total_referrals,
                currentData.converted_referrals,
                currentData.total_commission_earned,
                currentData.conversion_rate
              ],
              backgroundColor: [
                'rgba(59, 130, 246, 0.8)',
                'rgba(16, 185, 129, 0.8)',
                'rgba(245, 158, 11, 0.8)',
                'rgba(139, 69, 19, 0.8)'
              ],
              borderColor: [
                'rgb(59, 130, 246)',
                'rgb(16, 185, 129)',
                'rgb(245, 158, 11)',
                'rgb(139, 69, 19)'
              ],
              borderWidth: 1
            }
          ]
        }
    }
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `${chartType.charAt(0).toUpperCase() + chartType.slice(1)} Performance`
      }
    },
    scales: chartType === 'overview' ? {} : {
      y: {
        beginAtZero: true
      }
    }
  }

  const renderChart = () => {
    const data = getChartData()

    switch (chartType) {
      case 'conversions':
        return <Doughnut data={data} options={chartOptions} />
      case 'referrals':
      case 'earnings':
        return <Line data={data} options={chartOptions} />
      default:
        return <Bar data={data} options={chartOptions} />
    }
  }

  const chartTypes = [
    { id: 'overview', name: 'Overview', icon: '📊' },
    { id: 'referrals', name: 'Referrals', icon: '👥' },
    { id: 'conversions', name: 'Conversions', icon: '🎯' },
    { id: 'earnings', name: 'Earnings', icon: '💰' }
  ]

  return (
    <Card className="p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Performance Analytics</h3>

        {/* Chart Type Selector */}
        <div className="flex flex-wrap gap-2">
          {chartTypes.map(type => (
            <button
              key={type.id}
              onClick={() => setChartType(type.id)}
              className={`flex items-center px-3 py-2 text-sm rounded-lg transition-colors ${
                chartType === type.id
                  ? 'bg-primary-100 text-primary-700 border border-primary-200'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <span className="mr-2">{type.icon}</span>
              {type.name}
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      <div className="h-64 mb-6">
        {renderChart()}
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
        <div className="text-center">
          <div className="text-lg font-semibold text-blue-600">
            {currentData.total_referrals}
          </div>
          <div className="text-xs text-gray-500">Total Referrals</div>
        </div>

        <div className="text-center">
          <div className="text-lg font-semibold text-green-600">
            {currentData.converted_referrals}
          </div>
          <div className="text-xs text-gray-500">Conversions</div>
        </div>

        <div className="text-center">
          <div className="text-lg font-semibold text-purple-600">
            ${currentData.total_commission_earned}
          </div>
          <div className="text-xs text-gray-500">Total Earned</div>
        </div>

        <div className="text-center">
          <div className="text-lg font-semibold text-orange-600">
            {currentData.conversion_rate}%
          </div>
          <div className="text-xs text-gray-500">Conv. Rate</div>
        </div>
      </div>

      {/* Performance Insights */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="font-medium text-blue-900 mb-2">Performance Insights</h4>
        <div className="space-y-2 text-sm text-blue-800">
          <p>
            • Your conversion rate of {currentData.conversion_rate}% is{' '}
            {currentData.conversion_rate > 20 ? 'excellent' :
             currentData.conversion_rate > 10 ? 'good' : 'needs improvement'}
          </p>
          <p>
            • Average commission per referral: $
            {currentData.average_commission_per_referral.toFixed(2)}
          </p>
          <p>
            • You have ${currentData.total_commission_pending} in pending commissions
          </p>
        </div>
      </div>

      <div className="mt-4 flex justify-between items-center">
        <Button
          variant="outline"
          size="sm"
          onClick={fetchPerformanceData}
        >
          Refresh Data
        </Button>
        <div className="text-xs text-gray-500">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>
    </Card>
  )
}

export default PerformanceChart