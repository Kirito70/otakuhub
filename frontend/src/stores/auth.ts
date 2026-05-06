import axios from 'axios'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { secureStorage, type TokenPair } from 'src/services/storage'

interface AuthResponse {
  access_token: string
  refresh_token: string
}

interface RegisterPayload {
  username: string
  email: string
  password: string
}

interface LoginPayload {
  username: string
  password: string
}

const authApi = axios.create({
  baseURL: process.env.API_BASE_URL,
  timeout: 15000,
})

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => Boolean(accessToken.value))

  async function hydrateFromStorage(): Promise<void> {
    accessToken.value = await secureStorage.getAccessToken()
    refreshToken.value = await secureStorage.getRefreshToken()
  }

  async function setTokens(tokens: TokenPair): Promise<void> {
    accessToken.value = tokens.accessToken
    refreshToken.value = tokens.refreshToken
    await secureStorage.setTokens(tokens)
  }

  async function clearSession(): Promise<void> {
    accessToken.value = null
    refreshToken.value = null
    await secureStorage.clearTokens()
  }

  async function login(payload: LoginPayload): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.post<AuthResponse>('/api/v1/auth/login', payload)
      await setTokens({
        accessToken: response.data.access_token,
        refreshToken: response.data.refresh_token,
      })
    } catch {
      error.value = 'Invalid credentials. Please try again.'
      throw new Error(error.value)
    } finally {
      isLoading.value = false
    }
  }

  async function register(payload: RegisterPayload): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.post<AuthResponse>('/api/v1/auth/register', payload)
      await setTokens({
        accessToken: response.data.access_token,
        refreshToken: response.data.refresh_token,
      })
    } catch {
      error.value = 'Registration failed. Please check your inputs.'
      throw new Error(error.value)
    } finally {
      isLoading.value = false
    }
  }

  async function refreshAccessToken(): Promise<string | null> {
    if (!refreshToken.value) {
      return null
    }

    try {
      const response = await authApi.post<AuthResponse>('/api/v1/auth/refresh', {
        refresh_token: refreshToken.value,
      })

      await setTokens({
        accessToken: response.data.access_token,
        refreshToken: response.data.refresh_token,
      })

      return response.data.access_token
    } catch {
      await clearSession()
      return null
    }
  }

  async function logout(): Promise<void> {
    await clearSession()
  }

  return {
    accessToken,
    refreshToken,
    isLoading,
    error,
    isAuthenticated,
    hydrateFromStorage,
    setTokens,
    clearSession,
    login,
    register,
    refreshAccessToken,
    logout,
  }
})
