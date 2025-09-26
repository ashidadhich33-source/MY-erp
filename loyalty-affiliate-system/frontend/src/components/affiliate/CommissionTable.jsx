import { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import { CheckCircle, Clock, XCircle, Filter, Eye } from 'lucide-react'
import { affiliatesAPI } from '../../services/api'
import Card from '../ui/Card'
import Button from '../ui/Button'

const CommissionTable = ({ affiliateId }) => {
  const [commissions, setCommissions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [statusFilter, setStatusFilter] = useState('all')
  const [selectedCommission, setSelectedCommission] = useState(null)
  const { user } = useSelector((state) => state.auth)

  useEffect(() => {
    fetchCommissions()
  }, [affiliateId, statusFilter])

  const fetchCommissions = async () => {
    try {
      setLoading(true)
      let status = null
      if (statusFilter !== 'all') {
        status = statusFilter.toUpperCase()
      }

      const response = await affiliatesAPI.getCommissions(
        affiliateId || user.id,
        50,
        0,
        status
      )
      setCommissions(response.commissions)
    } catch (err) {
      setError('Failed to fetch commissions')
      console.error('Error fetching commissions:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-600" />
      case 'paid':
        return <CheckCircle className="h-4 w-4 text-blue-600" />
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-red-600" />
      default:
        return <Clock className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'paid':
        return 'bg-blue-100 text-blue-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const calculateTotals = () => {
    const totals = {
      all: 0,
      approved: 0,
      pending: 0,
      paid: 0,
      cancelled: 0
    }

    commissions.forEach(commission => {
      totals.all += commission.commission_amount
      totals[commission.status] += commission.commission_amount
    })

    return totals
  }

  const totals = calculateTotals()

  if (loading) {
    return (
      <Card className="p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="h-12 bg-gray-200 rounded"></div>
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
            onClick={fetchCommissions}
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
        <h3 className="text-lg font-semibold text-gray-900">Commission History</h3>

        {/* Status Filter */}
        <div className="flex items-center space-x-2">
          <Filter className="h-4 w-4 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="paid">Paid</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-50 p-3 rounded-lg text-center">
          <div className="text-lg font-semibold text-gray-900">${totals.all.toFixed(2)}</div>
          <div className="text-xs text-gray-600">Total</div>
        </div>
        <div className="bg-yellow-50 p-3 rounded-lg text-center">
          <div className="text-lg font-semibold text-yellow-800">${totals.pending.toFixed(2)}</div>
          <div className="text-xs text-yellow-600">Pending</div>
        </div>
        <div className="bg-green-50 p-3 rounded-lg text-center">
          <div className="text-lg font-semibold text-green-800">${totals.approved.toFixed(2)}</div>
          <div className="text-xs text-green-600">Approved</div>
        </div>
        <div className="bg-blue-50 p-3 rounded-lg text-center">
          <div className="text-lg font-semibold text-blue-800">${totals.paid.toFixed(2)}</div>
          <div className="text-xs text-blue-600">Paid</div>
        </div>
      </div>

      {commissions.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">💰</span>
          </div>
          <p className="text-gray-500">No commissions found</p>
          <p className="text-sm text-gray-400 mt-1">
            {statusFilter === 'all' ? 'Commissions will appear here when you make referrals that convert' : `No ${statusFilter} commissions yet`}
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Dates
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {commissions.map(commission => (
                <tr key={commission.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      ${commission.commission_amount.toFixed(2)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {commission.commission_rate}%
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getStatusIcon(commission.status)}
                      <span className={`ml-2 px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(commission.status)}`}>
                        {commission.status.charAt(0).toUpperCase() + commission.status.slice(1)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900 max-w-xs truncate" title={commission.description}>
                      {commission.description}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {formatDate(commission.created_at)}
                    </div>
                    {commission.approved_at && (
                      <div className="text-xs text-gray-500">
                        Approved: {formatDate(commission.approved_at)}
                      </div>
                    )}
                    {commission.paid_at && (
                      <div className="text-xs text-green-600">
                        Paid: {formatDate(commission.paid_at)}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSelectedCommission(commission)}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      Details
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Commission Details Modal */}
      {selectedCommission && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Commission Details</h3>

            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Amount:</span>
                <span className="font-semibold">${selectedCommission.commission_amount.toFixed(2)}</span>
              </div>

              <div className="flex justify-between">
                <span className="text-gray-600">Rate:</span>
                <span className="font-semibold">{selectedCommission.commission_rate}%</span>
              </div>

              <div className="flex justify-between">
                <span className="text-gray-600">Status:</span>
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(selectedCommission.status)}`}>
                  {selectedCommission.status}
                </span>
              </div>

              <div className="flex justify-between">
                <span className="text-gray-600">Created:</span>
                <span className="text-sm">{formatDate(selectedCommission.created_at)}</span>
              </div>

              {selectedCommission.approved_at && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Approved:</span>
                  <span className="text-sm">{formatDate(selectedCommission.approved_at)}</span>
                </div>
              )}

              {selectedCommission.paid_at && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Paid:</span>
                  <span className="text-sm text-green-600">{formatDate(selectedCommission.paid_at)}</span>
                </div>
              )}

              {selectedCommission.payment_reference && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Payment Ref:</span>
                  <span className="text-sm font-mono">{selectedCommission.payment_reference}</span>
                </div>
              )}

              <div className="pt-3">
                <p className="text-sm text-gray-600">Description:</p>
                <p className="text-sm text-gray-900">{selectedCommission.description}</p>
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <Button
                variant="outline"
                onClick={() => setSelectedCommission(null)}
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      )}

      <div className="mt-4 flex justify-between items-center">
        <Button
          variant="outline"
          size="sm"
          onClick={fetchCommissions}
        >
          Refresh
        </Button>
        <div className="text-sm text-gray-500">
          Showing {commissions.length} commission(s)
        </div>
      </div>
    </Card>
  )
}

export default CommissionTable