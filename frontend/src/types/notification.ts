export interface NotificationItem {
  id: string
  user_id: string
  type: string
  title: string
  body: string | null
  action_url: string | null
  related_media_id: string | null
  related_user_id: string | null
  is_read: boolean
  read_at: string | null
  sent_at: string | null
  created_at: string
}

export interface NotificationListResponse {
  items: NotificationItem[]
  total: number
  limit: number
  offset: number
}

export interface NotificationMarkReadResponse {
  updated_count: number
}

export interface NotificationPreferences {
  user_id: string
  new_episode: boolean
  new_chapter: boolean
  friend_activity: boolean
  recommendations: boolean
  watch_party_invite: boolean
  watch_party_reminder: boolean
  discord_webhook: string | null
  telegram_chat_id: string | null
  email_enabled: boolean
  push_enabled: boolean
  updated_at: string
}

export interface NotificationPreferencesUpdateRequest {
  new_episode?: boolean
  new_chapter?: boolean
  friend_activity?: boolean
  recommendations?: boolean
  watch_party_invite?: boolean
  watch_party_reminder?: boolean
  discord_webhook?: string | null
  telegram_chat_id?: string | null
  email_enabled?: boolean
  push_enabled?: boolean
}
