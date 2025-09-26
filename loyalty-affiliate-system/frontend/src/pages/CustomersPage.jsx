import { useState } from 'react'
import { Users, UserPlus, List, User, Users as UsersIcon, Search } from 'lucide-react'
import CustomerList from '../components/customer/CustomerList'
import CustomerDetails from '../components/customer/CustomerDetails'
import KidsManager from '../components/customer/KidsManager'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'

const CustomersPage = () => {
  const [activeTab, setActiveTab] = useState('list')
  const [selectedCustomer, setSelectedCustomer] = useState(null)
  const [showKidsManager, setShowKidsManager] = useState(false)

  const tabs = [
    { id: 'list', name: 'Customer List', icon: List },
    { id: 'details', name: 'Customer Details', icon: User },
    { id: 'kids', name: 'Kids Management', icon: UsersIcon },
  ]

  const handleViewCustomer = (customerId) => {
    setSelectedCustomer(customerId)
    setActiveTab('details')
  }

  const handleManageKids = (customerId, customerName) => {
    setSelectedCustomer({ id: customerId, name: customerName })
    setShowKidsManager(true)
  }

  const handleBackToList = () => {
    setActiveTab('list')
    setSelectedCustomer(null)
    setShowKidsManager(false)
  }

  // If we're in kids manager mode, show the kids manager
  if (showKidsManager && selectedCustomer) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            onClick={handleBackToList}
          >
            ← Back to Customers
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Kids Management</h1>
            <p className="text-gray-600">
              Managing kids for: {selectedCustomer.name}
            </p>
          </div>
        </div>
        <KidsManager
          customerId={selectedCustomer.id}
          customerName={selectedCustomer.name}
        />
      </div>
    )
  }

  // If we're viewing customer details, show the customer details
  if (activeTab === 'details' && selectedCustomer) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            onClick={handleBackToList}
          >
            ← Back to List
          </Button>
          <div className="flex items-center space-x-3">
            <Button
              variant="outline"
              onClick={() => handleManageKids(selectedCustomer.id, selectedCustomer.name)}
            >
              <UsersIcon className="h-4 w-4 mr-2" />
              Manage Kids
            </Button>
            <Button>
              <UserPlus className="h-4 w-4 mr-2" />
              Edit Customer
            </Button>
          </div>
        </div>
        <CustomerDetails customerId={selectedCustomer.id} />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Customer Management</h1>
        <p className="mt-1 text-sm text-gray-600">
          Manage customer accounts, view analytics, and track engagement.
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4 text-center">
          <Users className="h-8 w-8 text-blue-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">1,247</div>
          <div className="text-sm text-gray-600">Total Customers</div>
        </Card>

        <Card className="p-4 text-center">
          <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
            <span className="text-green-600 text-sm">●</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">892</div>
          <div className="text-sm text-gray-600">Active Customers</div>
        </Card>

        <Card className="p-4 text-center">
          <div className="h-8 w-8 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-2">
            <span className="text-yellow-600 text-sm">🏆</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">156</div>
          <div className="text-sm text-gray-600">Gold/Platinum</div>
        </Card>

        <Card className="p-4 text-center">
          <div className="h-8 w-8 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
            <span className="text-purple-600 text-sm">👶</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">324</div>
          <div className="text-sm text-gray-600">Kids Registered</div>
        </Card>
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
        {activeTab === 'list' && (
          <CustomerList
            onViewCustomer={handleViewCustomer}
            onManageKids={handleManageKids}
          />
        )}

        {activeTab === 'details' && !selectedCustomer && (
          <Card className="p-12 text-center">
            <User className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Customer</h3>
            <p className="text-gray-600 mb-6">
              Choose a customer from the list to view their details and manage their account.
            </p>
            <Button onClick={() => setActiveTab('list')}>
              <Search className="h-4 w-4 mr-2" />
              Browse Customers
            </Button>
          </Card>
        )}

        {activeTab === 'kids' && (
          <Card className="p-12 text-center">
            <UsersIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Kids Management</h3>
            <p className="text-gray-600 mb-6">
              Manage children's information for birthday promotions and age-based offers.
              Select a customer first to manage their kids.
            </p>
            <Button onClick={() => setActiveTab('list')}>
              <Search className="h-4 w-4 mr-2" />
              Select Customer
            </Button>
          </Card>
        )}
      </div>

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Button
            variant="outline"
            onClick={() => setActiveTab('list')}
            className="justify-center"
          >
            <List className="h-4 w-4 mr-2" />
            View All Customers
          </Button>
          <Button
            variant="outline"
            onClick={() => {
              // Open customer creation modal
              alert('Customer creation form would open here')
            }}
            className="justify-center"
          >
            <UserPlus className="h-4 w-4 mr-2" />
            Add New Customer
          </Button>
          <Button
            variant="outline"
            onClick={() => {
              // Open bulk operations
              alert('Bulk operations would open here')
            }}
            className="justify-center"
          >
            <Users className="h-4 w-4 mr-2" />
            Bulk Operations
          </Button>
          <Button
            variant="outline"
            onClick={() => {
              // Open analytics
              alert('Customer analytics would open here')
            }}
            className="justify-center"
          >
            <Search className="h-4 w-4 mr-2" />
            Customer Analytics
          </Button>
        </div>
      </Card>

      {/* Customer Segmentation */}
      <Card className="p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Customer Segmentation</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">156</div>
            <div className="text-sm text-green-700">High Value Customers</div>
            <div className="text-xs text-green-600 mt-1">Gold/Platinum tier with high points</div>
          </div>

          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">892</div>
            <div className="text-sm text-blue-700">Active Customers</div>
            <div className="text-xs text-blue-600 mt-1">Activity within last 30 days</div>
          </div>

          <div className="text-center p-4 bg-yellow-50 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">89</div>
            <div className="text-sm text-yellow-700">New Customers</div>
            <div className="text-xs text-yellow-600 mt-1">Joined within last 30 days</div>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default CustomersPage