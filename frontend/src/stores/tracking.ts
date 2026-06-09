import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { api } from 'src/boot/axios'
import type {
  CustomList,
  CustomListCreate,
  CustomListEntriesReplaceRequest,
  ListEntry,
  ListEntryCreate,
  ListEntryHistoryItem,
  ListStats,
  ListEntryUpdate,
  UserListHistoryResponse,
  UserListResponse,
  WatchStatus,
} from 'src/types/tracking'

const statuses: WatchStatus[] = [
  'watching',
  'reading',
  'completed',
  'paused',
  'dropped',
  'plan_to_watch',
  'plan_to_read',
  'rewatching',
  'rereading',
]

export const useTrackingStore = defineStore('tracking', () => {
  const entries = ref<ListEntry[]>([])
  const customLists = ref<CustomList[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const byStatus = computed(() => {
    const grouped: Record<WatchStatus, ListEntry[]> = Object.fromEntries(
      statuses.map((status) => [status, []]),
    ) as Record<WatchStatus, ListEntry[]>

    for (const entry of entries.value) {
      grouped[entry.status].push(entry)
    }

    return grouped
  })

  async function fetchMyList(status?: WatchStatus): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const params: Record<string, string> = {}
      if (status) {
        params.status = status
      }
      const response = await api.get<UserListResponse>('/api/v1/lists/me', { params })
      entries.value = response.data.items ?? []
    } catch {
      error.value = 'Failed to load your list.'
      entries.value = []
    } finally {
      isLoading.value = false
    }
  }

  async function addToList(payload: ListEntryCreate): Promise<void> {
    await api.post('/api/v1/lists', payload)
    await fetchMyList()
  }

  async function updateEntry(mediaId: string, payload: ListEntryUpdate): Promise<void> {
    await api.patch(`/api/v1/lists/${mediaId}`, payload)

    const current = entries.value.find((entry) => entry.media_id === mediaId)
    if (current) {
      current.progress = payload.progress ?? current.progress
      current.score = payload.score ?? current.score
      current.status = payload.status ?? current.status
      current.notes = payload.notes ?? current.notes
    }
  }

  async function getEntryByMedia(mediaId: string): Promise<ListEntry | null> {
    try {
      const response = await api.get<ListEntry>(`/api/v1/lists/entries/${mediaId}`)
      return response.data
    } catch {
      return null
    }
  }

  async function createCustomList(payload: CustomListCreate): Promise<CustomList> {
    const response = await api.post<CustomList>('/api/v1/lists/custom', payload)
    const created = response.data
    customLists.value.unshift(created)
    return created
  }

  // -- Phase 5.3: History & Statistics --

  const history = ref<ListEntryHistoryItem[]>([])
  const historyIsLoading = ref(false)
  const historyError = ref<string | null>(null)

  const stats = computed<ListStats>(() => {
    const s: ListStats = {
      total: 0,
      watching: 0,
      reading: 0,
      completed: 0,
      paused: 0,
      dropped: 0,
      plan_to_watch: 0,
      plan_to_read: 0,
      rewatching: 0,
      rereading: 0,
    }
    for (const entry of entries.value) {
      s.total++
      s[entry.status]++
    }
    return s
  })

  async function fetchHistory(limit = 20): Promise<void> {
    historyIsLoading.value = true
    historyError.value = null
    try {
      const response = await api.get<UserListHistoryResponse>('/api/v1/lists/me/history', { params: { limit } })
      history.value = response.data.items ?? []
    } catch {
      historyError.value = 'Failed to load history.'
      history.value = []
    } finally {
      historyIsLoading.value = false
    }
  }

  async function replaceCustomListEntries(
    listId: string,
    payload: CustomListEntriesReplaceRequest,
  ): Promise<void> {
    await api.put(`/api/v1/lists/custom/${listId}/entries`, payload)
  }

  return {
    entries,
    customLists,
    isLoading,
    error,
    history,
    historyIsLoading,
    historyError,
    byStatus,
    stats,
    fetchMyList,
    addToList,
    updateEntry,
    getEntryByMedia,
    createCustomList,
    replaceCustomListEntries,
    fetchHistory,
  }
})
