import { useState } from 'react'
import { useSelector } from 'react-redux'
import { Gift, History, Award, ShoppingBag } from 'lucide-react'
import PointsDisplay from '../components/loyalty/PointsDisplay'
import TierProgress from '../components/loyalty/TierProgress'
import RewardsCatalog from '../components/loyalty/RewardsCatalog'
import TransactionHistory from '../components/loyalty/TransactionHistory'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'

const LoyaltyPage = () => {
  const [activeTab, setActiveTab] = useState('dashboard')
  const { user } = useSelector((state) => state.auth)

  const tabs = [
    { id: 'dashboard', name: 'Dashboard', icon: Gift },
    { id: 'rewards', name: 'Rewards', icon: ShoppingBag },
    { id: 'history', name: 'History', icon: History },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Loyalty Program</h1>
        <p className="mt-1 text-sm text-gray-600">
          Manage your loyalty points, browse rewards, and view transaction history.
        </p>
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
        {activeTab === 'dashboard' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <PointsDisplay customerId={user.id} />
            <TierProgress customerId={user.id} />
          </div>
        )}

        {activeTab === 'rewards' && (
          <div>
            <RewardsCatalog customerId={user.id} />
          </div>
        )}

        {activeTab === 'history' && (
          <div>
            <TransactionHistory customerId={user.id} />
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Button
            variant="outline"
            onClick={() => setActiveTab('rewards')}
            className="justify-center"
          >
            <ShoppingBag className="h-4 w-4 mr-2" />
            Browse Rewards
          </Button>
          <Button
            variant="outline"
            onClick={() => setActiveTab('history')}
            className="justify-center"
          >
            <History className="h-4 w-4 mr-2" />
            View History
          </Button>
          <Button
            variant="outline"
            onClick={() => window.location.href = '/customers'}
            className="justify-center"
          >
            👥 Manage Customers
          </Button>
          <Button
            variant="outline"
            onClick={() => window.location.href = '/analytics'}
            className="justify-center"
          >
            📊 View Analytics
          </Button>
        </div>
      </Card>
    </div>
  )
}

export default LoyaltyPage