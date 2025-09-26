import { useState } from 'react'
import { Outlet, Navigate, useLocation } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import {
  LayoutDashboard,
  Users,
  Gift,
  UserCheck,
  MessageCircle,
  BarChart3,
  Settings,
  Menu,
  X,
  LogOut,
  User
} from 'lucide-react'
import { toggleSidebar, setSidebarOpen } from '../store/slices/uiSlice'
import { logout } from '../store/slices/authSlice'
import Button from '../components/ui/Button'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Customers', href: '/customers', icon: Users },
  { name: 'Loyalty', href: '/loyalty', icon: Gift },
  { name: 'Affiliates', href: '/affiliates', icon: UserCheck },
  { name: 'WhatsApp', href: '/whatsapp', icon: MessageCircle },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
]

const DashboardLayout = () => {
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const { sidebarOpen } = useSelector((state) => state.ui)
  const { user, isAuthenticated } = useSelector((state) => state.auth)
  const dispatch = useDispatch()
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  const handleLogout = async () => {
    dispatch(logout())
  }

  const closeSidebar = () => {
    dispatch(setSidebarOpen(false))
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={closeSidebar}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">Loyalty System</h1>
          <button
            onClick={closeSidebar}
            className="p-1 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 lg:hidden"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <nav className="mt-5 px-2 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <a
                key={item.name}
                href={item.href}
                onClick={closeSidebar}
                className={`
                  group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors duration-200
                  ${isActive
                    ? 'bg-primary-100 text-primary-900'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }
                `}
              >
                <item.icon className={`mr-3 h-5 w-5 ${isActive ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500'}`} />
                {item.name}
              </a>
            )
          })}
        </nav>
      </div>

      {/* Main content */}
      <div className="lg:pl-64 flex flex-col flex-1">
        {/* Top navigation */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
            <button
              onClick={() => dispatch(toggleSidebar())}
              className="p-1 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 lg:hidden"
            >
              <Menu className="h-6 w-6" />
            </button>

            <div className="flex items-center ml-auto space-x-4">
              {/* User menu */}
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center space-x-2 p-1 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
                >
                  <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <User className="h-4 w-4 text-primary-600" />
                  </div>
                  <span className="text-sm font-medium text-gray-700">{user?.name || 'User'}</span>
                </button>

                {userMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200">
                    <a
                      href="/profile"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      Profile
                    </a>
                    <a
                      href="/settings"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      Settings
                    </a>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      <LogOut className="inline h-4 w-4 mr-2" />
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default DashboardLayout