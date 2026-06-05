import { defineStore } from 'pinia'
import { ref, type Ref } from 'vue'

import { api } from 'src/boot/axios'
import type {
  WatchParty,
  WatchPartyCreateRequest,
  WatchPartyDetail,
  WatchPartyListResponse,
  WatchPartyRsvp,
  WatchPartyRsvpListResponse,
} from 'src/types/watchparty'

export const useWatchPartyStore = defineStore('watchparty', () => {
  const parties = ref<WatchParty[]>([]) as Ref<WatchParty[]>
  const total = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const pastParties = ref<WatchParty[]>([]) as Ref<WatchParty[]>
  const pastTotal = ref(0)
  const pastIsLoading = ref(false)
  const pastError = ref<string | null>(null)

  const currentDetail = ref<WatchPartyDetail | null>(null)
  const detailIsLoading = ref(false)
  const detailError = ref<string | null>(null)

  const rsvps = ref<WatchPartyRsvp[]>([]) as Ref<WatchPartyRsvp[]>
  const rsvpsIsLoading = ref(false)
  const rsvpsError = ref<string | null>(null)

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

  async function fetchPast(groupId?: string): Promise<void> {
    pastIsLoading.value = true
    pastError.value = null

    try {
      const response = await api.get<WatchPartyListResponse>('/api/v1/watchparty/past', {
        params: groupId ? { group_id: groupId } : undefined,
      })
      pastParties.value = response.data.items ?? []
      pastTotal.value = response.data.total ?? pastParties.value.length
    } catch {
      pastParties.value = []
      pastTotal.value = 0
      pastError.value = 'Failed to load past watch parties.'
    } finally {
      pastIsLoading.value = false
    }
  }

  async function fetchPartyDetail(partyId: string): Promise<void> {
    detailIsLoading.value = true
    detailError.value = null
    currentDetail.value = null

    try {
      const { data } = await api.get<WatchPartyDetail>(`/api/v1/watchparty/${partyId}`)
      currentDetail.value = data
    } catch {
      detailError.value = 'Failed to load party details.'
    } finally {
      detailIsLoading.value = false
    }
  }

  async function fetchRsvps(partyId: string): Promise<void> {
    rsvpsIsLoading.value = true
    rsvpsError.value = null

    try {
      const { data } = await api.get<WatchPartyRsvpListResponse>(`/api/v1/watchparty/${partyId}/rsvps`)
      rsvps.value = data.items ?? []
    } catch {
      rsvpsError.value = 'Failed to load RSVPs.'
    } finally {
      rsvpsIsLoading.value = false
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
    // Upcoming
    parties,
    total,
    isLoading,
    error,
    fetchUpcoming,
    // Past
    pastParties,
    pastTotal,
    pastIsLoading,
    pastError,
    fetchPast,
    // Detail
    currentDetail,
    detailIsLoading,
    detailError,
    fetchPartyDetail,
    // RSVPs
    rsvps,
    rsvpsIsLoading,
    rsvpsError,
    fetchRsvps,
    // Actions
    createWatchParty,
    rsvpToParty,
  }
})
