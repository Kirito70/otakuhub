export type WatchStatus =
  | 'watching'
  | 'reading'
  | 'completed'
  | 'paused'
  | 'dropped'
  | 'plan_to_watch'
  | 'plan_to_read'
  | 'rewatching'
  | 'rereading'

export interface ListEntry {
  id: string
  media_id: string
  status: WatchStatus
  progress: number
  score?: number | null
  notes?: string | null
  title?: string
  cover_image_medium?: string | null
}

export interface UserListResponse {
  items: ListEntry[]
  total: number
  limit: number
  offset: number
}

export interface ListEntryCreate {
  media_id: string
  status: WatchStatus
  progress?: number
  score?: number
  notes?: string
}

export interface ListEntryUpdate {
  status?: WatchStatus
  progress?: number
  score?: number | null
  notes?: string
}

export interface CustomList {
  id: string
  name: string
  description?: string | null
  is_public: boolean
  cover_image?: string | null
  sort_order: number
}

export interface CustomListCreate {
  name: string
  description?: string
  is_public?: boolean
  cover_image?: string
  sort_order?: number
}

export interface CustomListEntriesReplaceRequest {
  entries: Array<{
    media_id: string
    sort_order?: number
    note?: string
  }>
}

// -- Phase 5.3: History & Statistics --

export interface ListEntryHistoryItem {
  id: string
  entry_id: string
  media_id: string
  event_type: string
  old_status?: WatchStatus | null
  new_status?: WatchStatus | null
  old_progress?: number | null
  new_progress?: number | null
  old_score?: number | null
  new_score?: number | null
  note?: string | null
  created_at: string
}

export interface UserListHistoryResponse {
  items: ListEntryHistoryItem[]
  total: number
  limit: number
}

export interface ListStats {
  total: number
  watching: number
  reading: number
  completed: number
  paused: number
  dropped: number
  plan_to_watch: number
  plan_to_read: number
  rewatching: number
  rereading: number
}
