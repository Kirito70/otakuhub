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
