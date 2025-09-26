import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  dashboard: null,
  customers: null,
  loyalty: null,
  affiliates: null,
  revenue: null,
  loading: false,
  error: null,
}

const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {
    setDashboard: (state, action) => {
      state.dashboard = action.payload
    },
    setCustomers: (state, action) => {
      state.customers = action.payload
    },
    setLoyalty: (state, action) => {
      state.loyalty = action.payload
    },
    setAffiliates: (state, action) => {
      state.affiliates = action.payload
    },
    setRevenue: (state, action) => {
      state.revenue = action.payload
    },
    clearError: (state) => {
      state.error = null
    },
  },
})

export const { setDashboard, setCustomers, setLoyalty, setAffiliates, setRevenue, clearError } = analyticsSlice.actions

export default analyticsSlice.reducer