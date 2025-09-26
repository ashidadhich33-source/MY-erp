import { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import {
  TrendingUp,
  Users,
  DollarSign,
  Target,
  ExternalLink,
  Copy,
  Share2,
  Calendar
} from 'lucide-react'
import { affiliatesAPI } from '../../services/api'
import Card from '../ui/Card'
import Button from '../ui/Button'

const AffiliateDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const { user } = useSelector((state) => state.auth)

  useEffect(() => {
    fetchDashboardData()
  }, [user.id])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      const response = await affiliatesAPI.getDashboard(user.id)
      setDashboardData(response)
    } catch (err) {
      setError('Failed to fetch dashboard data')
      console.error('Error fetching dashboard:', err)
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    // You could add a toast notification here
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <Card className="p-6">
          <div className="animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="h-20 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </Card>
      </div>
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
            onClick={fetchDashboardData}
            className="mt-2"
          >
            Retry
          </Button>
        </div>
      </Card>
    )
  }

  if (!dashboardData) return null

  const { affiliate, performance, recent_referrals, recent_commissions, summary_stats } = dashboardData

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Affiliate Dashboard</h1>
          <p className="text-gray-600">
            Track your performance and manage your affiliate account
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">Affiliate Code</p>
          <div className="flex items-center space-x-2">
            <code className="bg-gray-100 px-2 py-1 rounded text-sm font-mono">
              {affiliate.affiliate_code}
            </code>
            <Button
              variant="outline"
              size="sm"
              onClick={() => copyToClipboard(affiliate.affiliate_code)}
            >
              <Copy className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center">
            <Users className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Total Referrals</p>
              <p className="text-2xl font-bold text-gray-900">{summary_stats.total_referrals}</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center">
            <Target className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Conversion Rate</p>
              <p className="text-2xl font-bold text-gray-900">{summary_stats.conversion_rate}%</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-purple-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Total Earnings</p>
              <p className="text-2xl font-bold text-gray-900">${affiliate.total_earnings}</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-orange-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Unpaid Balance</p>
              <p className="text-2xl font-bold text-gray-900">${affiliate.unpaid_balance}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Referral Link */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Referral Link</h3>
        <div className="flex items-center space-x-3">
          <div className="flex-1">
            <div className="flex items-center bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
              <span className="text-gray-700">{affiliate.referral_link}</span>
            </div>
          </div>
          <Button
            variant="outline"
            onClick={() => copyToClipboard(affiliate.referral_link)}
          >
            <Copy className="h-4 w-4 mr-2" />
            Copy
          </Button>
          <Button
            onClick={() => window.open(affiliate.referral_link, '_blank')}
          >
            <ExternalLink className="h-4 w-4 mr-2" />
            Visit
          </Button>
          <Button
            onClick={() => {
              if (navigator.share) {
                navigator.share({
                  title: 'Join our affiliate program',
                  text: 'Check out this amazing affiliate program!',
                  url: affiliate.referral_link
                })
              }
            }}
          >
            <Share2 className="h-4 w-4 mr-2" />
            Share
          </Button>
        </div>
        <p className="text-sm text-gray-500 mt-2">
          Share this link to earn commissions when people sign up through your referral
        </p>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Referrals */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Referrals</h3>
          {recent_referrals.length === 0 ? (
            <div className="text-center py-8">
              <Users className="h-12 w-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-500">No referrals yet</p>
              <p className="text-sm text-gray-400">Start sharing your referral link to see results</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recent_referrals.slice(0, 5).map(referral => (
                <div key={referral.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">Customer #{referral.customer_id}</p>
                    <p className="text-sm text-gray-600 capitalize">{referral.referral_source.replace('_', ' ')}</p>
                  </div>
                  <div className="text-right">
                    {referral.conversion_value > 0 ? (
                      <p className="font-medium text-green-600">${referral.conversion_value}</p>
                    ) : (
                      <p className="text-sm text-gray-500">Pending</p>
                    )}
                    <p className="text-xs text-gray-400">{new Date(referral.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Recent Commissions */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Commissions</h3>
          {recent_commissions.length === 0 ? (
            <div className="text-center py-8">
              <DollarSign className="h-12 w-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-500">No commissions yet</p>
              <p className="text-sm text-gray-400">Commissions appear when referrals make purchases</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recent_commissions.slice(0, 5).map(commission => (
                <div key={commission.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">${commission.commission_amount}</p>
                    <p className="text-sm text-gray-600">{commission.description}</p>
                  </div>
                  <div className="text-right">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      commission.status === 'approved' ? 'bg-green-100 text-green-800' :
                      commission.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {commission.status}
                    </span>
                    <p className="text-xs text-gray-400 mt-1">
                      {new Date(commission.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* Performance Summary */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{performance.this_month.total_referrals}</div>
            <p className="text-sm text-gray-600">Referrals This Month</p>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">${performance.this_month.total_commission_earned}</div>
            <p className="text-sm text-gray-600">Earned This Month</p>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{performance.current_tier}</div>
            <p className="text-sm text-gray-600">Current Tier</p>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default AffiliateDashboard