import { useState, useEffect } from 'react'
import { RefreshCw, Database, Sync, AlertTriangle, CheckCircle, XCircle, Clock } from 'lucide-react'
import { erpAPI } from '../../services/api'
import Card from '../ui/Card'
import Button from '../ui/Button'

const ERPSyncDashboard = () => {
  const [syncStatus, setSyncStatus] = useState(null)
  const [integrationHealth, setIntegrationHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastRefresh, setLastRefresh] = useState(null)

  useEffect(() => {
    fetchSyncStatus()
    fetchIntegrationHealth()

    // Set up auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchSyncStatus()
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  const fetchSyncStatus = async () => {
    try {
      const response = await erpAPI.getSyncStatus()
      setSyncStatus(response)
    } catch (err) {
      console.error('Error fetching sync status:', err)
    }
  }

  const fetchIntegrationHealth = async () => {
    try {
      setLoading(true)
      const response = await erpAPI.getIntegrationHealth()
      setIntegrationHealth(response)
    } catch (err) {
      setError('Failed to fetch integration health')
      console.error('Error fetching integration health:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleManualSync = async (syncType) => {
    try {
      await erpAPI.syncData({
        sync_type: syncType,
        full_sync: false
      })
      fetchSyncStatus() // Refresh status
    } catch (err) {
      console.error('Error starting sync:', err)
      alert('Failed to start sync. Please try again.')
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'failed':
      case 'unhealthy':
        return <XCircle className="h-5 w-5 text-red-600" />
      case 'in_progress':
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-600" />
      default:
        return <AlertTriangle className="h-5 w-5 text-gray-600" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected':
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'failed':
      case 'unhealthy':
        return 'bg-red-100 text-red-800'
      case 'in_progress':
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Never'
    return new Date(dateString).toLocaleString()
  }

  const calculateSyncHealth = () => {
    if (!syncStatus) return 'unknown'

    const recentSyncs = syncStatus.recent_syncs || []
    if (recentSyncs.length === 0) return 'unknown'

    const failedSyncs = recentSyncs.filter(sync => sync.status === 'failed').length
    const totalSyncs = recentSyncs.length

    if (failedSyncs === 0) return 'healthy'
    if (failedSyncs / totalSyncs > 0.5) return 'critical'
    return 'warning'
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="text-center text-danger-600">
          <p>{error}</p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              fetchSyncStatus()
              fetchIntegrationHealth()
            }}
            className="mt-2"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">ERP Integration Dashboard</h2>
          <p className="text-gray-600">
            Monitor ERP synchronization status and integration health
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <span className="text-sm text-gray-500">
            Last updated: {formatDate(lastRefresh || new Date())}
          </span>
          <Button
            variant="outline"
            onClick={() => {
              fetchSyncStatus()
              fetchIntegrationHealth()
              setLastRefresh(new Date())
            }}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Overall Health Status */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              {getStatusIcon(integrationHealth?.connection?.status)}
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Connection Status</p>
              <p className="text-lg font-semibold text-gray-900 capitalize">
                {integrationHealth?.connection?.status || 'Unknown'}
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              {getStatusIcon(calculateSyncHealth())}
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Sync Health</p>
              <p className="text-lg font-semibold text-gray-900 capitalize">
                {calculateSyncHealth()}
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Database className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Data Records</p>
              <p className="text-lg font-semibold text-gray-900">
                {integrationHealth?.data?.customers?.count || 0} customers
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Sync className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pending Syncs</p>
              <p className="text-lg font-semibold text-gray-900">
                {syncStatus?.pending_syncs || 0}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Connection Details */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Connection Details</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-3">ERP System Status</h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Connection Status:</span>
                <span className={`px-2 py-1 text-sm font-medium rounded-full ${getStatusColor(integrationHealth?.connection?.status)}`}>
                  {integrationHealth?.connection?.status || 'Unknown'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Overall Health:</span>
                <span className={`px-2 py-1 text-sm font-medium rounded-full ${getStatusColor(integrationHealth?.overall_health)}`}>
                  {integrationHealth?.overall_health || 'Unknown'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Last Sync:</span>
                <span className="text-sm text-gray-900">
                  {formatDate(syncStatus?.last_sync)}
                </span>
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-medium text-gray-900 mb-3">ERP Data Summary</h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Customers:</span>
                <span className="font-medium text-gray-900">
                  {integrationHealth?.data?.customers?.count || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Products:</span>
                <span className="font-medium text-gray-900">
                  {integrationHealth?.data?.products?.count || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Sales Records:</span>
                <span className="font-medium text-gray-900">
                  {integrationHealth?.data?.sales?.count || 0}
                </span>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Sync Operations */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Sync Operations</h3>
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(syncStatus?.connection_status)}`}>
              {syncStatus?.connection_status || 'Disconnected'}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border border-gray-200 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-medium text-gray-900">Customer Sync</h4>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleManualSync('customers')}
              >
                <RefreshCw className="h-4 w-4 mr-1" />
                Sync
              </Button>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Status:</span>
                <span className="text-gray-900">Ready</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Last Sync:</span>
                <span className="text-gray-900">2 hours ago</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Records:</span>
                <span className="text-gray-900">1,247 synced</span>
              </div>
            </div>
          </div>

          <div className="p-4 border border-gray-200 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-medium text-gray-900">Sales Sync</h4>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleManualSync('sales')}
              >
                <RefreshCw className="h-4 w-4 mr-1" />
                Sync
              </Button>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Status:</span>
                <span className="text-gray-900">Ready</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Last Sync:</span>
                <span className="text-gray-900">1 hour ago</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Records:</span>
                <span className="text-gray-900">45 synced</span>
              </div>
            </div>
          </div>

          <div className="p-4 border border-gray-200 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-medium text-gray-900">Full Sync</h4>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleManualSync('all')}
              >
                <RefreshCw className="h-4 w-4 mr-1" />
                Sync All
              </Button>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Status:</span>
                <span className="text-gray-900">Ready</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Next Scheduled:</span>
                <span className="text-gray-900">6:00 AM</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Duration:</span>
                <span className="text-gray-900">~5 minutes</span>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Recent Sync History */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Sync History</h3>
        <div className="space-y-3">
          {syncStatus?.recent_syncs?.slice(0, 5).map((sync, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                {getStatusIcon(sync.status)}
                <div>
                  <p className="font-medium text-gray-900 capitalize">
                    {sync.sync_type} Sync
                  </p>
                  <p className="text-sm text-gray-600">
                    {formatDate(sync.timestamp)}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(sync.status)}`}>
                  {sync.status}
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  {sync.records_successful}/{sync.records_processed} successful
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Error Summary */}
      {(syncStatus?.failed_syncs > 0 || integrationHealth?.overall_health === 'unhealthy') && (
        <Card className="p-6">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Integration Issues</h3>
              <div className="space-y-2">
                {integrationHealth?.connection?.status === 'failed' && (
                  <p className="text-sm text-red-700">
                    • ERP connection is not working. Check connection settings.
                  </p>
                )}
                {syncStatus?.failed_syncs > 0 && (
                  <p className="text-sm text-red-700">
                    • {syncStatus.failed_syncs} sync operations failed recently.
                  </p>
                )}
                <div className="mt-3">
                  <Button variant="outline" size="sm">
                    View Error Details
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}

export default ERPSyncDashboard