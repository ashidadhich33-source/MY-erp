import { MessageCircle, Send } from 'lucide-react'
import Card from '../components/ui/Card'

const WhatsAppPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">WhatsApp Integration</h1>
        <p className="mt-1 text-sm text-gray-600">
          Manage WhatsApp messaging, templates, and automation.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <Card className="p-6 text-center">
          <MessageCircle className="h-12 w-12 text-primary-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Message Templates</h3>
          <p className="text-sm text-gray-600">Create and manage message templates</p>
        </Card>

        <Card className="p-6 text-center">
          <Send className="h-12 w-12 text-primary-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Bulk Messaging</h3>
          <p className="text-sm text-gray-600">Send bulk messages to customers</p>
        </Card>

        <Card className="p-6 text-center">
          <MessageCircle className="h-12 w-12 text-primary-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Automation</h3>
          <p className="text-sm text-gray-600">Set up automated messaging rules</p>
        </Card>
      </div>

      <Card>
        <div className="text-center py-12">
          <p className="text-gray-500">WhatsApp integration features coming soon...</p>
        </div>
      </Card>
    </div>
  )
}

export default WhatsAppPage