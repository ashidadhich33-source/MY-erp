import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  points: 0,
  tier: null,
  transactions: [],
  rewards: [],
  loading: false,
  error: null,
}

const loyaltySlice = createSlice({
  name: 'loyalty',
  initialState,
  reducers: {
    setPoints: (state, action) => {
      state.points = action.payload
    },
    setTier: (state, action) => {
      state.tier = action.payload
    },
    addTransaction: (state, action) => {
      state.transactions.unshift(action.payload)
    },
    setTransactions: (state, action) => {
      state.transactions = action.payload
    },
    setRewards: (state, action) => {
      state.rewards = action.payload
    },
    clearError: (state) => {
      state.error = null
    },
  },
})

export const { setPoints, setTier, addTransaction, setTransactions, setRewards, clearError } = loyaltySlice.actions

export default loyaltySlice.reducer