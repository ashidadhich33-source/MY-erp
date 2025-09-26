import { useState } from 'react'
import { MessageCircle, History, Settings, Send, BarChart3 } from 'lucide-react'
import MessageHistory from '../components/whatsapp/MessageHistory'
import TemplateManager from '../components/whatsapp/TemplateManager'
import DeliveryStatus from '../components/whatsapp/DeliveryStatus'
import BroadcastForm from '../components/whatsapp/BroadcastForm'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'

const WhatsAppPage = () => {
  const [activeTab, setActiveTab] = useState('dashboard')

  const tabs = [
    { id: 'dashboard', name: 'Dashboard', icon: BarChart3 },
    { id: 'messages', name: 'Message History', icon: History },
    { id: 'templates', name: 'Templates', icon: Settings },
    { id: 'broadcast', name: 'Broadcast', icon: Send },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">WhatsApp Integration</h1>
        <p className="mt-1 text-sm text-gray-600">
          Manage WhatsApp messaging, templates, delivery tracking, and automated notifications.
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4 text-center">
          <MessageCircle className="h-8 w-8 text-green-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">1,247</div>
          <div className="text-sm text-gray-600">Messages Sent</div>
        </Card>

        <Card className="p-4 text-center">
          <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
            <span className="text-blue-600 text-sm">✓</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">94%</div>
          <div className="text-sm text-gray-600">Delivery Rate</div>
        </Card>

        <Card className="p-4 text-center">
          <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
            <span className="text-green-600 text-sm">👁️</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">68%</div>
          <div className="text-sm text-gray-600">Read Rate</div>
        </Card>

        <Card className="p-4 text-center">
          <div className="h-8 w-8 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
            <span className="text-purple-600 text-sm">📱</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">12</div>
          <div className="text-sm text-gray-600">Active Templates</div>
        </Card>
      </div>

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
        {activeTab === 'dashboard' && <DeliveryStatus />}
        {activeTab === 'messages' && <MessageHistory />}
        {activeTab === 'templates' && <TemplateManager />}
        {activeTab === 'broadcast' && <BroadcastForm />}
      </div>

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Button
            variant="outline"
            onClick={() => setActiveTab('broadcast')}
            className="justify-center"
          >
            <Send className="h-4 w-4 mr-2" />
            Send Broadcast
          </Button>
          <Button
            variant="outline"
            onClick={() => setActiveTab('templates')}
            className="justify-center"
          >
            <Settings className="h-4 w-4 mr-2" />
            Manage Templates
          </Button>
          <Button
            variant="outline"
            onClick={() => setActiveTab('messages')}
            className="justify-center"
          >
            <History className="h-4 w-4 mr-2" />
            View History
          </Button>
          <Button
            variant="outline"
            onClick={() => setActiveTab('dashboard')}
            className="justify-center"
          >
            <BarChart3 className="h-4 w-4 mr-2" />
            View Analytics
          </Button>
        </div>
      </Card>

      {/* Configuration Notice */}
      <Card className="p-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <span className="text-blue-600">ℹ️</span>
            </div>
            <div className="ml-3">
              <h4 className="text-sm font-medium text-blue-900">WhatsApp Business API Setup</h4>
              <div className="mt-2 text-sm text-blue-800">
                <p>
                  To use WhatsApp messaging features, you need to:
                </p>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>Configure WhatsApp Business API credentials in your environment</li>
                  <li>Set up webhooks for message status updates</li>
                  <li>Verify your business phone number</li>
                  <li>Create and submit message templates for approval</li>
                </ul>
                <p className="mt-2">
                  <a
                    href="https://developers.facebook.com/docs/whatsapp/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-medium text-blue-900 underline hover:text-blue-700"
                  >
                    View WhatsApp Business API documentation →
                  </a>
                </p>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default WhatsAppPage