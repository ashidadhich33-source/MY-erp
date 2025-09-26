import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  affiliates: [],
  currentAffiliate: null,
  commissions: [],
  loading: false,
  error: null,
}

const affiliatesSlice = createSlice({
  name: 'affiliates',
  initialState,
  reducers: {
    setAffiliates: (state, action) => {
      state.affiliates = action.payload
    },
    setCurrentAffiliate: (state, action) => {
      state.currentAffiliate = action.payload
    },
    setCommissions: (state, action) => {
      state.commissions = action.payload
    },
    clearError: (state) => {
      state.error = null
    },
  },
})

export const { setAffiliates, setCurrentAffiliate, setCommissions, clearError } = affiliatesSlice.actions

export default affiliatesSlice.reducer