import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Provider } from 'react-redux'
import { Toaster } from 'react-hot-toast'
import { store } from './store/store'
import DashboardLayout from './layouts/DashboardLayout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import ProfilePage from './pages/ProfilePage'
import CustomersPage from './pages/CustomersPage'
import LoyaltyPage from './pages/LoyaltyPage'
import AffiliatesPage from './pages/AffiliatesPage'
import WhatsAppPage from './pages/WhatsAppPage'
import AnalyticsPage from './pages/AnalyticsPage'
import NotFoundPage from './pages/NotFoundPage'
import './App.css'

function App() {
  return (
    <Provider store={store}>
      <Router>
        <div className="App">
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                duration: 3000,
                theme: {
                  primary: '#22c55e',
                  secondary: '#000',
                },
              },
              error: {
                duration: 4000,
                theme: {
                  primary: '#ef4444',
                  secondary: '#000',
                },
              },
            }}
          />
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Protected routes */}
            <Route path="/" element={<DashboardLayout />}>
              <Route index element={<DashboardPage />} />
              <Route path="profile" element={<ProfilePage />} />
              <Route path="customers" element={<CustomersPage />} />
              <Route path="loyalty" element={<LoyaltyPage />} />
              <Route path="affiliates" element={<AffiliatesPage />} />
              <Route path="whatsapp" element={<WhatsAppPage />} />
              <Route path="analytics" element={<AnalyticsPage />} />
            </Route>

            {/* 404 page */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </div>
      </Router>
    </Provider>
  )
}

export default App