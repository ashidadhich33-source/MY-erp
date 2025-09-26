import { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import { Coins, TrendingUp, Calendar } from 'lucide-react'
import { loyaltyAPI } from '../../services/api'
import Card from '../ui/Card'
import Button from '../ui/Button'

const PointsDisplay = ({ customerId }) => {
  const [balance, setBalance] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const { user } = useSelector((state) => state.auth)

  useEffect(() => {
    fetchBalance()
  }, [customerId])

  const fetchBalance = async () => {
    try {
      setLoading(true)
      const response = await loyaltyAPI.getPoints(customerId || user.id)
      setBalance(response)
      setError(null)
    } catch (err) {
      setError('Failed to fetch points balance')
      console.error('Error fetching balance:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Card className="p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/3"></div>
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
            onClick={fetchBalance}
            className="mt-2"
          >
            Retry
          </Button>
        </div>
      </Card>
    )
  }

  if (!balance) return null

  const getTierColor = (tier) => {
    switch (tier) {
      case 'bronze': return 'text-amber-600 bg-amber-100'
      case 'silver': return 'text-gray-600 bg-gray-100'
      case 'gold': return 'text-yellow-600 bg-yellow-100'
      case 'platinum': return 'text-purple-600 bg-purple-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const tierColor = getTierColor(balance.current_tier)

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Loyalty Points</h3>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${tierColor}`}>
          {balance.current_tier.charAt(0).toUpperCase() + balance.current_tier.slice(1)} Tier
        </div>
      </div>

      <div className="space-y-4">
        {/* Main Points Display */}
        <div className="text-center">
          <div className="flex items-center justify-center mb-2">
            <Coins className="h-8 w-8 text-primary-600 mr-2" />
            <span className="text-3xl font-bold text-gray-900">{balance.total_points}</span>
          </div>
          <p className="text-sm text-gray-600">Available Points</p>
        </div>

        {/* Progress to Next Tier */}
        {balance.next_tier && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Progress to {balance.next_tier}</span>
              <span className="text-gray-900 font-medium">
                {balance.points_to_next} points needed
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${balance.progress_to_next * 100}%` }}
              />
            </div>
          </div>
        )}

        {/* Tier Benefits */}
        {balance.tier_benefits && balance.tier_benefits.length > 0 && (
          <div className="border-t pt-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Current Benefits</h4>
            <div className="space-y-1">
              {balance.tier_benefits.map((benefit, index) => (
                <div key={index} className="flex items-center text-sm text-gray-600">
                  <TrendingUp className="h-4 w-4 mr-2 text-green-500" />
                  <span>{benefit.description}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Lifetime Points */}
        <div className="border-t pt-4">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center text-gray-600">
              <Calendar className="h-4 w-4 mr-1" />
              <span>Lifetime Points</span>
            </div>
            <span className="font-medium text-gray-900">{balance.lifetime_points}</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-2 pt-4">
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={fetchBalance}
          >
            Refresh
          </Button>
          <Button
            size="sm"
            className="flex-1"
            onClick={() => window.location.href = '/loyalty/history'}
          >
            History
          </Button>
        </div>
      </div>
    </Card>
  )
}

export default PointsDisplay