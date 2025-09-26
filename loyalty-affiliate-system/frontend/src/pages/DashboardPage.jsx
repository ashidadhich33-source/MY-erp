import { useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { Users, Gift, UserCheck, MessageCircle, TrendingUp, DollarSign } from 'lucide-react'
import { setPageLoading } from '../store/slices/uiSlice'
import Card from '../components/ui/Card'

const DashboardPage = () => {
  const { user } = useSelector((state) => state.auth)
  const dispatch = useDispatch()

  useEffect(() => {
    dispatch(setPageLoading(false))
  }, [dispatch])

  const stats = [
    {
      name: 'Total Customers',
      value: '2,350',
      icon: Users,
      change: '+20.1%',
      changeType: 'increase',
    },
    {
      name: 'Active Loyalty Members',
      value: '1,890',
      icon: Gift,
      change: '+15.2%',
      changeType: 'increase',
    },
    {
      name: 'Active Affiliates',
      value: '124',
      icon: UserCheck,
      change: '+5.4%',
      changeType: 'increase',
    },
    {
      name: 'WhatsApp Messages',
      value: '8,492',
      icon: MessageCircle,
      change: '+12.8%',
      changeType: 'increase',
    },
  ]

  const recentActivity = [
    {
      id: 1,
      type: 'loyalty',
      message: 'Customer John Doe earned 50 points',
      time: '2 minutes ago',
    },
    {
      id: 2,
      type: 'affiliate',
      message: 'Affiliate commission approved for $25.00',
      time: '5 minutes ago',
    },
    {
      id: 3,
      type: 'whatsapp',
      message: 'Birthday message sent to Sarah Johnson',
      time: '10 minutes ago',
    },
    {
      id: 4,
      type: 'customer',
      message: 'New customer registered: Mike Wilson',
      time: '15 minutes ago',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Welcome section */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.name || 'Admin'}!
        </h1>
        <p className="mt-1 text-sm text-gray-600">
          Here's what's happening with your loyalty and affiliate system today.
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.name} className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <stat.icon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    {stat.name}
                  </dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-gray-900">
                      {stat.value}
                    </div>
                    <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                      stat.changeType === 'increase'
                        ? 'text-green-600'
                        : 'text-red-600'
                    }`}>
                      <TrendingUp className="self-center flex-shrink-0 h-4 w-4 text-green-500" />
                      <span className="sr-only">
                        {stat.changeType === 'increase' ? 'Increased' : 'Decreased'} by
                      </span>
                      {stat.change}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        {/* Recent Activity */}
        <Card>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-start space-x-3">
                <div className={`flex-shrink-0 w-2 h-2 rounded-full mt-2 ${
                  activity.type === 'loyalty' ? 'bg-blue-500' :
                  activity.type === 'affiliate' ? 'bg-green-500' :
                  activity.type === 'whatsapp' ? 'bg-purple-500' :
                  'bg-gray-500'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900">{activity.message}</p>
                  <p className="text-sm text-gray-500">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Quick Actions */}
        <Card>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
              <Users className="h-5 w-5 mr-2" />
              Add New Customer
            </button>
            <button className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
              <Gift className="h-5 w-5 mr-2" />
              Award Points
            </button>
            <button className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
              <MessageCircle className="h-5 w-5 mr-2" />
              Send WhatsApp Message
            </button>
            <button className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
              <DollarSign className="h-5 w-5 mr-2" />
              Process Commissions
            </button>
          </div>
        </Card>
      </div>
    </div>
  )
}

export default DashboardPage