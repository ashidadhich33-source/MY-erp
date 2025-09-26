import { BarChart3, TrendingUp } from 'lucide-react'
import Card from '../components/ui/Card'

const AnalyticsPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics & Reporting</h1>
        <p className="mt-1 text-sm text-gray-600">
          View comprehensive analytics and generate reports.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="p-6 text-center">
          <BarChart3 className="h-12 w-12 text-primary-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Dashboard</h3>
          <p className="text-sm text-gray-600">Overview of key metrics</p>
        </Card>

        <Card className="p-6 text-center">
          <TrendingUp className="h-12 w-12 text-primary-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Customer Analytics</h3>
          <p className="text-sm text-gray-600">Customer behavior insights</p>
        </Card>

        <Card className="p-6 text-center">
          <BarChart3 className="h-12 w-12 text-primary-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Loyalty Reports</h3>
          <p className="text-sm text-gray-600">Program performance data</p>
        </Card>

        <Card className="p-6 text-center">
          <TrendingUp className="h-12 w-12 text-primary-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Affiliate Reports</h3>
          <p className="text-sm text-gray-600">Affiliate performance metrics</p>
        </Card>
      </div>

      <Card>
        <div className="text-center py-12">
          <p className="text-gray-500">Analytics dashboard and reporting features coming soon...</p>
        </div>
      </Card>
    </div>
  )
}

export default AnalyticsPage