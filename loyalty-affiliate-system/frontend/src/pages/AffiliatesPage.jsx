import { UserCheck, DollarSign } from 'lucide-react'
import Card from '../components/ui/Card'

const AffiliatesPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Affiliate Management</h1>
        <p className="mt-1 text-sm text-gray-600">
          Manage affiliate registrations, commissions, and performance.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <Card className="p-6 text-center">
          <UserCheck className="h-12 w-12 text-primary-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Affiliate Registration</h3>
          <p className="text-sm text-gray-600">Manage affiliate sign-ups and approvals</p>
        </Card>

        <Card className="p-6 text-center">
          <DollarSign className="h-12 w-12 text-primary-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Commission Tracking</h3>
          <p className="text-sm text-gray-600">Track and manage affiliate commissions</p>
        </Card>

        <Card className="p-6 text-center">
          <UserCheck className="h-12 w-12 text-primary-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Performance Analytics</h3>
          <p className="text-sm text-gray-600">View affiliate performance metrics</p>
        </Card>
      </div>

      <Card>
        <div className="text-center py-12">
          <p className="text-gray-500">Affiliate management features coming soon...</p>
        </div>
      </Card>
    </div>
  )
}

export default AffiliatesPage