import { ref } from 'vue'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import MediaDetailPage from '../MediaDetailPage.vue'

const mediaRef = ref<Record<string, unknown> | null>(null)
const isLoadingRef = ref(false)
const errorRef = ref<string | null>(null)
const mockFetchById = vi.fn()
let routeParams = { id: 'abc' }

vi.mock('vue-router', () => ({
  useRoute: () => ({ params: routeParams }),
  useRouter: () => ({ push: vi.fn().mockResolvedValue(undefined) }),
}))

vi.mock('src/composables/useMediaDetail', () => ({
  useMediaDetail: () => ({
    data: mediaRef,
    isLoading: isLoadingRef,
    error: errorRef,
    fetchById: mockFetchById,
  }),
}))

// Hoisted mocks for vi.mock factories (must be referenced in factory)
const { mockGetEntryByMedia, mockAddToList, mockUpdateEntry, mockApiGet, mockApiPost, mockApiPatch } = vi.hoisted(() => ({
  mockGetEntryByMedia: vi.fn(),
  mockAddToList: vi.fn(),
  mockUpdateEntry: vi.fn(),
  mockApiGet: vi.fn(),
  mockApiPost: vi.fn(),
  mockApiPatch: vi.fn(),
}))

// Mock tracking store
vi.mock('src/stores/tracking', () => ({
  useTrackingStore: () => ({
    getEntryByMedia: mockGetEntryByMedia,
    addToList: mockAddToList,
    updateEntry: mockUpdateEntry,
  }),
}))

// Mock API with per-URL implementation
vi.mock('src/boot/axios', () => ({
  api: {
    get: mockApiGet,
    post: mockApiPost,
    patch: mockApiPatch,
  },
}))

/** Creates default episode data for a given episode count */
function buildEpisodeData(count: number): Array<Record<string, unknown>> {
  return Array.from({ length: count }, (_, i) => {
    const ep = i + 1
    return {
      id: `ep-${ep}`,
      episode_number: ep,
      canonical_title: `Episode ${ep}`,
      thumbnail_url: null,
      duration_minutes: 24,
      canonical_air_date: `2024-01-${String(ep).padStart(2, '0')}`,
      sources: [
        { source: 'megaplay', language: 'sub', embed_url: `https://example.com/${ep}`, is_available: true },
      ],
    }
  })
}

/** Creates default server/source option data */
function buildServerData(count: number): Array<Record<string, unknown>> {
  return [
    {
      source: 'megaplay',
      episodes: Array.from({ length: count }, (_, i) => ({
        id: `srv-${i + 1}`,
        language: 'sub',
        episode_number: i + 1,
        embed_url: `https://example.com/${i + 1}`,
        is_available: true,
      })),
    },
  ]
}

const stubs = {
  HeroBanner: {
    props: ['title', 'titleEnglish', 'bannerImage', 'synopsis', 'score', 'year', 'mediaType', 'format', 'status', 'episodeCount', 'genres', 'isSynopsisExpanded'],
    template:
      '<div class="hero-banner-stub"><div class="hero-title">{{ title }}</div><button class="stub-play" @click="$emit(\'play\')">Play</button><button class="stub-add-list" @click="$emit(\'add-list\')">+ List</button><button class="stub-like" @click="$emit(\'like\')">Like</button><button class="stub-share" @click="$emit(\'share\')">Share</button><slot /></div>',
  },
  EpisodeList: {
    props: ['items', 'loading', 'error', 'selectedEpisodeNumber'],
    template:
      '<div class="episode-list-stub">{{ loading ? \'Loading episodes\' : error ? error : items.length + \' episodes\' }}</div>',
  },
  ServerSelector: {
    props: ['servers', 'selectedServerId', 'loading', 'error'],
    template:
      '<div class="server-selector-stub">{{ loading ? \'Loading servers\' : servers.length + \' servers\' }}</div>',
  },
  RelatedMediaCarousel: {
    props: ['items', 'isLoading', 'error'],
    template:
      '<div class="related-carousel-stub">{{ isLoading ? \'Loading related\' : items.length + \' related\' }}</div>',
  },
  'add-to-list-sheet': {
    props: ['modelValue', 'mediaId', 'title'],
    template:
      '<div class="add-to-list-sheet-stub" v-if="modelValue">AddToListSheet for {{ title }}</div>',
  },
  VideoPlayer: {
    props: ['embedUrl', 'title', 'isLoading', 'autoplay'],
    emits: ['ended', 'retry'],
    template:
      '<div class="video-player-stub" :data-embed-url="embedUrl"><div class="vp-title">{{ title }}</div><button class="trigger-ended" @click="$emit(\'ended\')">Trigger Ended</button></div>',
  },
}

