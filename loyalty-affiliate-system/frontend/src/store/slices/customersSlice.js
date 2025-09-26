import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { api } from './authSlice'

// Async thunks
export const fetchCustomers = createAsyncThunk(
  'customers/fetchCustomers',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await api.get('/customers', { params })
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch customers')
    }
  }
)

export const createCustomer = createAsyncThunk(
  'customers/createCustomer',
  async (customerData, { rejectWithValue }) => {
    try {
      const response = await api.post('/customers', customerData)
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to create customer')
    }
  }
)

const initialState = {
  customers: [],
  currentCustomer: null,
  loading: false,
  error: null,
  pagination: {
    page: 1,
    limit: 10,
    total: 0,
    totalPages: 0,
  },
  filters: {},
}

const customersSlice = createSlice({
  name: 'customers',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    setFilters: (state, action) => {
      state.filters = action.payload
    },
    clearFilters: (state) => {
      state.filters = {}
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCustomers.pending, (state) => {
        state.loading = true
      })
      .addCase(fetchCustomers.fulfilled, (state, action) => {
        state.loading = false
        state.customers = action.payload.data || action.payload
        state.pagination = action.payload.pagination || state.pagination
      })
      .addCase(fetchCustomers.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
      .addCase(createCustomer.fulfilled, (state, action) => {
        state.customers.unshift(action.payload)
      })
  },
})

export const { clearError, setFilters, clearFilters } = customersSlice.actions

export default customersSlice.reducer