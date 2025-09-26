import { useState } from 'react'
import { useSelector } from 'react-redux'
import { useForm } from 'react-hook-form'
import { UserPlus, Globe, CreditCard, FileText } from 'lucide-react'
import { affiliatesAPI } from '../../services/api'
import Card from '../ui/Card'
import Button from '../ui/Button'
import Input from '../ui/Input'

const AffiliateRegistration = () => {
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState(null)
  const { user } = useSelector((state) => state.auth)

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch
  } = useForm()

  const marketingChannels = watch('marketing_channels') || []

  const onSubmit = async (data) => {
    try {
      setLoading(true)
      setError(null)

      const requestData = {
        user_id: user.id,
        website_url: data.website_url || null,
        marketing_channels: data.marketing_channels || null,
        payment_method: data.payment_method || null,
        payment_details: data.payment_details ? JSON.parse(data.payment_details) : null,
        notes: data.notes || null
      }

      await affiliatesAPI.register(requestData)

      setSuccess(true)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to register as affiliate')
    } finally {
      setLoading(false)
    }
  }

  const handleChannelChange = (channel) => {
    const current = marketingChannels
    const updated = current.includes(channel)
      ? current.filter(c => c !== channel)
      : [...current, channel]

    // Update form value
    const syntheticEvent = {
      target: {
        name: 'marketing_channels',
        value: updated
      }
    }
    register('marketing_channels').onChange(syntheticEvent)
  }

  if (success) {
    return (
      <Card className="p-8 text-center">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <UserPlus className="h-8 w-8 text-green-600" />
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Welcome to our Affiliate Program!</h3>
        <p className="text-gray-600 mb-4">
          Your application has been submitted successfully. We'll review it and get back to you within 24-48 hours.
        </p>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <p className="text-sm text-blue-800">
            <strong>What's next?</strong><br />
            • We'll review your application<br />
            • You'll receive an email with your affiliate code<br />
            • Start earning commissions once approved
          </p>
        </div>
        <Button onClick={() => window.location.href = '/affiliates'}>
          Go to Affiliate Dashboard
        </Button>
      </Card>
    )
  }

  return (
    <Card className="p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Become an Affiliate</h3>
        <p className="text-gray-600">
          Join our affiliate program and start earning commissions by referring customers.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {error && (
          <div className="bg-danger-50 border border-danger-200 rounded-lg p-4">
            <p className="text-sm text-danger-600">{error}</p>
          </div>
        )}

        {/* Website Information */}
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900 flex items-center">
            <Globe className="h-4 w-4 mr-2" />
            Website Information (Optional)
          </h4>

          <Input
            label="Website URL"
            placeholder="https://yourwebsite.com"
            {...register('website_url', {
              pattern: {
                value: /^https?:\/\/.+/,
                message: 'Please enter a valid URL starting with http:// or https://'
              }
            })}
            error={errors.website_url?.message}
          />
        </div>

        {/* Marketing Channels */}
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900">Marketing Channels</h4>
          <p className="text-sm text-gray-600">Select the channels you plan to use for promotion</p>

          <div className="grid grid-cols-2 gap-3">
            {[
              'Social Media',
              'Blog/Content',
              'Email Marketing',
              'YouTube/Video',
              'Website',
              'Other'
            ].map(channel => (
              <label key={channel} className="flex items-center">
                <input
                  type="checkbox"
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  checked={marketingChannels.includes(channel)}
                  onChange={() => handleChannelChange(channel)}
                />
                <span className="ml-2 text-sm text-gray-700">{channel}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Payment Information */}
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900 flex items-center">
            <CreditCard className="h-4 w-4 mr-2" />
            Payment Information
          </h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Preferred Payment Method
              </label>
              <select
                {...register('payment_method')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Select method</option>
                <option value="bank_transfer">Bank Transfer</option>
                <option value="paypal">PayPal</option>
                <option value="check">Check</option>
                <option value="crypto">Cryptocurrency</option>
              </select>
            </div>

            <Input
              label="Payment Details (JSON format)"
              placeholder='{"account_number": "123456", "routing_number": "789"}'
              {...register('payment_details')}
            />
          </div>
        </div>

        {/* Additional Information */}
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900 flex items-center">
            <FileText className="h-4 w-4 mr-2" />
            Additional Information
          </h4>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tell us about your experience and why you want to be an affiliate
            </label>
            <textarea
              {...register('notes', {
                maxLength: {
                  value: 1000,
                  message: 'Notes must be less than 1000 characters'
                }
              })}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Share your marketing experience, audience size, or any relevant information..."
            />
            {errors.notes && (
              <p className="text-sm text-danger-600 mt-1">{errors.notes.message}</p>
            )}
            <p className="text-xs text-gray-500 mt-1">
              {watch('notes')?.length || 0}/1000 characters
            </p>
          </div>
        </div>

        {/* Commission Information */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">Commission Structure</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Base commission rate: 5%</li>
            <li>• Higher rates available for top performers</li>
            <li>• Commissions paid monthly (minimum $50 threshold)</li>
            <li>• Track referrals and earnings in real-time</li>
            <li>• Marketing materials provided</li>
          </ul>
        </div>

        {/* Terms and Agreement */}
        <div className="flex items-start">
          <input
            type="checkbox"
            {...register('agree_terms', { required: 'You must agree to the terms' })}
            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded mt-1"
          />
          <label className="ml-2 text-sm text-gray-700">
            I agree to the{' '}
            <a href="#" className="text-primary-600 hover:text-primary-500">
              Affiliate Program Terms and Conditions
            </a>
            {' '}and understand that my application will be reviewed before approval.
          </label>
        </div>
        {errors.agree_terms && (
          <p className="text-sm text-danger-600">{errors.agree_terms.message}</p>
        )}

        <Button
          type="submit"
          loading={loading}
          disabled={loading}
          className="w-full"
        >
          Submit Application
        </Button>
      </form>
    </Card>
  )
}

export default AffiliateRegistration