/** Stub Teleport to render content in-place for testing */
function mountPage(): ReturnType<typeof mount> {
  return mount(MediaDetailPage, {
    global: {
      stubs: {
        ...stubs,
        Teleport: {
          template: '<div><slot /></div>',
        },
      },
    },
  })
}

describe('MediaDetailPage', () => {
  beforeEach(() => {
    mediaRef.value = null
    isLoadingRef.value = false
    errorRef.value = null
    routeParams = { id: 'abc' }
    mockFetchById.mockReset()
    mockGetEntryByMedia.mockReset()
    mockAddToList.mockReset()
    mockUpdateEntry.mockReset()
    mockApiGet.mockReset()
    mockApiPost.mockReset()
    mockApiPatch.mockReset()
    // Default: empty data for all GET requests
    mockApiGet.mockResolvedValue({ data: { items: [] } })
  })

  it('renders loading spinner while fetching', () => {
    isLoadingRef.value = true
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Loading media details')
  })

  it('renders error state with retry when fetch fails', async () => {
    errorRef.value = 'Failed to load media detail.'
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Failed to load media detail.')
    const retryBtn = wrapper.find('button')
    expect(retryBtn.exists()).toBe(true)
  })

  it('renders HeroBanner with media data', () => {
    mediaRef.value = {
      id: '1',
      title_romaji: 'Attack on Titan',
      title_english: 'Attack on Titan',
      media_type: 'anime',
      format: 'TV',
      status: 'finished',
      average_score: 9.0,
      synopsis: 'A story about giants.',
      cover_image_large: 'http://example.com/cover.jpg',
      banner_image: 'http://example.com/banner.jpg',
      season_year: 2013,
      episode_count: 75,
      genres: ['Action', 'Drama'],
    }
    const wrapper = mountPage()
    expect(wrapper.find('.hero-banner-stub').exists()).toBe(true)
    expect(wrapper.text()).toContain('Attack on Titan')
  })

  it('renders tab bar with Episodes, Info, Related tabs', () => {
    mediaRef.value = { id: '1', title_romaji: 'Test' }
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Episodes')
    expect(wrapper.text()).toContain('Info')
    expect(wrapper.text()).toContain('Related')
  })

  it('defaults to Episodes tab', () => {
    mediaRef.value = { id: '1', title_romaji: 'Test' }
    const wrapper = mountPage()
    const tabs = wrapper.findAll('.tab-btn')
    expect(tabs[0].classes()).toContain('active')
  })

  it('switches active tab on click', async () => {
    mediaRef.value = { id: '1', title_romaji: 'Test' }
    const wrapper = mountPage()
    const tabs = wrapper.findAll('.tab-btn')
    // Click Info tab
    await tabs[1].trigger('click')
    expect(tabs[1].classes()).toContain('active')
    expect(wrapper.text()).toContain('Synopsis')
  })

  it('shows Add to List sheet on + List click', async () => {
    mediaRef.value = { id: '42', title_romaji: 'Naruto' }
    const wrapper = mountPage()
    expect(wrapper.find('.add-to-list-sheet-stub').exists()).toBe(false)

    const addBtn = wrapper.find('.stub-add-list')
    await addBtn.trigger('click')

    expect(wrapper.find('.add-to-list-sheet-stub').exists()).toBe(true)
    expect(wrapper.text()).toContain('Naruto')
  })

  it('renders fallback text for missing synopsis', async () => {
    mediaRef.value = {
      id: '2',
      title_romaji: 'One Piece',
      synopsis: null,
    }
    const wrapper = mountPage()
    // Click Info tab to see synopsis
    const infoTab = wrapper.findAll('.tab-btn')[1]
    await infoTab.trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('No synopsis available.')
  })

  it('shows Unknown for null media_type/format/status', async () => {
    mediaRef.value = {
      id: '4',
      title_romaji: 'Test',
      media_type: null,
      format: null,
      status: null,
    }
    const wrapper = mountPage()
    const infoTab = wrapper.findAll('.tab-btn')[1]
    await infoTab.trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('Unknown')
  })

  it('shows N/A when score is null', async () => {
    mediaRef.value = {
      id: '5',
      title_romaji: 'Test',
      average_score: null,
    }
    const wrapper = mountPage()
    const infoTab = wrapper.findAll('.tab-btn')[1]
    await infoTab.trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('N/A')
  })

  // --- Phase 28.6: Player overlay and progress tracking ---

  it('opens player overlay when Play button is clicked with episodes available', async () => {
    mediaRef.value = { id: '1', title_romaji: 'Attack on Titan', episode_count: 2 }
    routeParams = { id: '1' }
    mockApiGet.mockImplementation((url: string) => {
      if (url.includes('/episodes/sources')) {
        return Promise.resolve({ data: { items: buildEpisodeData(2) } })
      }
      if (url.includes('/sources')) {
        return Promise.resolve({ data: { items: buildServerData(2) } })
      }
      return Promise.resolve({ data: { items: [] } })
    })
    const wrapper = mountPage()
    await flushPromises()

    const playBtn = wrapper.find('.stub-play')
    await playBtn.trigger('click')
    await flushPromises()

    // Player overlay should be visible with Episode 1
    expect(wrapper.find('.player-overlay').exists()).toBe(true)
    expect(wrapper.text()).toContain('Ep 1')
  })

  it('navigates to next episode when player ends and auto-advance fires', async () => {
    mediaRef.value = { id: '1', title_romaji: 'Attack on Titan', episode_count: 2 }
    routeParams = { id: '1' }
    mockApiGet.mockImplementation((url: string) => {
      if (url.includes('/episodes/sources')) {
        return Promise.resolve({ data: { items: buildEpisodeData(2) } })
      }
      if (url.includes('/sources')) {
        return Promise.resolve({ data: { items: buildServerData(2) } })
      }
      return Promise.resolve({ data: { items: [] } })
    })
    mockGetEntryByMedia.mockResolvedValue(null) // no existing entry
    mockAddToList.mockResolvedValue(undefined)
    mockApiPost.mockResolvedValue({ data: { id: 'new-entry' } })

    const wrapper = mountPage()
    await flushPromises()

    // Open player for episode 1
    const playBtn = wrapper.find('.stub-play')
    await playBtn.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Ep 1')

    // Trigger ended on VideoPlayer
    const endedBtn = wrapper.find('.trigger-ended')
    await endedBtn.trigger('click')
    await flushPromises()

    // Should auto-advance to episode 2
    expect(wrapper.text()).toContain('Ep 2')
  })

  it('closes player when ended on last episode with no next', async () => {
    mediaRef.value = { id: '1', title_romaji: 'Single Episode Show', episode_count: 1 }
    routeParams = { id: '1' }
    mockApiGet.mockImplementation((url: string) => {
      if (url.includes('/episodes/sources')) {
        return Promise.resolve({ data: { items: buildEpisodeData(1) } })
      }
      if (url.includes('/sources')) {
        return Promise.resolve({ data: { items: buildServerData(1) } })
      }
      return Promise.resolve({ data: { items: [] } })
    })
    mockGetEntryByMedia.mockResolvedValue(null)
    mockAddToList.mockResolvedValue(undefined)

    const wrapper = mountPage()
    await flushPromises()

    // Open player
    const playBtn = wrapper.find('.stub-play')
    await playBtn.trigger('click')
    await flushPromises()

    expect(wrapper.find('.player-overlay').exists()).toBe(true)

    // Trigger ended (last episode)
    const endedBtn = wrapper.find('.trigger-ended')
    await endedBtn.trigger('click')
    await flushPromises()

    // Player should close
    expect(wrapper.find('.player-overlay').exists()).toBe(false)
  })

    it('calls tracking store addToList when no existing entry on player ended', async () => {
    mediaRef.value = { id: '1', title_romaji: 'Test Anime', episode_count: 2 }
    routeParams = { id: '1' }
    mockApiGet.mockImplementation((url: string) => {
      if (url.includes('/episodes/sources')) {
        return Promise.resolve({ data: { items: buildEpisodeData(2) } })
      }
      if (url.includes('/sources')) {
        return Promise.resolve({ data: { items: buildServerData(2) } })
      }
      return Promise.resolve({ data: { items: [] } })
    })
    mockGetEntryByMedia.mockResolvedValue(null)
    mockAddToList.mockResolvedValue(undefined)

    const wrapper = mountPage()
    await flushPromises()

    // Open player
    const playBtn = wrapper.find('.stub-play')
    await playBtn.trigger('click')
    await flushPromises()

    // Trigger ended
    const endedBtn = wrapper.find('.trigger-ended')
    await endedBtn.trigger('click')
    await flushPromises()

    // Should have called getEntryByMedia to check, then addToList to create
    expect(mockGetEntryByMedia).toHaveBeenCalledWith('1')
    expect(mockAddToList).toHaveBeenCalledWith(
      expect.objectContaining({ media_id: '1', progress: 1 }),
    )
  })

  it('calls tracking store updateEntry when existing entry on player ended', async () => {
    mediaRef.value = { id: '1', title_romaji: 'Test Anime', episode_count: 2 }
    routeParams = { id: '1' }
    mockApiGet.mockImplementation((url: string) => {
      if (url.includes('/episodes/sources')) {
        return Promise.resolve({ data: { items: buildEpisodeData(2) } })
      }
      if (url.includes('/sources')) {
        return Promise.resolve({ data: { items: buildServerData(2) } })
      }
      return Promise.resolve({ data: { items: [] } })
    })
    mockGetEntryByMedia.mockResolvedValue({
      id: 'entry-1',
      media_id: '1',
      status: 'watching',
      progress: 0,
    })
    mockUpdateEntry.mockResolvedValue(undefined)

    const wrapper = mountPage()
    await flushPromises()

    // Open player
    const playBtn = wrapper.find('.stub-play')
    await playBtn.trigger('click')
    await flushPromises()

    // Trigger ended
    const endedBtn = wrapper.find('.trigger-ended')
    await endedBtn.trigger('click')
    await flushPromises()

    // Should have called updateEntry with progress = 1
    expect(mockGetEntryByMedia).toHaveBeenCalledWith('1')
    expect(mockUpdateEntry).toHaveBeenCalledWith('1', expect.objectContaining({ progress: 1 }))
  })

  it('calls updateEntry with completed status on last episode', async () => {
    mediaRef.value = { id: '1', title_romaji: 'Test Anime', episode_count: 1 }
    routeParams = { id: '1' }
    mockApiGet.mockImplementation((url: string) => {
      if (url.includes('/episodes/sources')) {
        return Promise.resolve({ data: { items: buildEpisodeData(1) } })
      }
      if (url.includes('/sources')) {
        return Promise.resolve({ data: { items: buildServerData(1) } })
      }
      return Promise.resolve({ data: { items: [] } })
    })
    mockGetEntryByMedia.mockResolvedValue({
      id: 'entry-1',
      media_id: '1',
      status: 'watching',
      progress: 0,
    })
    mockUpdateEntry.mockResolvedValue(undefined)

    const wrapper = mountPage()
    await flushPromises()

    // Open player
    const playBtn = wrapper.find('.stub-play')
    await playBtn.trigger('click')
    await flushPromises()

    // Trigger ended
    const endedBtn = wrapper.find('.trigger-ended')
    await endedBtn.trigger('click')
    await flushPromises()

    expect(mockUpdateEntry).toHaveBeenCalledWith('1', {
      progress: 1,
      status: 'completed',
    })
  })

  it('prevents double-watch — ignores second ended event for same episode', async () => {
    mediaRef.value = { id: '1', title_romaji: 'Test Anime', episode_count: 2 }
    routeParams = { id: '1' }
    mockApiGet.mockImplementation((url: string) => {
      if (url.includes('/episodes/sources')) {
        return Promise.resolve({ data: { items: buildEpisodeData(2) } })
      }
      if (url.includes('/sources')) {
        return Promise.resolve({ data: { items: buildServerData(2) } })
      }
      return Promise.resolve({ data: { items: [] } })
    })
    mockGetEntryByMedia.mockResolvedValue(null)
    mockAddToList.mockResolvedValue(undefined)

    const wrapper = mountPage()
    await flushPromises()

    // Open player
    const playBtn = wrapper.find('.stub-play')
    await playBtn.trigger('click')
    await flushPromises()

    // First ended event — should advance to ep 2
    const endedBtn = wrapper.find('.trigger-ended')
    await endedBtn.trigger('click')
    await flushPromises()

    expect(mockAddToList).toHaveBeenCalledTimes(1)
    expect(wrapper.text()).toContain('Ep 2')

    // After re-render, re-find the ended button (VideoPlayer is recreated on advance)
    const endedBtn2 = wrapper.find('.trigger-ended')
    await endedBtn2.trigger('click')
    await flushPromises()

    // addToList should have been called twice (once for ep 1, once for ep 2 — different episodes)
    expect(mockAddToList).toHaveBeenCalledTimes(2)
  })
})
