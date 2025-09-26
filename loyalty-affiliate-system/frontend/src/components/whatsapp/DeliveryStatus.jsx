import { useState, useEffect } from 'react'
import { CheckCircle, Clock, XCircle, RefreshCw, AlertTriangle } from 'lucide-react'
import { whatsappAPI } from '../../services/api'
import Card from '../ui/Card'
import Button from '../ui/Button'

const DeliveryStatus = () => {
  const [messageStats, setMessageStats] = useState({
    total: 0,
    sent: 0,
    delivered: 0,
    read: 0,
    failed: 0
  })
  const [recentMessages, setRecentMessages] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchDeliveryStats()
    fetchRecentMessages()
  }, [])

  const fetchDeliveryStats = async () => {
    try {
      // This would typically come from a dedicated analytics endpoint
      // For now, we'll calculate from recent messages
      const response = await whatsappAPI.getHistory(null, 'outbound', 100)
      const messages = response.messages

      const stats = {
        total: messages.length,
        sent: messages.filter(m => m.status === 'sent').length,
        delivered: messages.filter(m => m.status === 'delivered').length,
        read: messages.filter(m => m.status === 'read').length,
        failed: messages.filter(m => m.status === 'failed').length
      }

      setMessageStats(stats)
    } catch (err) {
      console.error('Error fetching delivery stats:', err)
    }
  }

  const fetchRecentMessages = async () => {
    try {
      setLoading(true)
      const response = await whatsappAPI.getHistory(null, 'outbound', 10)
      setRecentMessages(response.messages)
    } catch (err) {
      setError('Failed to fetch recent messages')
      console.error('Error fetching messages:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'sent':
        return <Clock className="h-5 w-5 text-yellow-600" />
      case 'delivered':
        return <CheckCircle className="h-5 w-5 text-blue-600" />
      case 'read':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-600" />
      default:
        return <Clock className="h-5 w-5 text-gray-600" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'sent':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'delivered':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'read':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const getDeliveryRate = () => {
    if (messageStats.total === 0) return 0
    return Math.round((messageStats.delivered / messageStats.total) * 100)
  }

  const getReadRate = () => {
    if (messageStats.delivered === 0) return 0
    return Math.round((messageStats.read / messageStats.delivered) * 100)
  }

  if (loading) {
    return (
      <Card className="p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </Card>
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
              fetchDeliveryStats()
              fetchRecentMessages()
            }}
            className="mt-2"
          >
            Retry
          </Button>
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">WhatsApp Delivery Status</h2>
        <p className="text-gray-600">
          Monitor message delivery performance and track customer engagement.
        </p>
      </div>

      {/* Overall Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-gray-900">{messageStats.total}</div>
          <div className="text-sm text-gray-600">Total Sent</div>
        </Card>

        <Card className="p-4 text-center">
          <div className="flex items-center justify-center mb-2">
            {getStatusIcon('sent')}
          </div>
          <div className="text-2xl font-bold text-yellow-600">{messageStats.sent}</div>
          <div className="text-sm text-gray-600">Sent</div>
        </Card>

        <Card className="p-4 text-center">
          <div className="flex items-center justify-center mb-2">
            {getStatusIcon('delivered')}
          </div>
          <div className="text-2xl font-bold text-blue-600">{messageStats.delivered}</div>
          <div className="text-sm text-gray-600">Delivered</div>
        </Card>

        <Card className="p-4 text-center">
          <div className="flex items-center justify-center mb-2">
            {getStatusIcon('read')}
          </div>
          <div className="text-2xl font-bold text-green-600">{messageStats.read}</div>
          <div className="text-sm text-gray-600">Read</div>
        </Card>

        <Card className="p-4 text-center">
          <div className="flex items-center justify-center mb-2">
            {getStatusIcon('failed')}
          </div>
          <div className="text-2xl font-bold text-red-600">{messageStats.failed}</div>
          <div className="text-sm text-gray-600">Failed</div>
        </Card>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Delivery Performance</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Delivery Rate</span>
              <span className="text-2xl font-bold text-blue-600">{getDeliveryRate()}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${getDeliveryRate()}%` }}
              />
            </div>
            <p className="text-sm text-gray-500">
              {messageStats.delivered} of {messageStats.total} messages delivered
            </p>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Read Rate</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Read Rate</span>
              <span className="text-2xl font-bold text-green-600">{getReadRate()}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${getReadRate()}%` }}
              />
            </div>
            <p className="text-sm text-gray-500">
              {messageStats.read} of {messageStats.delivered} delivered messages read
            </p>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Failure Rate</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Failure Rate</span>
              <span className="text-2xl font-bold text-red-600">
                {messageStats.total > 0 ? Math.round((messageStats.failed / messageStats.total) * 100) : 0}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-red-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${messageStats.total > 0 ? (messageStats.failed / messageStats.total) * 100 : 0}%` }}
              />
            </div>
            <p className="text-sm text-gray-500">
              {messageStats.failed} messages failed to send
            </p>
          </div>
        </Card>
      </div>

      {/* Recent Messages */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Recent Messages</h3>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              fetchDeliveryStats()
              fetchRecentMessages()
            }}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>

        {recentMessages.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">💬</span>
            </div>
            <p className="text-gray-500">No recent messages</p>
            <p className="text-sm text-gray-400 mt-1">Messages will appear here as they are sent</p>
          </div>
        ) : (
          <div className="space-y-3">
            {recentMessages.map(message => (
              <div key={message.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(message.status)}
                  <div>
                    <p className="font-medium text-gray-900">
                      {message.direction === 'outbound' ? 'Sent to customer' : 'Received from customer'}
                    </p>
                    <p className="text-sm text-gray-600 truncate max-w-md">
                      {message.content}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatDate(message.sent_at || message.created_at)}
                    </p>
                  </div>
                </div>
                <span className={`px-3 py-1 text-sm font-medium rounded-full border ${getStatusColor(message.status)}`}>
                  {message.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Alerts and Recommendations */}
      {messageStats.total > 0 && (
        <Card className="p-6">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Performance Insights</h3>
              <div className="space-y-2 text-sm text-gray-700">
                {getDeliveryRate() < 90 && (
                  <p>• Your delivery rate is below 90%. Check recipient phone numbers and WhatsApp Business API status.</p>
                )}
                {getReadRate() < 50 && (
                  <p>• Message read rate is low. Consider improving message content or timing.</p>
                )}
                {messageStats.failed > 0 && (
                  <p>• You have failed messages. Review error logs and check template approvals.</p>
                )}
                {getDeliveryRate() >= 95 && getReadRate() >= 70 && (
                  <p className="text-green-700">• Excellent performance! Your WhatsApp messages have high delivery and read rates.</p>
                )}
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}

export default DeliveryStatus