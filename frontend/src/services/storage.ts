import type { TokenPair } from 'src/types/auth'

export interface SecureStorage {
  getAccessToken(): Promise<string | null>
  getRefreshToken(): Promise<string | null>
  setTokens(tokens: TokenPair): Promise<void>
  clearTokens(): Promise<void>
}

const ACCESS_TOKEN_KEY = 'otakuhub.access_token'
const REFRESH_TOKEN_KEY = 'otakuhub.refresh_token'

class BrowserStorageAdapter implements SecureStorage {
  async getAccessToken(): Promise<string | null> {
    return localStorage.getItem(ACCESS_TOKEN_KEY)
  }

  async getRefreshToken(): Promise<string | null> {
    return localStorage.getItem(REFRESH_TOKEN_KEY)
  }

  async setTokens(tokens: TokenPair): Promise<void> {
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.accessToken)
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refreshToken)
  }

  async clearTokens(): Promise<void> {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  }
}

export const secureStorage: SecureStorage = new BrowserStorageAdapter()
