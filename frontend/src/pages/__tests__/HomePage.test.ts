import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'

import { useHomeStore } from 'src/stores/home'

// Mock all child components
vi.mock('src/components/anime/AnimeCard.vue', () => ({
  default: { template: '<div class="mock-anime-card" @click="$emit(\'click\', $attrs.id)"><slot /></div>', inheritAttrs: false },
}))
vi.mock('src/components/anime/AnimeGrid.vue', () => ({
  default: { template: '<div class="mock-anime-grid"><slot /></div>' },
}))
vi.mock('src/components/anime/TrendingCarousel.vue', () => ({
  default: { template: '<div class="mock-carousel" @item-click="$emit(\'item-click\', $event)"><slot /></div>' },
}))
vi.mock('src/components/anime/ScoreRing.vue', () => ({
  default: { template: '<span class="mock-score">{{ score }}</span>', props: ['score', 'size'] },
}))
vi.mock('src/components/home/FriendActivityRow.vue', () => ({
  default: { template: '<div class="mock-activity"><slot /></div>' },
}))
vi.mock('src/components/home/GenrePills.vue', () => ({
  default: { template: '<div class="mock-genres"><slot /></div>' },
}))
vi.mock('src/components/home/SectionHeader.vue', () => ({
  default: { template: '<div class="mock-section-header">{{ title }}<slot name="actions" /></div>', props: ['title'] },
}))

// Mock router
const mockRouter = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
    { path: '/media/:id', name: 'media-detail', component: { template: '<div>Detail</div>' } },
    { path: '/discover', name: 'discover', component: { template: '<div>Discover</div>' } },
    { path: '/list', name: 'my-list', component: { template: '<div>My List</div>' } },
  ],
})

async function createWrapper() {
  setActivePinia(createPinia())
  const store = useHomeStore()

  // Provide default empty state
  store.spotlight = { title: 'Spotlight', items: [], isLoading: false, error: null }
  store.continueWatching = { title: 'Continue Watching', items: [], isLoading: false, error: null }
  store.trending = { title: 'Trending Now', items: [], isLoading: false, error: null }
  store.recentUpdates = { title: 'Recently Updated', items: [], isLoading: false, error: null }
  store.newReleases = { title: 'New Releases', items: [], isLoading: false, error: null }
  store.friendActivity = { title: 'Friends Watching', items: [], isLoading: false, error: null }
  store.genres = { title: 'Popular Genres', items: [], isLoading: false, error: null }

  const HomePage = (await import('../HomePage.vue')).default
  return mount(HomePage, {
    global: {
      plugins: [createPinia(), mockRouter],
      stubs: {
        'q-page': { template: '<div class="q-page"><slot /></div>' },
      },
    },
  })
}

describe('HomePage', () => {
  beforeEach(async () => {
    vi.restoreAllMocks()
    await mockRouter.push('/')
  })

  it('renders without crashing', async () => {
    const wrapper = await createWrapper()
    expect(wrapper.exists()).toBe(true)
  })

  it('renders Trending Now section', async () => {
    const wrapper = await createWrapper()
    expect(wrapper.text()).toContain('Trending Now')
  })

  it('renders New Releases section', async () => {
    const wrapper = await createWrapper()
    expect(wrapper.text()).toContain('New Releases')
  })

  it('renders Popular Genres section', async () => {
    const wrapper = await createWrapper()
    expect(wrapper.text()).toContain('Popular Genres')
  })

  it('does not render hero when spotlight is empty', async () => {
    const wrapper = await createWrapper()
    expect(wrapper.find('.hero-section').exists()).toBe(false)
  })

  it('does not render continue watching when empty', async () => {
    const wrapper = await createWrapper()
    expect(wrapper.text()).not.toContain('Continue Watching')
  })

  it('does not render recently updated when empty', async () => {
    const wrapper = await createWrapper()
    expect(wrapper.text()).not.toContain('Recently Updated')
  })

  it('renders Friends Watching section always (no v-if)', async () => {
    const wrapper = await createWrapper()
    // The Friends Watching section is always rendered with its header;
    // the component handles empty/error states internally.
    expect(wrapper.text()).toContain('Friends Watching')
    expect(wrapper.find('.mock-activity').exists()).toBe(true)
  })

  it('renders Continue Watching section when items exist', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    const store = useHomeStore()
    store.continueWatching = {
      title: 'Continue Watching',
      items: [
        {
          id: 'cw-1',
          title: 'Attack on Titan',
          coverImage: 'https://example.com/cover.jpg',
          mediaType: 'anime',
          format: 'TV',
          score: 9.0,
          year: 2013,
          episodeCount: 25,
          status: 'releasing',
          progress: 12,
          totalEpisodes: 25,
        },
      ],
      isLoading: false,
      error: null,
    }

    const HomePage = (await import('../HomePage.vue')).default
    const wrapper = mount(HomePage, {
      global: {
        plugins: [pinia, mockRouter],
        stubs: {
          'q-page': { template: '<div class="q-page"><slot /></div>' },
        },
      },
    })

    expect(wrapper.text()).toContain('Continue Watching')
    expect(wrapper.text()).toContain('See All')
    // AnimeCard is mocked — verify the mock card rendered
    expect(wrapper.find('.mock-anime-card').exists()).toBe(true)
  })

  it('renders See All button in Continue Watching section when items exist', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    const store = useHomeStore()
    store.continueWatching = {
      title: 'Continue Watching',
      items: [
        {
          id: 'cw-1',
          title: 'One Piece',
          coverImage: null,
          mediaType: 'anime',
          format: 'TV',
          score: null,
          year: null,
          episodeCount: null,
          status: 'releasing',
          progress: 5,
          totalEpisodes: null,
        },
      ],
      isLoading: false,
      error: null,
    }

    const HomePage = (await import('../HomePage.vue')).default
    const wrapper = mount(HomePage, {
      global: {
        plugins: [pinia, mockRouter],
        stubs: {
          'q-page': { template: '<div class="q-page"><slot /></div>' },
        },
      },
    })

    const seeAllBtn = wrapper.find('.see-all-btn')
    expect(seeAllBtn.exists()).toBe(true)
    expect(seeAllBtn.text()).toBe('See All')

    // Click See All should navigate to /list
    await seeAllBtn.trigger('click')
    // Wait for async navigation
    await new Promise((r) => setTimeout(r, 0))
    expect(mockRouter.currentRoute.value.path).toBe('/list')
  })
})
