import { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import { ArrowUpCircle, ArrowDownCircle, Clock, Filter } from 'lucide-react'
import { loyaltyAPI } from '../../services/api'
import Card from '../ui/Card'
import Button from '../ui/Button'

const TransactionHistory = ({ customerId }) => {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('all')
  const { user } = useSelector((state) => state.auth)

  useEffect(() => {
    fetchTransactions()
  }, [customerId, filter])

  const fetchTransactions = async () => {
    try {
      setLoading(true)
      let transactionType = null
      let source = null

      if (filter === 'earned') transactionType = 'earned'
      else if (filter === 'redeemed') transactionType = 'redeemed'
      else if (filter === 'expired') transactionType = 'expired'

      const response = await loyaltyAPI.getTransactions(
        customerId || user.id,
        50,
        0,
        transactionType,
        source
      )
      setTransactions(response.transactions)
      setError(null)
    } catch (err) {
      setError('Failed to fetch transaction history')
      console.error('Error fetching transactions:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatTransactionType = (type, points) => {
    const isPositive = points > 0
    switch (type) {
      case 'earned':
        return { icon: ArrowUpCircle, color: 'text-green-600', label: 'Earned' }
      case 'redeemed':
        return { icon: ArrowDownCircle, color: 'text-red-600', label: 'Redeemed' }
      case 'expired':
        return { icon: Clock, color: 'text-orange-600', label: 'Expired' }
      case 'adjustment':
        return {
          icon: isPositive ? ArrowUpCircle : ArrowDownCircle,
          color: isPositive ? 'text-blue-600' : 'text-purple-600',
          label: 'Adjusted'
        }
      default:
        return {
          icon: ArrowUpCircle,
          color: isPositive ? 'text-green-600' : 'text-red-600',
          label: 'Transaction'
        }
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
            onClick={fetchTransactions}
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
        <h3 className="text-lg font-semibold text-gray-900">Transaction History</h3>
        <div className="flex items-center space-x-2">
          <Filter className="h-4 w-4 text-gray-400" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Transactions</option>
            <option value="earned">Points Earned</option>
            <option value="redeemed">Points Redeemed</option>
            <option value="expired">Points Expired</option>
          </select>
        </div>
      </div>

      {transactions.length === 0 ? (
        <div className="text-center py-12">
          <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No transactions found</p>
          <p className="text-sm text-gray-400 mt-1">
            {filter === 'all' ? 'Start earning points to see your transaction history' : `No ${filter} transactions yet`}
          </p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {transactions.map(transaction => {
            const { icon: IconComponent, color, label } = formatTransactionType(
              transaction.type,
              transaction.points
            )
            const isPositive = transaction.points > 0

            return (
              <div
                key={transaction.id}
                className="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                {/* Transaction Icon */}
                <div className={`p-2 rounded-full mr-4 ${isPositive ? 'bg-green-100' : 'bg-red-100'}`}>
                  <IconComponent className={`h-5 w-5 ${color}`} />
                </div>

                {/* Transaction Details */}
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">{label}</h4>
                      <p className="text-sm text-gray-600">{transaction.description}</p>
                    </div>
                    <div className="text-right">
                      <div className={`font-semibold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                        {isPositive ? '+' : ''}{transaction.points} pts
                      </div>
                      <div className="text-xs text-gray-500">
                        {formatDate(transaction.created_at)}
                      </div>
                    </div>
                  </div>

                  {/* Additional Info */}
                  <div className="flex items-center justify-between mt-2">
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      {transaction.source && (
                        <span className="capitalize">
                          Source: {transaction.source.replace('_', ' ')}
                        </span>
                      )}
                      {transaction.reference_id && (
                        <span>Ref: {transaction.reference_id}</span>
                      )}
                    </div>

                    {transaction.expires_at && (
                      <div className="text-xs text-orange-600">
                        Expires: {formatDate(transaction.expires_at)}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Summary */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-lg font-semibold text-green-600">
              +{transactions.filter(t => t.points > 0).reduce((sum, t) => sum + t.points, 0)}
            </div>
            <div className="text-xs text-gray-500">Total Earned</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-red-600">
              {transactions.filter(t => t.points < 0).reduce((sum, t) => sum + Math.abs(t.points), 0)}
            </div>
            <div className="text-xs text-gray-500">Total Spent</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-gray-900">
              {transactions.reduce((sum, t) => sum + t.points, 0)}
            </div>
            <div className="text-xs text-gray-500">Net Change</div>
          </div>
        </div>
      </div>

      <div className="mt-4 text-center">
        <Button
          variant="outline"
          size="sm"
          onClick={fetchTransactions}
        >
          Refresh
        </Button>
      </div>
    </Card>
  )
}

export default TransactionHistory