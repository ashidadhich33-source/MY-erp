import { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import { MessageCircle, Send, Clock, CheckCircle, XCircle, Filter } from 'lucide-react'
import { whatsappAPI } from '../../services/api'
import Card from '../ui/Card'
import Button from '../ui/Button'

const MessageHistory = ({ customerId }) => {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [directionFilter, setDirectionFilter] = useState('all')
  const { user } = useSelector((state) => state.auth)

  useEffect(() => {
    fetchMessages()
  }, [customerId, directionFilter])

  const fetchMessages = async () => {
    try {
      setLoading(true)
      let direction = null
      if (directionFilter !== 'all') {
        direction = directionFilter.toUpperCase()
      }

      const response = await whatsappAPI.getHistory(customerId || user.id, direction)
      setMessages(response.messages)
    } catch (err) {
      setError('Failed to fetch message history')
      console.error('Error fetching messages:', err)
    } finally {
      setLoading(false)
    }
  }

  const getMessageIcon = (type, direction) => {
    if (direction === 'outbound') {
      return <Send className="h-4 w-4 text-blue-600" />
    } else {
      return <MessageCircle className="h-4 w-4 text-green-600" />
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'sent':
        return <Clock className="h-4 w-4 text-yellow-600" />
      case 'delivered':
        return <CheckCircle className="h-4 w-4 text-blue-600" />
      case 'read':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-600" />
      default:
        return <Clock className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'sent':
        return 'bg-yellow-100 text-yellow-800'
      case 'delivered':
        return 'bg-blue-100 text-blue-800'
      case 'read':
        return 'bg-green-100 text-green-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  if (loading) {
    return (
      <Card className="p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
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
            onClick={fetchMessages}
            className="mt-2"
          >
            Retry
          </Button>
        </div>
      </Card>
    )
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">WhatsApp Message History</h3>

        {/* Direction Filter */}
        <div className="flex items-center space-x-2">
          <Filter className="h-4 w-4 text-gray-400" />
          <select
            value={directionFilter}
            onChange={(e) => setDirectionFilter(e.target.value)}
            className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Messages</option>
            <option value="outbound">Sent by Us</option>
            <option value="inbound">Received</option>
          </select>
        </div>
      </div>

      {messages.length === 0 ? (
        <div className="text-center py-12">
          <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No messages found</p>
          <p className="text-sm text-gray-400 mt-1">
            {directionFilter === 'all' ? 'Start sending WhatsApp messages to see your history' : `No ${directionFilter} messages yet`}
          </p>
        </div>
      ) : (
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {messages.map(message => (
            <div
              key={message.id}
              className={`flex items-start space-x-3 p-4 border rounded-lg ${
                message.direction === 'outbound'
                  ? 'bg-blue-50 border-blue-200'
                  : 'bg-gray-50 border-gray-200'
              }`}
            >
              {/* Message Icon */}
              <div className={`p-2 rounded-full ${
                message.direction === 'outbound' ? 'bg-blue-100' : 'bg-green-100'
              }`}>
                {getMessageIcon(message.message_type, message.direction)}
              </div>

              {/* Message Content */}
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {message.direction}
                    </span>
                    <span className="text-xs text-gray-500">
                      {message.message_type}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(message.status)}
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(message.status)}`}>
                      {message.status}
                    </span>
                  </div>
                </div>

                <div className="text-sm text-gray-700 mb-2">
                  {message.content}
                </div>

                {/* Media URL */}
                {message.media_url && (
                  <div className="text-xs text-blue-600 mb-2">
                    📎 Media: {message.media_url}
                  </div>
                )}

                {/* Timestamps */}
                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  <span>Sent: {formatDate(message.sent_at || message.created_at)}</span>
                  {message.delivered_at && (
                    <span>Delivered: {formatDate(message.delivered_at)}</span>
                  )}
                  {message.read_at && (
                    <span>Read: {formatDate(message.read_at)}</span>
                  )}
                </div>

                {/* Error Message */}
                {message.error_message && (
                  <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
                    Error: {message.error_message}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Message Statistics */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-lg font-semibold text-gray-900">{messages.length}</div>
            <div className="text-xs text-gray-500">Total</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-blue-600">
              {messages.filter(m => m.direction === 'outbound').length}
            </div>
            <div className="text-xs text-gray-500">Sent</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-green-600">
              {messages.filter(m => m.direction === 'inbound').length}
            </div>
            <div className="text-xs text-gray-500">Received</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-purple-600">
              {messages.filter(m => m.status === 'delivered').length}
            </div>
            <div className="text-xs text-gray-500">Delivered</div>
          </div>
        </div>
      </div>

      <div className="mt-4 flex justify-between items-center">
        <Button
          variant="outline"
          size="sm"
          onClick={fetchMessages}
        >
          Refresh
        </Button>
        <div className="text-sm text-gray-500">
          Showing {messages.length} message(s)
        </div>
      </div>
    </Card>
  )
}

export default MessageHistory