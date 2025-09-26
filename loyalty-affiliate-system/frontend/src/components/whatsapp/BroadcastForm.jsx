import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { Send, Users, FileText, Calendar, AlertTriangle } from 'lucide-react'
import { whatsappAPI } from '../../services/api'
import Card from '../ui/Card'
import Button from '../ui/Button'
import Input from '../ui/Input'

const BroadcastForm = () => {
  const [customers, setCustomers] = useState([])
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(false)
  const [preview, setPreview] = useState('')
  const [selectedCustomers, setSelectedCustomers] = useState([])
  const [customerFilter, setCustomerFilter] = useState('all')

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors }
  } = useForm()

  const selectedTemplate = watch('template_id')
  const messageContent = watch('message_content')

  useEffect(() => {
    fetchCustomers()
    fetchTemplates()
  }, [])

  useEffect(() => {
    updatePreview()
  }, [selectedTemplate, messageContent])

  const fetchCustomers = async () => {
    try {
      // This would typically come from a customers API
      // For now, we'll use mock data
      const mockCustomers = [
        { id: 1, name: 'John Doe', phone: '+1234567890', tier: 'Gold' },
        { id: 2, name: 'Jane Smith', phone: '+1234567891', tier: 'Silver' },
        { id: 3, name: 'Bob Johnson', phone: '+1234567892', tier: 'Bronze' }
      ]
      setCustomers(mockCustomers)
    } catch (err) {
      console.error('Error fetching customers:', err)
    }
  }

  const fetchTemplates = async () => {
    try {
      const response = await whatsappAPI.getTemplates()
      setTemplates(response)
    } catch (err) {
      console.error('Error fetching templates:', err)
    }
  }

  const updatePreview = () => {
    if (selectedTemplate) {
      const template = templates.find(t => t.id == selectedTemplate)
      if (template) {
        let preview = template.content
        // Replace variables with sample data
        preview = preview.replace(/\{\{(\w+)\}\}/g, (match, variable) => {
          switch (variable) {
            case 'name': return 'John Doe'
            case 'points': return '150'
            case 'tier': return 'Gold'
            default: return `[${variable.toUpperCase()}]`
          }
        })
        setPreview(preview)
      }
    } else if (messageContent) {
      setPreview(messageContent)
    } else {
      setPreview('Message preview will appear here...')
    }
  }

  const handleCustomerToggle = (customerId) => {
    setSelectedCustomers(prev =>
      prev.includes(customerId)
        ? prev.filter(id => id !== customerId)
        : [...prev, customerId]
    )
  }

  const handleSelectAll = () => {
    const filteredCustomers = getFilteredCustomers()
    if (selectedCustomers.length === filteredCustomers.length) {
      setSelectedCustomers([])
    } else {
      setSelectedCustomers(filteredCustomers.map(c => c.id))
    }
  }

  const getFilteredCustomers = () => {
    if (customerFilter === 'all') return customers
    return customers.filter(c => c.tier.toLowerCase() === customerFilter.toLowerCase())
  }

  const handleSendBroadcast = async (data) => {
    if (selectedCustomers.length === 0) {
      alert('Please select at least one customer')
      return
    }

    try {
      setLoading(true)

      const results = []
      for (const customerId of selectedCustomers) {
        const customer = customers.find(c => c.id === customerId)

        try {
          if (data.template_id) {
            // Send template message
            await whatsappAPI.sendTemplate({
              phone_number: customer.phone,
              template_name: data.template_name,
              variables: {
                name: customer.name.split(' ')[0],
                full_name: customer.name,
                phone: customer.phone,
                tier: customer.tier
              },
              customer_id: customerId
            })
          } else {
            // Send custom message
            await whatsappAPI.send({
              phone_number: customer.phone,
              message_type: 'text',
              content: data.message_content,
              customer_id: customerId
            })
          }

          results.push({ customer: customer.name, status: 'success' })
        } catch (err) {
          results.push({ customer: customer.name, status: 'failed', error: err.message })
        }
      }

      // Show results
      const successCount = results.filter(r => r.status === 'success').length
      const failCount = results.filter(r => r.status === 'failed').length

      alert(`Broadcast completed!\n\nSuccessful: ${successCount}\nFailed: ${failCount}`)

    } catch (err) {
      alert(`Broadcast failed: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const filteredCustomers = getFilteredCustomers()

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Send Broadcast Message</h3>
          <p className="text-gray-600">
            Send WhatsApp messages to multiple customers at once using templates or custom content.
          </p>
        </div>

        <form onSubmit={handleSubmit(handleSendBroadcast)} className="space-y-6">
          {/* Message Type Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Message Type
              </label>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="radio"
                    {...register('message_type')}
                    value="template"
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                    onChange={() => setValue('template_id', '')}
                  />
                  <span className="ml-2 text-sm text-gray-700">Use Template</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    {...register('message_type')}
                    value="custom"
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                    onChange={() => setValue('template_id', '')}
                  />
                  <span className="ml-2 text-sm text-gray-700">Custom Message</span>
                </label>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Template
              </label>
              <select
                {...register('template_id')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                disabled={watch('message_type') !== 'template'}
              >
                <option value="">Select a template</option>
                {templates.map(template => (
                  <option key={template.id} value={template.id}>
                    {template.name} ({template.category})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Custom Message Content */}
          {watch('message_type') === 'custom' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Message Content
              </label>
              <textarea
                {...register('message_content', { required: 'Message content is required' })}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Enter your message content..."
              />
              {errors.message_content && (
                <p className="text-sm text-danger-600 mt-1">{errors.message_content.message}</p>
              )}
            </div>
          )}

          {/* Message Preview */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Message Preview
            </label>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 min-h-[100px]">
              <p className="text-sm text-gray-700 whitespace-pre-wrap">{preview}</p>
            </div>
          </div>

          {/* Customer Selection */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <label className="block text-sm font-medium text-gray-700">
                Select Recipients
              </label>
              <div className="flex items-center space-x-4">
                <select
                  value={customerFilter}
                  onChange={(e) => setCustomerFilter(e.target.value)}
                  className="text-sm border border-gray-300 rounded px-2 py-1"
                >
                  <option value="all">All Customers</option>
                  <option value="bronze">Bronze Tier</option>
                  <option value="silver">Silver Tier</option>
                  <option value="gold">Gold Tier</option>
                  <option value="platinum">Platinum Tier</option>
                </select>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleSelectAll}
                >
                  {selectedCustomers.length === filteredCustomers.length ? 'Deselect All' : 'Select All'}
                </Button>
              </div>
            </div>

            <div className="border border-gray-200 rounded-lg max-h-64 overflow-y-auto">
              {filteredCustomers.map(customer => (
                <label
                  key={customer.id}
                  className="flex items-center p-3 hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedCustomers.includes(customer.id)}
                    onChange={() => handleCustomerToggle(customer.id)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <div className="ml-3 flex-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{customer.name}</p>
                        <p className="text-xs text-gray-500">{customer.phone}</p>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        customer.tier === 'Bronze' ? 'bg-amber-100 text-amber-800' :
                        customer.tier === 'Silver' ? 'bg-gray-100 text-gray-800' :
                        customer.tier === 'Gold' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-purple-100 text-purple-800'
                      }`}>
                        {customer.tier}
                      </span>
                    </div>
                  </div>
                </label>
              ))}
            </div>

            <p className="text-xs text-gray-500 mt-2">
              {selectedCustomers.length} of {filteredCustomers.length} customers selected
            </p>
          </div>

          {/* Warning */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start">
              <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5 mr-3" />
              <div>
                <h4 className="text-sm font-medium text-yellow-800">Broadcast Guidelines</h4>
                <ul className="mt-2 text-sm text-yellow-700 space-y-1">
                  <li>• Only send to customers who have opted in to WhatsApp notifications</li>
                  <li>• Keep messages relevant and valuable to recipients</li>
                  <li>• Avoid sending too frequently to prevent opt-outs</li>
                  <li>• Include unsubscribe information if required by regulations</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setSelectedCustomers([])
                setValue('template_id', '')
                setValue('message_content', '')
              }}
            >
              Clear
            </Button>
            <Button
              type="submit"
              loading={loading}
              disabled={loading || selectedCustomers.length === 0}
            >
              <Send className="h-4 w-4 mr-2" />
              Send to {selectedCustomers.length} Customer{selectedCustomers.length !== 1 ? 's' : ''}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}

export default BroadcastForm