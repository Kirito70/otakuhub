import { flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { useWatchPartyStore } from '../watchparty'

const { mockGet, mockPost } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
}))

vi.mock('src/boot/axios', () => ({
  api: {
    get: mockGet,
    post: mockPost,
  },
}))

const sampleUpcoming = [
  { id: 'wp1', title: 'Naruto EP220', media_id: 'm1', group_id: 'g1', host_user_id: 'u1', scheduled_at: '2026-06-10T18:00:00Z', status: 'scheduled', episode_number: 220 },
  { id: 'wp2', title: 'One Piece EP1100', media_id: 'm2', group_id: 'g1', host_user_id: 'u1', scheduled_at: '2026-06-12T18:00:00Z', status: 'scheduled', episode_number: 1100 },
]

const samplePast = [
  { id: 'wp3', title: 'Bleach EP380', media_id: 'm3', group_id: 'g1', host_user_id: 'u2', scheduled_at: '2026-06-01T18:00:00Z', status: 'completed', episode_number: 380 },
]

const sampleDetail = { id: 'wp1', title: 'Naruto EP220', media_id: 'm1', group_id: 'g1', host_user_id: 'u1', scheduled_at: '2026-06-10T18:00:00Z', status: 'scheduled', episode_number: 220, notes: 'Bring snacks!' }

const sampleRsvps = [
  { party_id: 'wp1', user_id: 'u1', status: 'attending' },
  { party_id: 'wp1', user_id: 'u2', status: 'pending' },
]

describe('useWatchPartyStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetchUpcoming loads parties', async () => {
    mockGet.mockResolvedValue({ data: { items: sampleUpcoming, total: 2 } })
    const store = useWatchPartyStore()

    await store.fetchUpcoming()
    expect(mockGet).toHaveBeenCalledWith('/api/v1/watchparty', expect.any(Object))
    expect(store.parties).toHaveLength(2)
    expect(store.total).toBe(2)
    expect(store.isLoading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('fetchUpcoming handles error', async () => {
    mockGet.mockRejectedValue(new Error('API error'))
    const store = useWatchPartyStore()

    await store.fetchUpcoming()
    expect(store.error).toBe('Failed to load upcoming watch parties.')
    expect(store.parties).toHaveLength(0)
  })

  it('fetchUpcoming passes group_id param', async () => {
    mockGet.mockResolvedValue({ data: { items: [], total: 0 } })
    const store = useWatchPartyStore()

    await store.fetchUpcoming('g1')
    expect(mockGet).toHaveBeenCalledWith('/api/v1/watchparty', expect.objectContaining({
      params: { group_id: 'g1' },
    }))
  })

  it('fetchPast loads past parties', async () => {
    mockGet.mockResolvedValue({ data: { items: samplePast, total: 1 } })
    const store = useWatchPartyStore()

    await store.fetchPast()
    expect(mockGet).toHaveBeenCalledWith('/api/v1/watchparty/past', expect.any(Object))
    expect(store.pastParties).toHaveLength(1)
    expect(store.pastIsLoading).toBe(false)
  })

  it('fetchPast handles error', async () => {
    mockGet.mockRejectedValue(new Error('API error'))
    const store = useWatchPartyStore()

    await store.fetchPast()
    expect(store.pastError).toBe('Failed to load past watch parties.')
    expect(store.pastParties).toHaveLength(0)
  })

  it('fetchPartyDetail loads detail', async () => {
    mockGet.mockResolvedValue({ data: sampleDetail })
    const store = useWatchPartyStore()

    await store.fetchPartyDetail('wp1')
    expect(mockGet).toHaveBeenCalledWith('/api/v1/watchparty/wp1')
    expect(store.currentDetail?.title).toBe('Naruto EP220')
    expect(store.detailIsLoading).toBe(false)
  })

  it('fetchPartyDetail handles error', async () => {
    mockGet.mockRejectedValue(new Error('API error'))
    const store = useWatchPartyStore()

    await store.fetchPartyDetail('wp1')
    expect(store.detailError).toBe('Failed to load party details.')
    expect(store.currentDetail).toBeNull()
  })

  it('fetchRsvps loads RSVPs', async () => {
    mockGet.mockResolvedValue({ data: { items: sampleRsvps } })
    const store = useWatchPartyStore()

    await store.fetchRsvps('wp1')
    expect(mockGet).toHaveBeenCalledWith('/api/v1/watchparty/wp1/rsvps')
    expect(store.rsvps).toHaveLength(2)
  })

  it('fetchRsvps handles error', async () => {
    mockGet.mockRejectedValue(new Error('API error'))
    const store = useWatchPartyStore()

    await store.fetchRsvps('wp1')
    expect(store.rsvpsError).toBe('Failed to load RSVPs.')
    expect(store.rsvps).toHaveLength(0)
  })

  it('createWatchParty calls POST then refetches', async () => {
    mockPost.mockResolvedValue({ data: {} })
    mockGet.mockResolvedValue({ data: { items: sampleUpcoming, total: 2 } })
    const store = useWatchPartyStore()

    await store.createWatchParty({ media_id: 'm1', group_id: 'g1', scheduled_at: '2026-06-15T18:00:00Z' })
    expect(mockPost).toHaveBeenCalledWith('/api/v1/watchparty', expect.objectContaining({ media_id: 'm1' }))
    expect(mockGet).toHaveBeenCalled() // refetch
  })

  it('createWatchParty handles error and throws', async () => {
    mockPost.mockRejectedValue(new Error('API error'))
    const store = useWatchPartyStore()

    await expect(store.createWatchParty({ media_id: 'm1', group_id: 'g1', scheduled_at: '2026-06-15T18:00:00Z' }))
      .rejects.toThrow('create_watchparty_failed')
    expect(store.error).toBe('Failed to create watch party.')
  })

  it('rsvpToParty calls POST then refetches', async () => {
    mockPost.mockResolvedValue({ data: {} })
    mockGet.mockResolvedValue({ data: { items: sampleUpcoming, total: 2 } })
    const store = useWatchPartyStore()

    await store.rsvpToParty('wp1', 'attending')
    expect(mockPost).toHaveBeenCalledWith('/api/v1/watchparty/wp1/rsvp', { status: 'attending' })
  })

  it('rsvpToParty handles error and throws', async () => {
    mockPost.mockRejectedValue(new Error('API error'))
    const store = useWatchPartyStore()

    await expect(store.rsvpToParty('wp1', 'attending'))
      .rejects.toThrow('rsvp_failed')
    expect(store.error).toBe('Failed to submit RSVP.')
  })
})
