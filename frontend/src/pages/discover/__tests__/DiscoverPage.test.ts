import { ref } from 'vue'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import DiscoverPage from '../DiscoverPage.vue'

const itemsRef = ref<Array<Record<string, unknown>>>([])
const totalRef = ref(0)
const isLoadingRef = ref(false)
const errorRef = ref<string | null>(null)
let routeQuery = {}
const mockSearch = vi.fn()
const mockPush = vi.fn().mockResolvedValue(undefined)

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
  useRoute: () => ({ query: routeQuery }),
}))

vi.mock('src/composables/useMediaSearch', () => ({
  useMediaSearch: () => ({
    data: itemsRef,
    total: totalRef,
    isLoading: isLoadingRef,
    error: errorRef,
    search: mockSearch,
  }),
}))

const stubs = {
  'q-page': { template: '<div><slot /></div>' },
  'q-input': {
    props: ['modelValue', 'label'],
    template:
      '<input :value="modelValue" :placeholder="label" data-name="search-input" @keyup="$emit(\'keyup\', $event)" @input="$emit(\'update:modelValue\', $event.target.value)" />',
  },
  'q-icon': true,
  'q-select': true,
  'q-btn': {
    props: ['label', 'color', 'loading', 'type', 'flat'],
    template: '<button :disabled="loading" :data-name="label" @click="$emit(\'click\')">{{ label }}</button>',
  },
  'q-banner': {
    props: ['dense'],
    template: '<div class="q-banner"><slot /><slot name="action" /></div>',
  },
  'q-card': {
    template: '<div class="q-card" data-name="media-card"><slot /></div>',
  },
  'q-img': {
    template:
      '<div class="q-img"><slot name="error"><div class="no-cover">No Cover</div></slot></div>',
  },
  'q-card-section': {
    template: '<div class="q-card-section"><slot /></div>',
  },
  'q-spinner': true,
}

describe('DiscoverPage', () => {
  beforeEach(() => {
    itemsRef.value = []
    totalRef.value = 0
    isLoadingRef.value = false
    errorRef.value = null
    routeQuery = {}
    mockSearch.mockReset()
    mockPush.mockClear()
  })

  it('renders search input and type filter', () => {
    const wrapper = mount(DiscoverPage, { global: { stubs } })
    expect(wrapper.find('input[data-name="search-input"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Search')
  })

  it('shows standardized empty state when no results exist', () => {
    const wrapper = mount(DiscoverPage, { global: { stubs } })
    expect(wrapper.text()).toContain('No results to display yet.')
  })

  it('shows loading state while searching', () => {
    isLoadingRef.value = true
    const wrapper = mount(DiscoverPage, { global: { stubs } })
    expect(wrapper.text()).toContain('Searching media...')
  })

  it('shows error state with retry when search fails', async () => {
    errorRef.value = 'Failed to fetch media. Please try again.'
    const wrapper = mount(DiscoverPage, { global: { stubs } })

    // Error banner should be visible
    expect(wrapper.text()).toContain('Failed to fetch media. Please try again.')

    // Click Retry button inside the error banner (it's a q-btn with flat+white)
    const retryBtn = wrapper.findAll('button').find((b) => b.text().includes('Retry'))
    expect(retryBtn).toBeDefined()
    await retryBtn!.trigger('click')
    expect(mockSearch).toHaveBeenCalled()
  })

  it('calls search on Search button click', async () => {
    mockSearch.mockResolvedValue(undefined)
    const wrapper = mount(DiscoverPage, { global: { stubs } })
    const searchBtn = wrapper.findAll('button').find((b) => b.attributes('data-name') === 'Search')
    expect(searchBtn).toBeDefined()
    await searchBtn!.trigger('click')
    expect(mockSearch).toHaveBeenCalledWith(expect.objectContaining({ query: undefined }))
  })

  it('calls search on Enter key press in input', async () => {
    mockSearch.mockResolvedValue(undefined)
    const wrapper = mount(DiscoverPage, { global: { stubs } })
    const input = wrapper.find('input[data-name="search-input"]')
    await input.setValue('Naruto')
    await input.trigger('keyup', { key: 'Enter' })
    expect(mockSearch).toHaveBeenCalled()
  })

  it('renders search results as media cards with metadata', () => {
    itemsRef.value = [
      {
        id: '1',
        title_romaji: 'Naruto',
        title_english: 'Naruto',
        cover_image_medium: 'http://example.com/cover.jpg',
        media_type: 'anime',
        format: 'TV',
        average_score: 8.5,
      },
    ]
    totalRef.value = 1
    const wrapper = mount(DiscoverPage, { global: { stubs } })
    expect(wrapper.text()).toContain('Naruto')
    expect(wrapper.text()).toContain('anime')
    expect(wrapper.text()).toContain('TV')
    expect(wrapper.text()).toContain('8.5')
    expect(wrapper.text()).toContain('1 result(s)')
  })

  it('navigates to media detail on card click', async () => {
    itemsRef.value = [{ id: '42', title_romaji: 'One Piece', cover_image_medium: null }]
    totalRef.value = 1
    const wrapper = mount(DiscoverPage, { global: { stubs } })
    const card = wrapper.find('.q-card')
    expect(card.exists()).toBe(true)
    await card.trigger('click')
    expect(mockPush).toHaveBeenCalledWith({ name: 'media-detail', params: { id: '42' } })
  })

  it('shows No Cover fallback when cover image is missing', () => {
    itemsRef.value = [
      {
        id: '2',
        title_romaji: 'Bleach',
        cover_image_medium: null,
        media_type: 'anime',
        format: 'TV',
        average_score: 7.8,
      },
    ]
    totalRef.value = 1
    const wrapper = mount(DiscoverPage, { global: { stubs } })
    expect(wrapper.text()).toContain('No Cover')
  })

  it('hides result count while loading or when error exists', () => {
    itemsRef.value = [{ id: '3', title_romaji: 'Test', cover_image_medium: null }]
    totalRef.value = 5
    const wrapper = mount(DiscoverPage, { global: { stubs } })
    expect(wrapper.text()).toContain('5 result(s)')

    // Result count hidden while loading
    isLoadingRef.value = true
    const wrapperLoading = mount(DiscoverPage, { global: { stubs } })
    expect(wrapperLoading.text()).not.toContain('result(s)')

    // Result count hidden on error
    isLoadingRef.value = false
    errorRef.value = 'Error!'
    const wrapperError = mount(DiscoverPage, { global: { stubs } })
    expect(wrapperError.text()).not.toContain('result(s)')
  })

  it('auto-searches by genre when genre query param is present on mount', async () => {
    routeQuery = { genre: 'action' }

    mount(DiscoverPage, { global: { stubs } })
    await flushPromises()

    expect(mockSearch).toHaveBeenCalledWith(
      expect.objectContaining({ genres: ['action'], page: 1 }),
    )
  })
})
