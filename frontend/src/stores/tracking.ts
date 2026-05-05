import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { api } from 'src/boot/axios'
import type {
  CustomList,
  CustomListCreate,
  CustomListEntriesReplaceRequest,
  ListEntry,
  ListEntryCreate,
  ListEntryUpdate,
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

  async function fetchMyList(): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.get<UserListResponse>('/api/v1/lists/me')
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

  async function createCustomList(payload: CustomListCreate): Promise<CustomList> {
    const response = await api.post<CustomList>('/api/v1/lists/custom', payload)
    const created = response.data
    customLists.value.unshift(created)
    return created
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
    byStatus,
    fetchMyList,
    addToList,
    updateEntry,
    createCustomList,
    replaceCustomListEntries,
  }
})
