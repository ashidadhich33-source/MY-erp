import { Plus, Search } from 'lucide-react'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Card from '../components/ui/Card'

const CustomersPage = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Customers</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage your customer database and loyalty information.
          </p>
        </div>
        <Button>
          <Plus className="h-5 w-5 mr-2" />
          Add Customer
        </Button>
      </div>

      <Card className="p-4">
        <div className="flex items-center space-x-4 mb-4">
          <div className="flex-1">
            <Input
              placeholder="Search customers..."
              icon={<Search className="h-5 w-5 text-gray-400" />}
            />
          </div>
          <Button variant="outline">Filter</Button>
        </div>

        <div className="text-center py-12">
          <p className="text-gray-500">Customer management interface coming soon...</p>
        </div>
      </Card>
    </div>
  )
}

export default CustomersPage