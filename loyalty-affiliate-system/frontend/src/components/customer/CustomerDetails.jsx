import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Edit, User, Phone, Mail, Calendar, Trophy, Activity,
  TrendingUp, Users, Gift, History, BarChart3, PieChart, Target
} from 'lucide-react'
import { customersAPI } from '../../services/api'
import Card from '../ui/Card'
import Button from '../ui/Button'

const CustomerDetails = () => {
  const { customerId } = useParams()
  const navigate = useNavigate()
  const [customer, setCustomer] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [recentTransactions, setRecentTransactions] = useState([])
  const [recentRedemptions, setRecentRedemptions] = useState([])
  const [kids, setKids] = useState([])
  const [tierHistory, setTierHistory] = useState([])
  const [timeline, setTimeline] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    fetchCustomerData()
  }, [customerId])

  const fetchCustomerData = async () => {
    try {
      setLoading(true)
      const response = await customersAPI.getById(customerId)
      setCustomer(response.customer)
      setAnalytics(response.analytics)
      setRecentTransactions(response.recent_transactions)
      setRecentRedemptions(response.recent_redemptions)
      setKids(response.kids)
      setTierHistory(response.tier_history)

      // Fetch timeline separately
      const timelineResponse = await customersAPI.getTimeline(customerId)
      setTimeline(timelineResponse.activities)
    } catch (err) {
      setError('Failed to fetch customer data')
      console.error('Error fetching customer:', err)
    } finally {
      setLoading(false)
    }
  }

  const getTierColor = (tier) => {
    switch (tier) {
      case 'bronze': return 'bg-amber-100 text-amber-800'
      case 'silver': return 'bg-gray-100 text-gray-800'
      case 'gold': return 'bg-yellow-100 text-yellow-800'
      case 'platinum': return 'bg-purple-100 text-purple-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'inactive': return 'bg-gray-100 text-gray-800'
      case 'suspended': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString() + ' ' +
           new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const getActivityIcon = (type) => {
    switch (type) {
      case 'transaction': return <TrendingUp className="h-4 w-4 text-blue-600" />
      case 'redemption': return <Gift className="h-4 w-4 text-purple-600" />
      case 'tier_change': return <Trophy className="h-4 w-4 text-yellow-600" />
      default: return <Activity className="h-4 w-4 text-gray-600" />
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2 space-y-6">
              <div className="h-32 bg-gray-200 rounded"></div>
              <div className="h-64 bg-gray-200 rounded"></div>
            </div>
            <div className="space-y-6">
              <div className="h-48 bg-gray-200 rounded"></div>
              <div className="h-32 bg-gray-200 rounded"></div>
            </div>
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
        <Button onClick={() => navigate('/customers')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Customers
        </Button>
      </div>
    )
  }

  if (!customer) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-2xl">👤</span>
        </div>
        <p className="text-gray-600">Customer not found</p>
        <Button onClick={() => navigate('/customers')} className="mt-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Customers
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            onClick={() => navigate('/customers')}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{customer.name}</h1>
            <p className="text-gray-600">
              Customer ID: {customer.id} • Joined {new Date(customer.joined_date).toLocaleDateString()}
            </p>
          </div>
        </div>
        <Button>
          <Edit className="h-4 w-4 mr-2" />
          Edit Customer
        </Button>
      </div>

      {/* Customer Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4 text-center">
          <Trophy className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
          <div className="text-lg font-bold text-gray-900">{customer.tier}</div>
          <div className="text-sm text-gray-600">Current Tier</div>
        </Card>

        <Card className="p-4 text-center">
          <Target className="h-8 w-8 text-blue-600 mx-auto mb-2" />
          <div className="text-lg font-bold text-gray-900">{customer.total_points}</div>
          <div className="text-sm text-gray-600">Total Points</div>
        </Card>

        <Card className="p-4 text-center">
          <Activity className="h-8 w-8 text-green-600 mx-auto mb-2" />
          <div className="text-lg font-bold text-gray-900">{analytics?.engagement_score || 0}%</div>
          <div className="text-sm text-gray-600">Engagement Score</div>
        </Card>

        <Card className="p-4 text-center">
          <Users className="h-8 w-8 text-purple-600 mx-auto mb-2" />
          <div className="text-lg font-bold text-gray-900">{kids.length}</div>
          <div className="text-sm text-gray-600">Registered Kids</div>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Customer Info & Analytics */}
        <div className="lg:col-span-2 space-y-6">
          {/* Customer Information */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Customer Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-3">
                <User className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">Full Name</p>
                  <p className="font-medium">{customer.name}</p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <Mail className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">Email</p>
                  <p className="font-medium">{customer.email}</p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <Phone className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">Phone</p>
                  <p className="font-medium">{customer.phone}</p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <Calendar className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">Last Activity</p>
                  <p className="font-medium">{formatDate(customer.last_activity)}</p>
                </div>
              </div>
            </div>

            <div className="mt-4 flex items-center space-x-4">
              <span className={`px-3 py-1 text-sm font-medium rounded-full ${getTierColor(customer.tier)}`}>
                {customer.tier.charAt(0).toUpperCase() + customer.tier.slice(1)} Tier
              </span>
              <span className={`px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(customer.status)}`}>
                {customer.status.charAt(0).toUpperCase() + customer.status.slice(1)}
              </span>
            </div>
          </Card>

          {/* Analytics */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Analytics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{analytics?.total_transactions || 0}</div>
                <div className="text-sm text-gray-600">Total Transactions</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{analytics?.earned_points || 0}</div>
                <div className="text-sm text-gray-600">Points Earned</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{analytics?.spent_points || 0}</div>
                <div className="text-sm text-gray-600">Points Spent</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{analytics?.recent_activity_score || 0}</div>
                <div className="text-sm text-gray-600">Recent Activity</div>
              </div>
            </div>

            {/* Progress to next tier */}
            {analytics?.next_tier && (
              <div className="mt-6">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-gray-700">
                    Progress to {analytics.next_tier}
                  </span>
                  <span className="text-sm text-gray-500">
                    {analytics.points_to_next_tier} points needed
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${analytics.tier_progress * 100}%` }}
                  />
                </div>
              </div>
            )}
          </Card>

          {/* Kids Information */}
          {kids.length > 0 && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Kids Information</h3>
              <div className="space-y-3">
                {kids.map(kid => (
                  <div key={kid.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium">{kid.name}</p>
                      <p className="text-sm text-gray-600">
                        Age: {kid.age} • {kid.gender}
                      </p>
                      {kid.notes && (
                        <p className="text-xs text-gray-500 mt-1">{kid.notes}</p>
                      )}
                    </div>
                    <div className="text-sm text-gray-500">
                      {new Date(kid.date_of_birth).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>

        {/* Right Column - Activity & Timeline */}
        <div className="space-y-6">
          {/* Quick Stats */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Current Streak</span>
                <span className="font-medium">{customer.current_streak} days</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Longest Streak</span>
                <span className="font-medium">{customer.longest_streak} days</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Lifetime Points</span>
                <span className="font-medium">{customer.lifetime_points}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Avg Points/Transaction</span>
                <span className="font-medium">{analytics?.avg_points_per_transaction || 0}</span>
              </div>
            </div>
          </Card>

          {/* Recent Transactions */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Transactions</h3>
            {recentTransactions.length === 0 ? (
              <p className="text-gray-500 text-sm">No recent transactions</p>
            ) : (
              <div className="space-y-3">
                {recentTransactions.slice(0, 5).map(transaction => (
                  <div key={transaction.id} className="flex justify-between items-center">
                    <div>
                      <p className="font-medium text-sm">{transaction.description}</p>
                      <p className="text-xs text-gray-500">{formatDate(transaction.created_at)}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs font-medium rounded ${
                      transaction.points > 0
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {transaction.points > 0 ? '+' : ''}{transaction.points}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Recent Redemptions */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Redemptions</h3>
            {recentRedemptions.length === 0 ? (
              <p className="text-gray-500 text-sm">No recent redemptions</p>
            ) : (
              <div className="space-y-3">
                {recentRedemptions.slice(0, 3).map(redemption => (
                  <div key={redemption.id}>
                    <p className="font-medium text-sm">{redemption.reward_name}</p>
                    <p className="text-xs text-gray-500">
                      {redemption.quantity}x • {formatDate(redemption.created_at)}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>

      {/* Activity Timeline */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Activity Timeline</h3>
        {timeline.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No activity recorded</p>
        ) : (
          <div className="space-y-4">
            {timeline.map((activity, index) => (
              <div key={index} className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  {getActivityIcon(activity.type)}
                </div>
                <div className="flex-1">
                  <p className="font-medium text-sm">{activity.description}</p>
                  <p className="text-xs text-gray-500">{activity.details}</p>
                  <p className="text-xs text-gray-400">{formatDate(activity.timestamp)}</p>
                </div>
                {activity.points_change !== 0 && (
                  <div className="flex-shrink-0">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${
                      activity.points_change > 0
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {activity.points_change > 0 ? '+' : ''}{activity.points_change}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}

export default CustomerDetails