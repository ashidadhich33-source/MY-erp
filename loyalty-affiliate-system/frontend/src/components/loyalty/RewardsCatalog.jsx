import { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import { Gift, ShoppingCart, Star, Package } from 'lucide-react'
import { loyaltyAPI } from '../../services/api'
import Card from '../ui/Card'
import Button from '../ui/Button'

const RewardsCatalog = ({ customerId }) => {
  const [rewards, setRewards] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [redeemingReward, setRedeemingReward] = useState(null)
  const { user } = useSelector((state) => state.auth)

  useEffect(() => {
    fetchRewards()
  }, [customerId])

  const fetchRewards = async () => {
    try {
      setLoading(true)
      const response = await loyaltyAPI.getAvailableRewards(customerId || user.id)
      setRewards(response)
      setError(null)
    } catch (err) {
      setError('Failed to fetch rewards')
      console.error('Error fetching rewards:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleRedeem = async (rewardId) => {
    try {
      setRedeemingReward(rewardId)
      await loyaltyAPI.redeemReward({
        customer_id: customerId || user.id,
        reward_id: rewardId
      })
      // Refresh rewards after redemption
      await fetchRewards()
      alert('Reward redeemed successfully!')
    } catch (err) {
      alert(`Failed to redeem reward: ${err.response?.data?.detail || 'Unknown error'}`)
    } finally {
      setRedeemingReward(null)
    }
  }

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'food': return Package
      case 'beverage': return '☕'
      case 'gift': return Gift
      case 'discount': return '💰'
      case 'service': return '🛎️'
      case 'event': return '🎉'
      default: return Gift
    }
  }

  const getCategoryColor = (category) => {
    switch (category) {
      case 'food': return 'bg-orange-100 text-orange-800'
      case 'beverage': return 'bg-amber-100 text-amber-800'
      case 'gift': return 'bg-purple-100 text-purple-800'
      case 'discount': return 'bg-green-100 text-green-800'
      case 'service': return 'bg-blue-100 text-blue-800'
      case 'event': return 'bg-pink-100 text-pink-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const categories = ['all', ...new Set(rewards.map(r => r.category))]

  const filteredRewards = selectedCategory === 'all'
    ? rewards
    : rewards.filter(r => r.category === selectedCategory)

  if (loading) {
    return (
      <Card className="p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="h-48 bg-gray-200 rounded"></div>
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
            onClick={fetchRewards}
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
        <h3 className="text-lg font-semibold text-gray-900">Rewards Catalog</h3>
        <div className="flex items-center space-x-2">
          {categories.map(category => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-3 py-1 text-sm rounded-full transition-colors ${
                selectedCategory === category
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {category === 'all' ? 'All' : category.charAt(0).toUpperCase() + category.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {filteredRewards.length === 0 ? (
        <div className="text-center py-12">
          <Gift className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No rewards available in this category</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredRewards.map(reward => {
            const Icon = getCategoryIcon(reward.category)
            const categoryColor = getCategoryColor(reward.category)
            const isRedeeming = redeemingReward === reward.id

            return (
              <div
                key={reward.id}
                className={`border rounded-lg p-4 transition-all hover:shadow-md ${
                  reward.is_featured ? 'border-primary-200 bg-primary-50' : 'border-gray-200'
                }`}
              >
                {/* Featured Badge */}
                {reward.is_featured && (
                  <div className="flex items-center mb-2">
                    <Star className="h-4 w-4 text-primary-600 mr-1" />
                    <span className="text-xs font-medium text-primary-600">Featured</span>
                  </div>
                )}

                {/* Category Icon */}
                <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium mb-3 ${categoryColor}`}>
                  <span className="mr-1">{Icon}</span>
                  {reward.category}
                </div>

                {/* Reward Image */}
                {reward.image_url && (
                  <img
                    src={reward.image_url}
                    alt={reward.name}
                    className="w-full h-32 object-cover rounded-lg mb-3"
                  />
                )}

                {/* Reward Details */}
                <h4 className="font-semibold text-gray-900 mb-2">{reward.name}</h4>
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">{reward.description}</p>

                {/* Points Required */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center">
                    <Gift className="h-4 w-4 text-primary-600 mr-1" />
                    <span className="font-medium text-primary-600">{reward.points_required}</span>
                    <span className="text-sm text-gray-500 ml-1">points</span>
                  </div>
                  <div className="text-xs text-gray-500">
                    Stock: {reward.stock_remaining === 'unlimited' ? '∞' : reward.stock_remaining}
                  </div>
                </div>

                {/* Redemption Info */}
                {reward.customer_redemptions > 0 && (
                  <div className="text-xs text-gray-500 mb-3">
                    Redeemed: {reward.customer_redemptions}/{reward.max_per_customer}
                  </div>
                )}

                {/* Redeem Button */}
                <Button
                  onClick={() => handleRedeem(reward.id)}
                  disabled={isRedeeming}
                  loading={isRedeeming}
                  className="w-full"
                  size="sm"
                >
                  <ShoppingCart className="h-4 w-4 mr-2" />
                  {isRedeeming ? 'Redeeming...' : 'Redeem Now'}
                </Button>
              </div>
            )
          })}
        </div>
      )}

      {/* Summary */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex justify-between items-center text-sm text-gray-600">
          <span>Showing {filteredRewards.length} reward(s)</span>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchRewards}
          >
            Refresh
          </Button>
        </div>
      </div>
    </Card>
  )
}

export default RewardsCatalog