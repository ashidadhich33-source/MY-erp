import axios from 'axios'

// Create axios instance
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API endpoints
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),
  refreshToken: (token) => api.post('/auth/refresh', { refresh_token: token }),
}

export const customersAPI = {
  getAll: (params) => api.get('/customers', { params }),
  getById: (id) => api.get(`/customers/${id}`),
  create: (customerData) => api.post('/customers', customerData),
  update: (id, customerData) => api.put(`/customers/${id}`, customerData),
  delete: (id) => api.delete(`/customers/${id}`),
  getKids: (customerId) => api.get(`/customers/${customerId}/kids`),
  addKid: (customerId, kidData) => api.post(`/customers/${customerId}/kids`, kidData),
  updateKid: (customerId, kidId, kidData) => api.put(`/customers/${customerId}/kids/${kidId}`, kidData),
  deleteKid: (customerId, kidId) => api.delete(`/customers/${customerId}/kids/${kidId}`),
}

export const loyaltyAPI = {
  getPoints: (customerId) => api.get(`/loyalty/points/${customerId}`),
  awardPoints: (data) => api.post('/loyalty/points/award', data),
  deductPoints: (data) => api.post('/loyalty/points/deduct', data),
  getTransactions: (customerId) => api.get(`/loyalty/transactions/${customerId}`),
  getTiers: () => api.get('/loyalty/tiers'),
  getCustomerTier: (customerId) => api.get(`/loyalty/customer-tier/${customerId}`),
  upgradeTier: (data) => api.post('/loyalty/upgrade-tier', data),
  getRewards: () => api.get('/rewards'),
  getAvailableRewards: (customerId) => api.get(`/rewards/available/${customerId}`),
  redeemReward: (data) => api.post('/rewards/redeem', data),
  getRewardHistory: (customerId) => api.get(`/rewards/history/${customerId}`),
}

export const affiliatesAPI = {
  register: (affiliateData) => api.post('/affiliates/register', affiliateData),
  getById: (id) => api.get(`/affiliates/${id}`),
  update: (id, affiliateData) => api.put(`/affiliates/${id}`, affiliateData),
  getAll: () => api.get('/affiliates'),
  getCommissions: (affiliateId) => api.get(`/affiliates/commissions/${affiliateId}`),
  approveCommission: (commissionId) => api.post(`/affiliates/commissions/approve`, { commission_id: commissionId }),
  getPayouts: () => api.get('/affiliates/payouts'),
  createPayout: (data) => api.post('/affiliates/payout', data),
}

export const whatsappAPI = {
  sendMessage: (data) => api.post('/whatsapp/send', data),
  webhook: (data) => api.post('/whatsapp/webhook', data),
  getHistory: (customerId) => api.get(`/whatsapp/history/${customerId}`),
  getTemplates: () => api.get('/whatsapp/templates'),
}

export const analyticsAPI = {
  getDashboard: () => api.get('/analytics/dashboard'),
  getCustomers: (params) => api.get('/analytics/customers', { params }),
  getLoyalty: (params) => api.get('/analytics/loyalty', { params }),
  getAffiliates: (params) => api.get('/analytics/affiliates', { params }),
  getRevenue: (params) => api.get('/analytics/revenue', { params }),
}

export default api