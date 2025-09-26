import { useState } from 'react'
import { Database, Settings, Sync, ArrowRight, Activity, AlertTriangle } from 'lucide-react'
import ERPSyncDashboard from '../components/erp/ERPSyncDashboard'
import DataMappingInterface from '../components/erp/DataMappingInterface'
import ERPIntegrationConfig from '../components/erp/ERPIntegrationConfig'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'

const ERPPage = () => {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [integrationStatus, setIntegrationStatus] = useState('disconnected')

  const tabs = [
    { id: 'dashboard', name: 'Sync Dashboard', icon: Database },
    { id: 'mapping', name: 'Data Mapping', icon: ArrowRight },
    { id: 'config', name: 'Configuration', icon: Settings },
  ]

  const integrationSteps = [
    { id: 'config', name: 'Configure Connection', completed: false },
    { id: 'connect', name: 'Test Connection', completed: false },
    { id: 'map', name: 'Set Up Data Mapping', completed: false },
    { id: 'sync', name: 'Configure Sync Schedule', completed: false },
    { id: 'test', name: 'Test Integration', completed: false }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">ERP Integration</h1>
        <p className="mt-1 text-sm text-gray-600">
          Connect and synchronize data with Logic ERP system for seamless business operations.
        </p>
      </div>

      {/* Integration Status */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4 text-center">
          <div className={`w-12 h-12 mx-auto mb-2 rounded-full flex items-center justify-center ${
            integrationStatus === 'connected' ? 'bg-green-100' :
            integrationStatus === 'partial' ? 'bg-yellow-100' : 'bg-red-100'
          }`}>
            {integrationStatus === 'connected' ? (
              <Activity className="h-6 w-6 text-green-600" />
            ) : integrationStatus === 'partial' ? (
              <AlertTriangle className="h-6 w-6 text-yellow-600" />
            ) : (
              <Activity className="h-6 w-6 text-red-600" />
            )}
          </div>
          <div className="text-lg font-bold text-gray-900">
            {integrationStatus === 'connected' ? 'Connected' :
             integrationStatus === 'partial' ? 'Partial' : 'Disconnected'}
          </div>
          <div className="text-sm text-gray-600">Integration Status</div>
        </Card>

        <Card className="p-4 text-center">
          <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
            <Database className="h-6 w-6 text-blue-600" />
          </div>
          <div className="text-lg font-bold text-gray-900">1,247</div>
          <div className="text-sm text-gray-600">Customers Synced</div>
        </Card>

        <Card className="p-4 text-center">
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
            <Sync className="h-6 w-6 text-green-600" />
          </div>
          <div className="text-lg font-bold text-gray-900">45</div>
          <div className="text-sm text-gray-600">Last Sync</div>
        </Card>

        <Card className="p-4 text-center">
          <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
            <Settings className="h-6 w-6 text-purple-600" />
          </div>
          <div className="text-lg font-bold text-gray-900">3</div>
          <div className="text-sm text-gray-600">Active Mappings</div>
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
        {activeTab === 'dashboard' && <ERPSyncDashboard />}
        {activeTab === 'mapping' && <DataMappingInterface />}
        {activeTab === 'config' && <ERPIntegrationConfig />}
      </div>

      {/* Integration Setup Progress */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Integration Setup Progress</h3>
        <div className="space-y-3">
          {integrationSteps.map((step, index) => (
            <div key={step.id} className="flex items-center space-x-3">
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-sm font-medium ${
                step.completed
                  ? 'bg-green-100 text-green-800'
                  : index === 0
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-gray-100 text-gray-600'
              }`}>
                {step.completed ? '✓' : index + 1}
              </div>
              <div className="flex-1">
                <p className={`text-sm font-medium ${
                  step.completed
                    ? 'text-green-800'
                    : index === 0
                    ? 'text-blue-800'
                    : 'text-gray-700'
                }`}>
                  {step.name}
                </p>
              </div>
              {index === 0 && !step.completed && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setActiveTab('config')}
                >
                  Configure
                </Button>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Button
            variant="outline"
            onClick={() => setActiveTab('config')}
            className="justify-center"
          >
            <Settings className="h-4 w-4 mr-2" />
            Configure Connection
          </Button>
          <Button
            variant="outline"
            onClick={() => setActiveTab('mapping')}
            className="justify-center"
          >
            <ArrowRight className="h-4 w-4 mr-2" />
            Set Up Mapping
          </Button>
          <Button
            variant="outline"
            onClick={() => setActiveTab('dashboard')}
            className="justify-center"
          >
            <Database className="h-4 w-4 mr-2" />
            View Sync Status
          </Button>
          <Button
            variant="outline"
            onClick={() => {
              // Test integration
              alert('Integration test would run here')
            }}
            className="justify-center"
          >
            <Activity className="h-4 w-4 mr-2" />
            Test Integration
          </Button>
        </div>
      </Card>

      {/* Integration Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Features</h3>
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-blue-600 text-sm">🔄</span>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Real-time Sync</h4>
                <p className="text-sm text-gray-600">
                  Automatic synchronization with configurable intervals and retry logic
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-green-600 text-sm">⚙️</span>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Data Transformation</h4>
                <p className="text-sm text-gray-600">
                  Flexible data mapping and transformation with validation rules
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-purple-600 text-sm">📊</span>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Error Handling</h4>
                <p className="text-sm text-gray-600">
                  Comprehensive error handling with detailed logging and notifications
                </p>
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Types</h3>
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-orange-600 text-sm">👥</span>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Customer Data</h4>
                <p className="text-sm text-gray-600">
                  Customer information, contact details, and profile data
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-teal-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-teal-600 text-sm">🛒</span>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Sales Data</h4>
                <p className="text-sm text-gray-600">
                  Transaction records, sales history, and purchase data
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-indigo-600 text-sm">📦</span>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Product Data</h4>
                <p className="text-sm text-gray-600">
                  Product catalog, pricing, and inventory information
                </p>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Integration Benefits */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Integration Benefits</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-green-50 rounded-lg">
            <h4 className="font-medium text-green-900 mb-2">Seamless Data Flow</h4>
            <p className="text-sm text-green-800">
              Automatic data synchronization eliminates manual data entry and reduces errors
              between your loyalty system and ERP.
            </p>
          </div>

          <div className="p-4 bg-blue-50 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">Real-time Updates</h4>
            <p className="text-sm text-blue-800">
              Customer purchases and transactions are immediately reflected in both systems,
              ensuring data consistency.
            </p>
          </div>

          <div className="p-4 bg-purple-50 rounded-lg">
            <h4 className="font-medium text-purple-900 mb-2">Unified Customer View</h4>
            <p className="text-sm text-purple-800">
              Single customer profiles across all systems provide better customer service
              and personalized experiences.
            </p>
          </div>

          <div className="p-4 bg-orange-50 rounded-lg">
            <h4 className="font-medium text-orange-900 mb-2">Automated Workflows</h4>
            <p className="text-sm text-orange-800">
              Loyalty points are automatically awarded for purchases, and customer tiers
              are updated based on transaction history.
            </p>
          </div>
        </div>
      </Card>

      {/* Setup Instructions */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Setup Instructions</h3>
        <div className="space-y-4">
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-blue-600 text-sm font-bold">1</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Configure Connection</h4>
              <p className="text-sm text-gray-600">
                Enter your Logic ERP server details, credentials, and test the connection
                to ensure proper connectivity.
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-blue-600 text-sm font-bold">2</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Set Up Data Mapping</h4>
              <p className="text-sm text-gray-600">
                Configure how fields from your ERP system map to loyalty system fields,
                including any necessary transformations.
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-blue-600 text-sm font-bold">3</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Configure Sync Schedule</h4>
              <p className="text-sm text-gray-600">
                Set up automatic synchronization intervals for different data types
                (customers, sales, products).
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-blue-600 text-sm font-bold">4</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Test Integration</h4>
              <p className="text-sm text-gray-600">
                Run test synchronizations to verify that data flows correctly between
                systems and handle any mapping issues.
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-blue-600 text-sm font-bold">5</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Monitor & Maintain</h4>
              <p className="text-sm text-gray-600">
                Monitor the integration dashboard for sync status, errors, and performance
                metrics to ensure smooth operation.
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default ERPPage