/** Social feed activity item from list_entry_history */
export interface FeedActivityItem {
  id: string
  entry_id: string
  user_id: string
  media_id: string
  event_type: string
  old_status?: string | null
  new_status?: string | null
  old_progress?: number | null
  new_progress?: number | null
  old_score?: number | null
  new_score?: number | null
  note?: string | null
  created_at: string
}

export interface SocialFeedResponse {
  items: FeedActivityItem[]
  total: number
  limit: number
  offset: number
}

/** Recommendation from another group member */
export interface Recommendation {
  id: string
  from_user_id: string
  to_user_id: string
  media_id: string
  message?: string | null
  is_acknowledged: boolean
  acknowledged_at?: string | null
  created_at: string
  updated_at: string
}

export interface RecommendationInboxResponse {
  items: Recommendation[]
  total: number
  limit: number
  offset: number
}

export interface RecommendationSentResponse {
  items: Recommendation[]
  total: number
  limit: number
  offset: number
}

export interface RecommendationCreateRequest {
  to_user_id: string
  media_id: string
  message?: string | null
}

/** Discussion thread for a media entry */
export interface Discussion {
  id: string
  media_id: string
  group_id: string
  user_id: string
  title?: string | null
  body: string
  has_spoilers: boolean
  episode_number?: number | null
  chapter_number?: number | null
  created_at: string
  updated_at: string
}

export interface DiscussionListResponse {
  items: Discussion[]
  total: number
  limit: number
  offset: number
}

export interface DiscussionCreateRequest {
  media_id: string
  group_id: string
  title?: string | null
  body: string
  has_spoilers?: boolean
  episode_number?: number | null
  chapter_number?: number | null
}

/** Reply under a discussion thread */
export interface DiscussionReply {
  id: string
  discussion_id: string
  user_id: string
  parent_reply_id?: string | null
  body: string
  has_spoilers: boolean
  created_at: string
  updated_at: string
}

export interface DiscussionReplyListResponse {
  items: DiscussionReply[]
  total: number
  limit: number
  offset: number
}

export interface DiscussionReplyCreateRequest {
  body: string
  has_spoilers?: boolean
  parent_reply_id?: string | null
}

/** Generic paginated response helper */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

/** User profile (for profile page) */
export interface UserProfile {
  id: string
  username: string
  display_name?: string | null
  email: string
  avatar_url?: string | null
  bio?: string | null
  timezone: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface UserProfileUpdateRequest {
  display_name?: string | null
  avatar_url?: string | null
  bio?: string | null
  timezone?: string | null
}

export interface PasswordChangeRequest {
  current_password: string
  new_password: string
}

/** User settings (theme/language/timezone) */
export interface UserSettings {
  user_id: string
  theme: string
  language: string
  timezone: string
  created_at: string
  updated_at: string
}

export interface UserSettingsUpdateRequest {
  theme?: string
  language?: string
  timezone?: string
}
