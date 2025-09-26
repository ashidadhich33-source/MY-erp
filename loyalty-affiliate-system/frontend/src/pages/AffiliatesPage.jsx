import { useState } from 'react'
import { useSelector } from 'react-redux'
import { UserCheck, Users, BarChart3, Download, Settings } from 'lucide-react'
import AffiliateRegistration from '../components/affiliate/AffiliateRegistration'
import AffiliateDashboard from '../components/affiliate/AffiliateDashboard'
import PerformanceChart from '../components/affiliate/PerformanceChart'
import CommissionTable from '../components/affiliate/CommissionTable'
import MarketingMaterials from '../components/affiliate/MarketingMaterials'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'

const AffiliatesPage = () => {
  const [activeTab, setActiveTab] = useState('dashboard')
  const { user } = useSelector((state) => state.auth)

  const tabs = [
    { id: 'dashboard', name: 'Dashboard', icon: BarChart3 },
    { id: 'performance', name: 'Analytics', icon: BarChart3 },
    { id: 'commissions', name: 'Commissions', icon: UserCheck },
    { id: 'materials', name: 'Marketing', icon: Download },
  ]

  // Check if user is already an affiliate
  const isAffiliate = user.role === 'affiliate'

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Affiliate Portal</h1>
        <p className="mt-1 text-sm text-gray-600">
          {isAffiliate
            ? 'Manage your affiliate account, track performance, and view commissions.'
            : 'Join our affiliate program and start earning commissions by referring customers.'
          }
        </p>
      </div>

      {/* Registration Section for Non-Affiliates */}
      {!isAffiliate && (
        <Card className="p-6">
          <div className="text-center">
            <UserCheck className="h-16 w-16 text-primary-600 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Become an Affiliate</h2>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              Join our affiliate program and earn commissions by referring customers to our loyalty program.
              It's free to join and you can start earning immediately after approval.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600 mb-2">5%</div>
                <div className="text-sm text-gray-600">Base Commission Rate</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600 mb-2">$50</div>
                <div className="text-sm text-gray-600">Minimum Payout</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600 mb-2">30 Days</div>
                <div className="text-sm text-gray-600">Cookie Duration</div>
              </div>
            </div>
            <Button
              onClick={() => setActiveTab('register')}
              size="lg"
            >
              Apply Now
            </Button>
          </div>
        </Card>
      )}

      {/* Main Content */}
      {isAffiliate ? (
        <>
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
            {activeTab === 'dashboard' && <AffiliateDashboard />}
            {activeTab === 'performance' && <PerformanceChart affiliateId={user.id} />}
            {activeTab === 'commissions' && <CommissionTable affiliateId={user.id} />}
            {activeTab === 'materials' && <MarketingMaterials />}
          </div>
        </>
      ) : (
        // Registration Form
        activeTab === 'register' && <AffiliateRegistration />
      )}

      {/* Admin Features (if user is admin) */}
      {user.role === 'admin' && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Admin Controls</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Button
              variant="outline"
              onClick={() => window.location.href = '/admin/affiliates'}
              className="justify-center"
            >
              <Users className="h-4 w-4 mr-2" />
              Manage Affiliates
            </Button>
            <Button
              variant="outline"
              onClick={() => window.location.href = '/admin/commissions'}
              className="justify-center"
            >
              <UserCheck className="h-4 w-4 mr-2" />
              Approve Commissions
            </Button>
            <Button
              variant="outline"
              onClick={() => window.location.href = '/admin/payouts'}
              className="justify-center"
            >
              💰 Process Payouts
            </Button>
            <Button
              variant="outline"
              onClick={() => window.location.href = '/admin/reports'}
              className="justify-center"
            >
              📊 View Reports
            </Button>
          </div>
        </Card>
      )}
    </div>
  )
}

export default AffiliatesPage