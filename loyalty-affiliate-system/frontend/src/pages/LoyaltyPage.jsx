import { Gift, TrendingUp } from 'lucide-react'
import Card from '../components/ui/Card'

const LoyaltyPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Loyalty Program</h1>
        <p className="mt-1 text-sm text-gray-600">
          Manage loyalty points, tiers, and rewards.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <Card className="p-6 text-center">
          <Gift className="h-12 w-12 text-primary-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Points Management</h3>
          <p className="text-sm text-gray-600">Award and track customer loyalty points</p>
        </Card>

        <Card className="p-6 text-center">
          <TrendingUp className="h-12 w-12 text-primary-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Tier Management</h3>
          <p className="text-sm text-gray-600">Manage customer tiers and benefits</p>
        </Card>

        <Card className="p-6 text-center">
          <Gift className="h-12 w-12 text-primary-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Rewards Catalog</h3>
          <p className="text-sm text-gray-600">Manage available rewards and redemptions</p>
        </Card>
      </div>

      <Card>
        <div className="text-center py-12">
          <p className="text-gray-500">Loyalty management features coming soon...</p>
        </div>
      </Card>
    </div>
  )
}

export default LoyaltyPage