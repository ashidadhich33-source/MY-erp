import { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import { Trophy, Star, Award, Crown } from 'lucide-react'
import { loyaltyAPI } from '../../services/api'
import Card from '../ui/Card'

const TierProgress = ({ customerId }) => {
  const [tierData, setTierData] = useState(null)
  const [loading, setLoading] = useState(true)
  const { user } = useSelector((state) => state.auth)

  useEffect(() => {
    fetchTierData()
  }, [customerId])

  const fetchTierData = async () => {
    try {
      setLoading(true)
      const response = await loyaltyAPI.getPoints(customerId || user.id)
      setTierData(response)
    } catch (err) {
      console.error('Error fetching tier data:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading || !tierData) {
    return (
      <Card className="p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-4 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </Card>
    )
  }

  const getTierIcon = (tier) => {
    switch (tier) {
      case 'bronze': return Trophy
      case 'silver': return Award
      case 'gold': return Star
      case 'platinum': return Crown
      default: return Trophy
    }
  }

  const getTierColor = (tier) => {
    switch (tier) {
      case 'bronze': return 'border-amber-200 bg-amber-50 text-amber-800'
      case 'silver': return 'border-gray-200 bg-gray-50 text-gray-800'
      case 'gold': return 'border-yellow-200 bg-yellow-50 text-yellow-800'
      case 'platinum': return 'border-purple-200 bg-purple-50 text-purple-800'
      default: return 'border-gray-200 bg-gray-50 text-gray-800'
    }
  }

  const tierThresholds = {
    bronze: 0,
    silver: 200,
    gold: 500,
    platinum: 1000
  }

  const tiers = Object.entries(tierThresholds)
  const currentTierIndex = tiers.findIndex(([tier]) => tier === tierData.current_tier)

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Tier Progress</h3>

      <div className="space-y-4">
        {tiers.map(([tier, threshold], index) => {
          const Icon = getTierIcon(tier)
          const isCurrentTier = tier === tierData.current_tier
          const isUnlocked = index <= currentTierIndex
          const isNextTier = index === currentTierIndex + 1
          const tierColor = getTierColor(tier)

          return (
            <div
              key={tier}
              className={`relative p-4 rounded-lg border-2 transition-all duration-200 ${
                isCurrentTier
                  ? `${tierColor} border-current shadow-md`
                  : isUnlocked
                  ? 'border-gray-200 bg-gray-50'
                  : 'border-gray-200 bg-gray-50 opacity-60'
              }`}
            >
              {/* Tier Icon and Name */}
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-full ${
                  isCurrentTier ? 'bg-white' : 'bg-gray-100'
                }`}>
                  <Icon className={`h-5 w-5 ${
                    isCurrentTier ? 'text-current' : 'text-gray-400'
                  }`} />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium capitalize">
                    {tier} Tier
                    {isCurrentTier && <span className="ml-2 text-xs">(Current)</span>}
                    {isNextTier && <span className="ml-2 text-xs text-primary-600">(Next)</span>}
                  </h4>
                  <p className="text-sm text-gray-600">
                    {threshold} points required
                  </p>
                </div>
              </div>

              {/* Progress Bar for Current Tier */}
              {isCurrentTier && tierData.next_tier && (
                <div className="mt-3">
                  <div className="flex justify-between text-sm mb-1">
                    <span>Progress</span>
                    <span>{tierData.points_to_next} points to go</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-current h-2 rounded-full transition-all duration-300"
                      style={{ width: `${tierData.progress_to_next * 100}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Tier Benefits Preview */}
              {isCurrentTier && tierData.tier_benefits && (
                <div className="mt-3 pt-3 border-t border-current border-opacity-20">
                  <h5 className="text-sm font-medium mb-2">Your Benefits:</h5>
                  <ul className="space-y-1">
                    {tierData.tier_benefits.slice(0, 2).map((benefit, idx) => (
                      <li key={idx} className="text-xs flex items-center">
                        <span className="w-1.5 h-1.5 bg-current rounded-full mr-2"></span>
                        {benefit.description}
                      </li>
                    ))}
                    {tierData.tier_benefits.length > 2 && (
                      <li className="text-xs text-gray-500">
                        +{tierData.tier_benefits.length - 2} more benefits
                      </li>
                    )}
                  </ul>
                </div>
              )}

              {/* Lock Icon for Locked Tiers */}
              {!isUnlocked && (
                <div className="absolute inset-0 flex items-center justify-center bg-gray-50 bg-opacity-75 rounded-lg">
                  <div className="text-center">
                    <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-2">
                      🔒
                    </div>
                    <p className="text-xs text-gray-500">Locked</p>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Tier Upgrade Notice */}
      {tierData.next_tier && (
        <div className="mt-4 p-3 bg-primary-50 border border-primary-200 rounded-lg">
          <div className="flex items-center">
            <Star className="h-5 w-5 text-primary-600 mr-2" />
            <div className="flex-1">
              <p className="text-sm font-medium text-primary-900">
                Almost there! {tierData.points_to_next} more points to reach {tierData.next_tier} tier
              </p>
              <p className="text-xs text-primary-700">
                You'll unlock new benefits and perks!
              </p>
            </div>
          </div>
        </div>
      )}
    </Card>
  )
}

export default TierProgress