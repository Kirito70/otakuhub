import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { boot } from 'quasar/wrappers'

import { useAuthStore } from 'src/stores/auth'

const api = axios.create({
  baseURL: process.env.API_BASE_URL,
  timeout: 15000,
})

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

export default boot(({ store }) => {
  const authStore = useAuthStore(store)

  api.interceptors.request.use((config) => {
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }

    return config
  })

  api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const config = error.config as RetryableRequestConfig | undefined

      if (!config || config._retry || error.response?.status !== 401) {
        return Promise.reject(error)
      }

      config._retry = true

      const newAccessToken = await authStore.refreshAccessToken()

      if (!newAccessToken) {
        return Promise.reject(error)
      }

      config.headers.Authorization = `Bearer ${newAccessToken}`
      return api(config)
    },
  )

  void authStore.hydrateFromStorage()
})

export { api }
