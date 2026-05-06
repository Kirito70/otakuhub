export type PartyStatus = 'scheduled' | 'live' | 'completed' | 'cancelled'

export interface WatchParty {
  id: string
  group_id: string
  host_user_id: string
  media_id: string
  episode_number: number | null
  title: string | null
  scheduled_at: string
  status: PartyStatus
  stream_url: string | null
  sync_url: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface WatchPartyListResponse {
  items: WatchParty[]
  total: number
  limit: number
  offset: number
}

export interface WatchPartyCreateRequest {
  group_id: string
  media_id: string
  scheduled_at: string
  title?: string
  episode_number?: number
  stream_url?: string
  sync_url?: string
  notes?: string
}
