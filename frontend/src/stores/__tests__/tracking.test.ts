import { flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { useTrackingStore } from '../tracking'

const { mockGet, mockPost, mockPatch } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
  mockPatch: vi.fn(),
}))

vi.mock('src/boot/axios', () => ({
  api: {
    get: mockGet,
    post: mockPost,
    patch: mockPatch,
  },
}))

const sampleEntries = [
  { id: '1', media_id: 'm1', title: 'Naruto', status: 'watching', progress: 50, score: 8 },
  { id: '2', media_id: 'm2', title: 'One Piece', status: 'completed', progress: 100, score: 9 },
  { id: '3', media_id: 'm3', title: 'Bleach', status: 'paused', progress: 30, score: 7 },
]

describe('useTrackingStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetchMyList calls API and populates entries', async () => {
    mockGet.mockResolvedValue({ data: { items: sampleEntries } })
    const store = useTrackingStore()
    expect(store.entries).toHaveLength(0)

    await store.fetchMyList()
    expect(mockGet).toHaveBeenCalledWith('/api/v1/lists/me', expect.any(Object))
    expect(store.entries).toHaveLength(3)
    expect(store.isLoading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('fetchMyList handles error', async () => {
    mockGet.mockRejectedValue(new Error('API error'))
    const store = useTrackingStore()

    await store.fetchMyList()
    expect(store.error).toBe('Failed to load your list.')
    expect(store.entries).toHaveLength(0)
    expect(store.isLoading).toBe(false)
  })

  it('fetchMyList with status filter', async () => {
    mockGet.mockResolvedValue({ data: { items: [] } })
    const store = useTrackingStore()

    await store.fetchMyList('watching')
    expect(mockGet).toHaveBeenCalledWith('/api/v1/lists/me', expect.objectContaining({
      params: { status: 'watching' },
    }))
  })

  it('addToList calls POST then refetches', async () => {
    mockPost.mockResolvedValue({ data: {} })
    mockGet.mockResolvedValue({ data: { items: sampleEntries } })
    const store = useTrackingStore()

    await store.addToList({ media_id: 'm4', status: 'plan_to_watch' })
    expect(mockPost).toHaveBeenCalledWith('/api/v1/lists', expect.objectContaining({
      media_id: 'm4',
    }))
    expect(mockGet).toHaveBeenCalled() // refetches
  })

  it('updateEntry calls PATCH and updates local state', async () => {
    mockGet.mockResolvedValue({ data: { items: sampleEntries } })
    await useTrackingStore().fetchMyList()

    mockPatch.mockResolvedValue({ data: {} })
    const store = useTrackingStore()
    await store.updateEntry('m1', { progress: 60, score: 9 })

    expect(mockPatch).toHaveBeenCalledWith('/api/v1/lists/m1', expect.objectContaining({
      progress: 60,
      score: 9,
    }))

    const entry = store.entries.find((e) => e.media_id === 'm1')
    expect(entry?.progress).toBe(60)
    expect(entry?.score).toBe(9)
  })

  it('createCustomList calls POST and prepends list', async () => {
    const newList = { id: 'cl1', name: 'My Favorites', description: '', is_public: false, sort_order: 0 }
    mockPost.mockResolvedValue({ data: newList })
    const store = useTrackingStore()

    const result = await store.createCustomList({ name: 'My Favorites' })
    expect(result).toEqual(newList)
    expect(store.customLists).toContainEqual(newList)
  })

  it('stats computed from entries', async () => {
    mockGet.mockResolvedValue({ data: { items: sampleEntries } })
    const store = useTrackingStore()
    await store.fetchMyList()

    expect(store.stats.total).toBe(3)
    expect(store.stats.watching).toBe(1)
    expect(store.stats.completed).toBe(1)
    expect(store.stats.paused).toBe(1)
    expect(store.stats.dropped).toBe(0)
  })

  it('byStatus groups entries by status', async () => {
    mockGet.mockResolvedValue({ data: { items: sampleEntries } })
    const store = useTrackingStore()
    await store.fetchMyList()

    expect(store.byStatus.watching).toHaveLength(1)
    expect(store.byStatus.completed).toHaveLength(1)
    expect(store.byStatus.paused).toHaveLength(1)
    expect(store.byStatus.watching[0].media_id).toBe('m1')
  })

  it('fetchHistory calls API and populates history', async () => {
    const historyItems = [
      { id: 'h1', entry_id: '1', media_id: 'm1', event_type: 'status_changed', old_status: 'plan_to_watch', new_status: 'watching', created_at: '2026-06-05T00:00:00Z' },
    ]
    mockGet.mockResolvedValue({ data: { items: historyItems } })
    const store = useTrackingStore()

    await store.fetchHistory()
    expect(mockGet).toHaveBeenCalledWith('/api/v1/lists/me/history', expect.any(Object))
    expect(store.history).toHaveLength(1)
  })

  it('fetchHistory handles error', async () => {
    mockGet.mockRejectedValue(new Error('API error'))
    const store = useTrackingStore()

    await store.fetchHistory()
    expect(store.historyError).toBe('Failed to load history.')
    expect(store.history).toHaveLength(0)
  })
})
