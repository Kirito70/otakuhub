import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { boot } from 'quasar/wrappers'
import type { Router } from 'vue-router'

import { useAuthStore } from 'src/stores/auth'

const api = axios.create({
  baseURL: process.env.API_BASE_URL,
  timeout: 15000,
})

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

/** Routes that are allowed to stay on after a 401 without redirecting to login. */
const PUBLIC_AUTH_ROUTES = new Set(['login', 'register', 'setup'])

function redirectToLoginOnAuthFailure(router: Router): void {
  const currentRouteName = router.currentRoute.value?.name
  if (typeof currentRouteName === 'string' && PUBLIC_AUTH_ROUTES.has(currentRouteName)) {
    return // already on a public auth route — no redirect loop
  }
  router.push({ name: 'login' })
}

export default boot(({ app, store, router }) => {
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
        // Refresh failed — session is invalid. Redirect to login.
        redirectToLoginOnAuthFailure(router)
        return Promise.reject(error)
      }

      config.headers.Authorization = `Bearer ${newAccessToken}`
      return api(config)
    },
  )

  void authStore.hydrateFromStorage()
})

export { api }
