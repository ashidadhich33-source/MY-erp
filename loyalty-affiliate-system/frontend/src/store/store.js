import { configureStore } from '@reduxjs/toolkit'
import authSlice from './slices/authSlice'
import uiSlice from './slices/uiSlice'
import customersSlice from './slices/customersSlice'
import loyaltySlice from './slices/loyaltySlice'
import affiliatesSlice from './slices/affiliatesSlice'
import whatsappSlice from './slices/whatsappSlice'
import analyticsSlice from './slices/analyticsSlice'

export const store = configureStore({
  reducer: {
    auth: authSlice,
    ui: uiSlice,
    customers: customersSlice,
    loyalty: loyaltySlice,
    affiliates: affiliatesSlice,
    whatsapp: whatsappSlice,
    analytics: analyticsSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
})

export default store