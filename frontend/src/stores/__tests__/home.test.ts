import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

import { useHomeStore } from '../home'

// Mock the API
vi.mock('src/boot/axios', () => ({
  api: {
    get: vi.fn(),
  },
}))

describe('home store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('initializes with empty sections', () => {
    const store = useHomeStore()
    expect(store.spotlight.items).toEqual([])
    expect(store.spotlight.isLoading).toBe(false)
    expect(store.trending.items).toEqual([])
    expect(store.newReleases.items).toEqual([])
    expect(store.genres.items).toEqual([])
    expect(store.anyLoading).toBe(false)
    expect(store.anyError).toBeNull()
  })

  it('hasData is false when all sections empty', () => {
    const store = useHomeStore()
    expect(store.hasData).toBe(false)
  })

  it('hasData is true when spotlight has items', () => {
    const store = useHomeStore()
    store.spotlight.items = [{ id: '1', title: 'Test', coverImage: null, mediaType: 'anime', format: 'TV', score: 8, year: 2024, episodeCount: 12 }]
    expect(store.hasData).toBe(true)
  })

  it('fetchHome sets loading states', async () => {
    const { api } = await import('src/boot/axios')
    const mockGet = vi.mocked(api.get)

    // Mock all API responses
    mockGet.mockResolvedValue({ data: { items: [] } })

    const store = useHomeStore()
    const fetchPromise = store.fetchHome()
    // Should be loading
    expect(store.anyLoading).toBe(true)
    expect(store.spotlight.isLoading).toBe(true)
    expect(store.trending.isLoading).toBe(true)

    await fetchPromise
    expect(store.anyLoading).toBe(false)
  })

  it('handle API errors gracefully', async () => {
    const { api } = await import('src/boot/axios')
    const mockGet = vi.mocked(api.get)

    // Make most requests fail, but genres succeed (it's the last one)
    mockGet
      .mockRejectedValueOnce(new Error('Spotlight failed'))    // spotlight
      .mockRejectedValueOnce(new Error('CW failed'))           // continueWatching
      .mockRejectedValueOnce(new Error('Trending failed'))     // trending
      .mockRejectedValueOnce(new Error('Updates failed'))      // recentUpdates (first try)
      .mockRejectedValueOnce(new Error('Releases failed'))     // newReleases
      .mockRejectedValueOnce(new Error('Activity failed'))     // friendActivity
      .mockResolvedValue({ data: [{ id: 'g1', name: 'Action', slug: 'action' }] }) // genres

    const store = useHomeStore()
    await store.fetchHome()

    expect(store.anyError).toBeTruthy()
    expect(store.genres.items.length).toBe(1)
    expect(store.genres.items[0].name).toBe('Action')
  })

  it('fetchGenres handles both array and envelope responses', async () => {
    const { api } = await import('src/boot/axios')
    const mockGet = vi.mocked(api.get)

    // Test with envelope response
    mockGet.mockResolvedValue({ data: { items: [{ id: 'g1', name: 'Action', slug: 'action' }] } })

    const store = useHomeStore()
    await store.fetchGenres()
    expect(store.genres.items.length).toBe(1)
    expect(store.genres.items[0].name).toBe('Action')
  })

  it('fetchContinueWatching maps entries with media to ContinueWatchingItem', async () => {
    const { api } = await import('src/boot/axios')
    const mockGet = vi.mocked(api.get)

    mockGet.mockResolvedValue({
      data: {
        items: [
          {
            id: 'entry-1',
            user_id: 'user-1',
            media_id: 'media-1',
            status: 'watching',
            progress: 12,
            media: {
              id: 'media-1',
              title_romaji: 'Attack on Titan',
              title_english: 'Attack on Titan',
              cover_image_medium: 'https://example.com/cover.jpg',
              media_type: 'anime',
              format: 'TV',
              average_score: 9.0,
              season_year: 2013,
              episode_count: 25,
              status: 'finished',
            },
          },
        ],
      },
    })

    const store = useHomeStore()
    await store.fetchContinueWatching()

    expect(store.continueWatching.items.length).toBe(1)
    expect(store.continueWatching.items[0].title).toBe('Attack on Titan')
    expect(store.continueWatching.items[0].progress).toBe(12)
    expect(store.continueWatching.items[0].totalEpisodes).toBe(25)
    expect(store.continueWatching.error).toBeNull()
  })

  it('fetchContinueWatching filters out entries without media', async () => {
    const { api } = await import('src/boot/axios')
    const mockGet = vi.mocked(api.get)

    mockGet.mockResolvedValue({
      data: {
        items: [
          { id: 'entry-1', status: 'watching', progress: 5, media: null },
          { id: 'entry-2', status: 'watching', progress: 10, media: undefined },
        ],
      },
    })

    const store = useHomeStore()
    await store.fetchContinueWatching()

    expect(store.continueWatching.items.length).toBe(0)
  })

  it('fetchContinueWatching handles totalEpisodes being null gracefully', async () => {
    const { api } = await import('src/boot/axios')
    const mockGet = vi.mocked(api.get)

    mockGet.mockResolvedValue({
      data: {
        items: [
          {
            id: 'entry-1',
            progress: 3,
            media: {
              id: 'media-1',
              title_romaji: 'One Piece',
              cover_image_medium: null,
              media_type: 'anime',
              format: 'TV',
              episode_count: null,
            },
          },
        ],
      },
    })

    const store = useHomeStore()
    await store.fetchContinueWatching()

    expect(store.continueWatching.items.length).toBe(1)
    expect(store.continueWatching.items[0].totalEpisodes).toBeNull()
    expect(store.continueWatching.items[0].progress).toBe(3)
  })

  it('fetchContinueWatching handles API failure gracefully (no throw)', async () => {
    const { api } = await import('src/boot/axios')
    const mockGet = vi.mocked(api.get)

    mockGet.mockRejectedValue(new Error('Network error'))

    const store = useHomeStore()
    // Should NOT throw — Continue Watching is optional
    await expect(store.fetchContinueWatching()).resolves.toBeUndefined()

    expect(store.continueWatching.items.length).toBe(0)
    expect(store.continueWatching.error).toBeTruthy()
    expect(store.continueWatching.isLoading).toBe(false)
  })

  it('fetchFriendActivity fetches items without filter', async () => {
    const { api } = await import('src/boot/axios')
    const mockGet = vi.mocked(api.get)

    mockGet.mockResolvedValue({
      data: { items: [{ id: 'a1', user_id: 'u1', media_id: 'm1', event_type: 'status_changed', created_at: new Date().toISOString() }], total: 1, limit: 10, offset: 0 },
    })

    const store = useHomeStore()
    await store.fetchFriendActivity()

    expect(store.friendActivity.items.length).toBe(1)
    expect(store.friendActivityFilter).toBe('all')
    expect(mockGet).toHaveBeenCalledWith('/api/v1/social/feed', { params: { limit: 10 } })
  })

  it('fetchFriendActivity sends media_type param with filter', async () => {
    const { api } = await import('src/boot/axios')
    const mockGet = vi.mocked(api.get)

    mockGet.mockResolvedValue({
      data: { items: [], total: 0, limit: 10, offset: 0 },
    })

    const store = useHomeStore()
    await store.fetchFriendActivity(false, 'anime')

    expect(store.friendActivityFilter).toBe('anime')
    expect(mockGet).toHaveBeenCalledWith('/api/v1/social/feed', { params: { limit: 10, media_type: 'anime' } })
  })

  it('loadMoreFriendActivity appends items and tracks hasMore', async () => {
    const { api } = await import('src/boot/axios')
    const mockGet = vi.mocked(api.get)

    // First call returns 1 item out of 3 total
    mockGet.mockResolvedValueOnce({
      data: { items: [{ id: 'a1', user_id: 'u1', media_id: 'm1', event_type: 'status_changed', created_at: new Date().toISOString() }], total: 3, limit: 1, offset: 0 },
    })
    // Second call returns next item
    mockGet.mockResolvedValueOnce({
      data: { items: [{ id: 'a2', user_id: 'u2', media_id: 'm2', event_type: 'progress_updated', created_at: new Date().toISOString() }], total: 3, limit: 1, offset: 1 },
    })

    const store = useHomeStore()
    await store.fetchFriendActivity()
    expect(store.friendActivity.items.length).toBe(1)
    expect(store.friendActivityHasMore).toBe(true)

    await store.loadMoreFriendActivity()
    expect(store.friendActivity.items.length).toBe(2)
    expect(store.friendActivityHasMore).toBe(true) // 2 < 3
  })

  it('setFriendActivityFilter resets and re-fetches', async () => {
    const { api } = await import('src/boot/axios')
    const mockGet = vi.mocked(api.get)

    mockGet.mockResolvedValue({
      data: { items: [{ id: 'a1', user_id: 'u1', media_id: 'm1', event_type: 'status_changed', created_at: new Date().toISOString() }], total: 1, limit: 10, offset: 0 },
    })

    const store = useHomeStore()
    // Pre-populate with old data (Pinia unwraps refs, so no .value needed)
    store.friendActivity.items = [{ id: 'old', userId: 'u0', username: 'old', displayName: null, avatarUrl: null, mediaId: 'm0', mediaTitle: 'Old', mediaCoverImage: null, eventType: 'added', newStatus: null, newProgress: null, createdAt: '' }]

    await store.setFriendActivityFilter('manga')

    expect(store.friendActivityFilter).toBe('manga')
    expect(store.friendActivity.items.length).toBe(1) // reset and re-fetched
    expect(mockGet).toHaveBeenCalledWith('/api/v1/social/feed', { params: { limit: 10, media_type: 'manga' } })
  })

  it('fetchTrending maps API data to MediaItem', async () => {
    const { api } = await import('src/boot/axios')
    const mockGet = vi.mocked(api.get)

    mockGet.mockResolvedValue({
      data: {
        items: [
          {
            id: '123',
            title_romaji: 'Attack on Titan',
            title_english: 'Attack on Titan',
            cover_image_medium: 'https://example.com/cover.jpg',
            media_type: 'anime',
            format: 'TV',
            average_score: 9.0,
            season_year: 2013,
            episode_count: 25,
            status: 'finished',
          },
        ],
      },
    })

    const store = useHomeStore()
    await store.fetchTrending()

    expect(store.trending.items.length).toBe(1)
    expect(store.trending.items[0].title).toBe('Attack on Titan')
    expect(store.trending.items[0].score).toBe(9)
    expect(store.trending.items[0].mediaType).toBe('anime')
    expect(store.trending.items[0].episodeCount).toBe(25)
  })
})
