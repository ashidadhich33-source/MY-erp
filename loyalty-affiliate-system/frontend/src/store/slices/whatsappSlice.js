import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  messages: [],
  templates: [],
  deliveryStatus: {},
  loading: false,
  error: null,
}

const whatsappSlice = createSlice({
  name: 'whatsapp',
  initialState,
  reducers: {
    setMessages: (state, action) => {
      state.messages = action.payload
    },
    addMessage: (state, action) => {
      state.messages.unshift(action.payload)
    },
    setTemplates: (state, action) => {
      state.templates = action.payload
    },
    setDeliveryStatus: (state, action) => {
      state.deliveryStatus = { ...state.deliveryStatus, ...action.payload }
    },
    clearError: (state) => {
      state.error = null
    },
  },
})

export const { setMessages, addMessage, setTemplates, setDeliveryStatus, clearError } = whatsappSlice.actions

export default whatsappSlice.reducer