import axios from 'axios'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { secureStorage, type TokenPair } from 'src/services/storage'

interface AuthResponse {
  access_token: string
  refresh_token: string
}

export interface UserProfile {
  id: string
  username: string
  display_name: string | null
  email: string
  avatar_url: string | null
  bio: string | null
  timezone: string
  is_active: boolean
  created_at: string
  updated_at: string
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
  const user = ref<UserProfile | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => Boolean(accessToken.value))
  const displayName = computed(() => user.value?.display_name ?? user.value?.username ?? 'User')
  const avatarInitial = computed(() => (displayName.value.charAt(0) ?? 'U').toUpperCase())

  async function hydrateFromStorage(): Promise<void> {
    accessToken.value = await secureStorage.getAccessToken()
    refreshToken.value = await secureStorage.getRefreshToken()
  }

  async function fetchProfile(): Promise<void> {
    if (!accessToken.value) {
      user.value = null
      return
    }
    try {
      const response = await authApi.get<UserProfile>('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${accessToken.value}` },
      })
      user.value = response.data
    } catch {
      user.value = null
    }
  }

  async function setTokens(tokens: TokenPair): Promise<void> {
    accessToken.value = tokens.accessToken
    refreshToken.value = tokens.refreshToken
    await secureStorage.setTokens(tokens)
  }

  async function clearSession(): Promise<void> {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
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
      await fetchProfile()
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
      // Register returns UserProfile (no tokens). Login immediately to get tokens.
      await authApi.post('/api/v1/auth/register', payload)
      // Now log in to obtain tokens
      const loginRes = await authApi.post<AuthResponse>('/api/v1/auth/login', {
        username: payload.username,
        password: payload.password,
      })
      await setTokens({
        accessToken: loginRes.data.access_token,
        refreshToken: loginRes.data.refresh_token,
      })
      await fetchProfile()
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
    try {
      if (refreshToken.value) {
        await authApi.post('/api/v1/auth/logout', {
          refresh_token: refreshToken.value,
        })
      }
    } catch {
      // Logout best-effort: clear local session regardless
    } finally {
      await clearSession()
    }
  }

  return {
    accessToken,
    refreshToken,
    user,
    isLoading,
    error,
    isAuthenticated,
    displayName,
    avatarInitial,
    hydrateFromStorage,
    fetchProfile,
    setTokens,
    clearSession,
    login,
    register,
    refreshAccessToken,
    logout,
  }
})
