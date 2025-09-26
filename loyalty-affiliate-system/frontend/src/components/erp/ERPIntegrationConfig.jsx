import { useState, useEffect } from 'react'
import { Settings, Database, CheckCircle, XCircle, AlertTriangle, Save, RefreshCw } from 'lucide-react'
import { erpAPI } from '../../services/api'
import Card from '../ui/Card'
import Button from '../ui/Input'

const ERPIntegrationConfig = () => {
  const [connectionStatus, setConnectionStatus] = useState(null)
  const [syncSchedule, setSyncSchedule] = useState(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [config, setConfig] = useState({
    host: '',
    port: 8080,
    database: '',
    username: '',
    password: '',
    api_key: '',
    timeout: 30
  })

  useEffect(() => {
    loadCurrentConfig()
    checkConnectionStatus()
    loadSyncSchedule()
  }, [])

  const loadCurrentConfig = () => {
    // Load current configuration from localStorage or API
    const savedConfig = localStorage.getItem('erp_config')
    if (savedConfig) {
      setConfig(JSON.parse(savedConfig))
    }
  }

  const checkConnectionStatus = async () => {
    try {
      const response = await erpAPI.getIntegrationHealth()
      setConnectionStatus(response.connection)
    } catch (err) {
      console.error('Error checking connection:', err)
      setConnectionStatus({ status: 'unknown', message: 'Unable to check status' })
    }
  }

  const loadSyncSchedule = async () => {
    try {
      const response = await erpAPI.getSyncSchedule()
      setSyncSchedule(response)
    } catch (err) {
      console.error('Error loading sync schedule:', err)
    }
  }

  const handleConfigChange = (field, value) => {
    setConfig(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const testConnection = async () => {
    try {
      setLoading(true)
      const response = await erpAPI.testConnection(config)
      setConnectionStatus(response)
    } catch (err) {
      console.error('Error testing connection:', err)
      setConnectionStatus({
        status: 'failed',
        message: 'Connection test failed. Please check your settings.'
      })
    } finally {
      setLoading(false)
    }
  }

  const saveConfiguration = async () => {
    try {
      setSaving(true)

      // Save to localStorage for now
      localStorage.setItem('erp_config', JSON.stringify(config))

      // Save to backend (this would be implemented)
      // await erpAPI.saveConfiguration(config)

      alert('Configuration saved successfully!')
    } catch (err) {
      console.error('Error saving configuration:', err)
      alert('Failed to save configuration. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const updateSyncSchedule = async (scheduleType, enabled, interval) => {
    try {
      await erpAPI.configureSyncSchedule({
        [scheduleType]: {
          enabled,
          interval_hours: interval
        }
      })
      loadSyncSchedule()
      alert('Sync schedule updated successfully!')
    } catch (err) {
      console.error('Error updating sync schedule:', err)
      alert('Failed to update sync schedule. Please try again.')
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-600" />
      default:
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected':
        return 'bg-green-100 text-green-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-yellow-100 text-yellow-800'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">ERP Integration Configuration</h2>
          <p className="text-gray-600">
            Configure and manage your Logic ERP integration settings
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => {
            loadCurrentConfig()
            checkConnectionStatus()
            loadSyncSchedule()
          }}
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Connection Status */}
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {getStatusIcon(connectionStatus?.status)}
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Connection Status</h3>
              <p className="text-gray-600">
                {connectionStatus?.message || 'Status unknown'}
              </p>
            </div>
          </div>
          <div className={`px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(connectionStatus?.status)}`}>
            {connectionStatus?.status || 'Unknown'}
          </div>
        </div>
      </Card>

      {/* Connection Configuration */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">ERP Connection Settings</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ERP Host *
              </label>
              <input
                type="text"
                value={config.host}
                onChange={(e) => handleConfigChange('host', e.target.value)}
                placeholder="erp.yourcompany.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Port *
              </label>
              <input
                type="number"
                value={config.port}
                onChange={(e) => handleConfigChange('port', parseInt(e.target.value))}
                placeholder="8080"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Database Name *
              </label>
              <input
                type="text"
                value={config.database}
                onChange={(e) => handleConfigChange('database', e.target.value)}
                placeholder="logic_erp"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Username *
              </label>
              <input
                type="text"
                value={config.username}
                onChange={(e) => handleConfigChange('username', e.target.value)}
                placeholder="erp_user"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password *
              </label>
              <input
                type="password"
                value={config.password}
                onChange={(e) => handleConfigChange('password', e.target.value)}
                placeholder="••••••••"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Key (Optional)
              </label>
              <input
                type="password"
                value={config.api_key}
                onChange={(e) => handleConfigChange('api_key', e.target.value)}
                placeholder="API key for authentication"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Connection Timeout (seconds)
              </label>
              <input
                type="number"
                value={config.timeout}
                onChange={(e) => handleConfigChange('timeout', parseInt(e.target.value))}
                placeholder="30"
                min="10"
                max="300"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div className="flex items-center justify-between pt-4">
              <Button
                variant="outline"
                onClick={testConnection}
                loading={loading}
                disabled={loading}
              >
                Test Connection
              </Button>
              <Button
                onClick={saveConfiguration}
                loading={saving}
                disabled={saving}
              >
                <Save className="h-4 w-4 mr-2" />
                Save Configuration
              </Button>
            </div>
          </div>
        </div>
      </Card>

      {/* Sync Schedule Configuration */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Synchronization Schedule</h3>

        <div className="space-y-4">
          {syncSchedule && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900">Customer Sync</h4>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={syncSchedule.customers_sync?.enabled || false}
                        onChange={(e) => updateSyncSchedule('customers_sync', e.target.checked, syncSchedule.customers_sync?.interval_hours || 6)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                    </label>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Interval:</span>
                      <span className="text-gray-900">
                        {syncSchedule.customers_sync?.interval_hours || 6} hours
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Next Run:</span>
                      <span className="text-gray-900">
                        {syncSchedule.customers_sync?.next_run ?
                          new Date(syncSchedule.customers_sync.next_run).toLocaleTimeString() :
                          'Not scheduled'
                        }
                      </span>
                    </div>
                  </div>
                </div>

                <div className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900">Sales Sync</h4>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={syncSchedule.sales_sync?.enabled || false}
                        onChange={(e) => updateSyncSchedule('sales_sync', e.target.checked, syncSchedule.sales_sync?.interval_hours || 1)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                    </label>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Interval:</span>
                      <span className="text-gray-900">
                        {syncSchedule.sales_sync?.interval_hours || 1} hours
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Next Run:</span>
                      <span className="text-gray-900">
                        {syncSchedule.sales_sync?.next_run ?
                          new Date(syncSchedule.sales_sync.next_run).toLocaleTimeString() :
                          'Not scheduled'
                        }
                      </span>
                    </div>
                  </div>
                </div>

                <div className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900">Products Sync</h4>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={syncSchedule.products_sync?.enabled || false}
                        onChange={(e) => updateSyncSchedule('products_sync', e.target.checked, syncSchedule.products_sync?.interval_hours || 24)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                    </label>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Interval:</span>
                      <span className="text-gray-900">
                        {syncSchedule.products_sync?.interval_hours || 24} hours
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Next Run:</span>
                      <span className="text-gray-900">
                        {syncSchedule.products_sync?.next_run ?
                          new Date(syncSchedule.products_sync.next_run).toLocaleTimeString() :
                          'Not scheduled'
                        }
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </Card>

      {/* Integration Features */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Integration Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-blue-600 text-sm">🔄</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Real-time Sync</h4>
              <p className="text-sm text-gray-600">
                Automatic synchronization of customer and sales data with configurable intervals
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-green-600 text-sm">⚙️</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Data Mapping</h4>
              <p className="text-sm text-gray-600">
                Flexible data mapping with transformation capabilities and validation rules
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
                Comprehensive error handling with retry logic and detailed error reporting
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-orange-600 text-sm">🔍</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Audit Trail</h4>
              <p className="text-sm text-gray-600">
                Complete audit trail of all synchronization activities and data changes
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Help Section */}
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
                Enter your Logic ERP server details including host, port, database name, and credentials.
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-blue-600 text-sm font-bold">2</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Test Connection</h4>
              <p className="text-sm text-gray-600">
                Click "Test Connection" to verify that the integration can successfully connect to your ERP system.
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-blue-600 text-sm font-bold">3</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Configure Data Mapping</h4>
              <p className="text-sm text-gray-600">
                Set up field mappings to define how data should be transferred between the systems.
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-blue-600 text-sm font-bold">4</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Set Sync Schedule</h4>
              <p className="text-sm text-gray-600">
                Configure how often data should be synchronized between the systems.
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-blue-600 text-sm font-bold">5</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Test Integration</h4>
              <p className="text-sm text-gray-600">
                Run initial synchronization tests to ensure everything is working correctly.
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default ERPIntegrationConfig