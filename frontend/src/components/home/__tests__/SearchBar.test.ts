import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'

// Mock the API
import { api } from 'src/boot/axios'

vi.mock('src/boot/axios', () => ({
  api: {
    get: vi.fn(),
  },
}))

const mockRouter = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
    { path: '/search', name: 'search', component: { template: '<div>Search</div>' } },
    { path: '/media/:id', name: 'media-detail', component: { template: '<div>Detail</div>' } },
  ],
})

// Sample media items for the search response
const sampleItems = [
  { id: '1', title_romaji: 'Attack on Titan', title_english: 'Attack on Titan', cover_image_medium: 'https://example.com/aot.jpg', media_type: 'anime', format: 'TV', average_score: 9.0, season_year: 2013, episode_count: 25, status: 'finished' },
  { id: '2', title_romaji: 'Jujutsu Kaisen', title_english: null, cover_image_medium: null, media_type: 'anime', format: 'TV', average_score: 8.5, season_year: 2020, episode_count: 24, status: 'releasing' },
]

describe('SearchBar', () => {
  beforeEach(async () => {
    vi.clearAllMocks()
    await mockRouter.push('/')
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  async function createWrapper() {
    const SearchBar = (await import('../SearchBar.vue')).default
    return mount(SearchBar, {
      global: { plugins: [mockRouter] },
    })
  }

  it('renders input with placeholder', async () => {
    const wrapper = await createWrapper()
    const input = wrapper.find('.search-input')
    expect(input.exists()).toBe(true)
    expect(input.attributes('placeholder')).toBe('Search anime, manga, manhwa...')
  })

  it('shows clear button when query is typed', async () => {
    const wrapper = await createWrapper()
    const input = wrapper.find('.search-input')
    await input.setValue('test')
    expect(wrapper.find('.search-clear-btn').exists()).toBe(true)
  })

  it('shows search icon when query is empty', async () => {
    const wrapper = await createWrapper()
    expect(wrapper.find('.search-icon').exists()).toBe(true)
    expect(wrapper.find('.search-clear-btn').exists()).toBe(false)
  })

  it('calls API after debounce on input', async () => {
    vi.useFakeTimers()
    const mockGet = vi.mocked(api.get)
    mockGet.mockResolvedValue({ data: { items: sampleItems } })

    const wrapper = await createWrapper()
    const input = wrapper.find('.search-input')
    await input.setValue('Attack')

    // Immediately after setting value — debounce hasn't fired yet
    expect(mockGet).not.toHaveBeenCalled()

    // Advance past 300ms debounce using async timer advancement
    await vi.advanceTimersByTimeAsync(350)

    expect(mockGet).toHaveBeenCalledTimes(1)
    expect(mockGet).toHaveBeenCalledWith('/api/v1/media/search', {
      params: { query: 'Attack', limit: 5 },
    })
  })

  it('shows loading state in dropdown during fetch', async () => {
    vi.useFakeTimers()
    const mockGet = vi.mocked(api.get)
    // Return a promise that never resolves so loading stays true
    mockGet.mockReturnValue(new Promise(() => undefined))

    const wrapper = await createWrapper()
    const input = wrapper.find('.search-input')
    await input.setValue('Attack')
    await vi.advanceTimersByTimeAsync(350)
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.dropdown-loading').exists()).toBe(true)
    expect(wrapper.find('.dropdown-loading').text()).toContain('Searching')
  })

  it('shows results in dropdown after fetch', async () => {
    vi.useFakeTimers()
    const mockGet = vi.mocked(api.get)
    mockGet.mockResolvedValue({ data: { items: sampleItems } })

    const wrapper = await createWrapper()
    const input = wrapper.find('.search-input')
    await input.setValue('Attack')
    await vi.advanceTimersByTimeAsync(350)
    await wrapper.vm.$nextTick()

    expect(wrapper.findAll('.dropdown-item').length).toBe(2)
    expect(wrapper.find('.dropdown-item-title').text()).toContain('Attack on Titan')
  })

  it('shows empty state when no results', async () => {
    vi.useFakeTimers()
    const mockGet = vi.mocked(api.get)
    mockGet.mockResolvedValue({ data: { items: [] } })

    const wrapper = await createWrapper()
    const input = wrapper.find('.search-input')
    await input.setValue('zzzznonexistent')
    await vi.advanceTimersByTimeAsync(350)
    await wrapper.vm.$nextTick()

    const dropdown = wrapper.find('.search-dropdown')
    expect(dropdown.exists()).toBe(true)
    expect(wrapper.find('.dropdown-empty').exists()).toBe(true)
    expect(wrapper.find('.dropdown-empty').text()).toBe('No results found')
  })

  it('shows error state when API fails', async () => {
    vi.useFakeTimers()
    const mockGet = vi.mocked(api.get)
    mockGet.mockRejectedValue(new Error('Network error'))

    const wrapper = await createWrapper()
    const input = wrapper.find('.search-input')
    await input.setValue('Attack')
    await vi.advanceTimersByTimeAsync(350)
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.dropdown-error').exists()).toBe(true)
    expect(wrapper.find('.dropdown-error').text()).toBe('Search failed')
  })

  it('navigates to media-detail on result click', async () => {
    const mockGet = vi.mocked(api.get)
    mockGet.mockResolvedValue({ data: { items: sampleItems } })

    const wrapper = await createWrapper()
    const input = wrapper.find('.search-input')
    await input.setValue('Attack')
    // Use real delays for navigation test
    await new Promise((r) => setTimeout(r, 400))
    await wrapper.vm.$nextTick()

    expect(wrapper.findAll('.dropdown-item').length).toBe(2)
    await wrapper.findAll('.dropdown-item')[0].trigger('click')

    // Wait for async router navigation
    await new Promise((r) => setTimeout(r, 50))
    expect(mockRouter.currentRoute.value.path).toBe('/media/1')
  })

  it('navigates to search results on Enter key', async () => {
    const wrapper = await createWrapper()
    const input = wrapper.find('.search-input')
    await input.setValue('Test Query')
    await input.trigger('keydown.enter')
    await new Promise((r) => setTimeout(r, 0))
    expect(mockRouter.currentRoute.value.path).toBe('/search')
    expect(mockRouter.currentRoute.value.query.q).toBe('Test Query')
  })

  it('clears query and results on clear button click', async () => {
    const wrapper = await createWrapper()
    const input = wrapper.find('.search-input')
    await input.setValue('test')
    expect(wrapper.find('.search-clear-btn').exists()).toBe(true)

    await wrapper.find('.search-clear-btn').trigger('click')
    const inputEl = wrapper.find('.search-input').element as HTMLInputElement
    expect(inputEl.value).toBe('')
    expect(wrapper.find('.search-clear-btn').exists()).toBe(false)
    expect(wrapper.find('.search-dropdown').exists()).toBe(false)
  })
})
