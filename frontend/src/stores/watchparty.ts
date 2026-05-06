import { defineStore } from 'pinia'
import { ref } from 'vue'

import { api } from 'src/boot/axios'
import type { WatchParty, WatchPartyCreateRequest, WatchPartyListResponse } from 'src/types/watchparty'

export const useWatchPartyStore = defineStore('watchparty', () => {
  const parties = ref<WatchParty[]>([])
  const total = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchUpcoming(groupId?: string): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.get<WatchPartyListResponse>('/api/v1/watchparty', {
        params: groupId ? { group_id: groupId } : undefined,
      })
      parties.value = response.data.items ?? []
      total.value = response.data.total ?? parties.value.length
    } catch {
      parties.value = []
      total.value = 0
      error.value = 'Failed to load upcoming watch parties.'
    } finally {
      isLoading.value = false
    }
  }

  async function createWatchParty(payload: WatchPartyCreateRequest): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      await api.post('/api/v1/watchparty', payload)
      await fetchUpcoming(payload.group_id)
    } catch {
      error.value = 'Failed to create watch party.'
      throw new Error('create_watchparty_failed')
    } finally {
      isLoading.value = false
    }
  }

  async function rsvpToParty(partyId: string, status: 'pending' | 'attending' | 'declined'): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      await api.post(`/api/v1/watchparty/${partyId}/rsvp`, { status })
      await fetchUpcoming()
    } catch {
      error.value = 'Failed to submit RSVP.'
      throw new Error('rsvp_failed')
    } finally {
      isLoading.value = false
    }
  }

  return {
    parties,
    total,
    isLoading,
    error,
    fetchUpcoming,
    createWatchParty,
    rsvpToParty,
  }
})
