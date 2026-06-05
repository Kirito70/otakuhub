/** Token pair returned from auth endpoints */
export interface TokenPair {
  accessToken: string
  refreshToken: string
}

/** Backend auth response shape (snake_case from API) */
export interface AuthResponse {
  access_token: string
  refresh_token: string
}

export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload {
  username: string
  email: string
  password: string
}

/** Authenticated user profile — always fully populated */
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

export interface PasswordChangeRequest {
  current_password: string
  new_password: string
}

export interface UserProfileUpdateRequest {
  display_name?: string | null
  avatar_url?: string | null
  bio?: string | null
  timezone?: string | null
}
