import { useSelector } from 'react-redux'
import { User, Mail, Phone, Calendar } from 'lucide-react'
import Card from '../components/ui/Card'

const ProfilePage = () => {
  const { user } = useSelector((state) => state.auth)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
        <p className="mt-1 text-sm text-gray-600">
          Manage your account settings and preferences.
        </p>
      </div>

      <Card>
        <h2 className="text-lg font-medium text-gray-900 mb-4">Personal Information</h2>
        <div className="space-y-4">
          <div className="flex items-center space-x-3">
            <User className="h-5 w-5 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900">{user?.name || 'User Name'}</p>
              <p className="text-sm text-gray-500">Full Name</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Mail className="h-5 w-5 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900">{user?.email || 'user@example.com'}</p>
              <p className="text-sm text-gray-500">Email Address</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Phone className="h-5 w-5 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900">{user?.phone || '+1 (555) 123-4567'}</p>
              <p className="text-sm text-gray-500">Phone Number</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Calendar className="h-5 w-5 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900">January 1, 2024</p>
              <p className="text-sm text-gray-500">Member Since</p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default ProfilePage