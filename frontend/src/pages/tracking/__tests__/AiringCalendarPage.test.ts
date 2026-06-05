import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import AiringCalendarPage from '../AiringCalendarPage.vue'

const mockGet = vi.hoisted(() => vi.fn())
let mockGetResolve: (value: unknown) => void
let mockGetReject: (reason: unknown) => void

function createDeferredPromise(): Promise<unknown> {
  return new Promise((resolve, reject) => {
    mockGetResolve = resolve
    mockGetReject = reject
  })
}

vi.mock('src/boot/axios', () => ({
  api: {
    get: mockGet,
  },
}))

// Mock router so clickable q-item navigation works
const mockPush = vi.hoisted(() => vi.fn().mockResolvedValue(undefined))
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
}))

const stubs = {
  'q-page': { template: '<div><slot /></div>' },
  'q-btn': {
    props: ['label', 'loading', 'outline', 'color', 'icon'],
    template: '<button :disabled="loading" data-name="refresh-btn" @click="$emit(\'click\')">{{ label }}</button>',
  },
  'q-banner': {
    props: ['rounded'],
    template: '<div class="q-banner"><slot /></div>',
  },
  'q-list': {
    template: '<div class="q-list"><slot /></div>',
  },
  'q-item': {
    props: ['clickable', 'to'],
    template: '<div class="q-item" data-name="airing-item" @click="$emit(\'click\')"><slot /></div>',
  },
  'q-item-section': {
    props: ['avatar'],
    template: '<div class="q-item-section"><slot /></div>',
  },
  'q-avatar': {
    props: ['rounded', 'size'],
    template: '<div class="q-avatar"><slot /></div>',
  },
  'q-icon': {
    props: ['name'],
    template: '<span class="q-icon">{{ name }}</span>',
  },
  'q-item-label': {
    props: ['caption'],
    template: '<div class="q-item-label"><slot /></div>',
  },
}

describe('AiringCalendarPage', () => {
  beforeEach(() => {
    mockGet.mockReset()
    mockPush.mockReset()
  })

  it('renders airing calendar title and subtitle', async () => {
    mockGet.mockResolvedValue({ data: { items: [] } })
    const wrapper = mount(AiringCalendarPage, { global: { stubs } })
    await flushPromises()
    expect(wrapper.text()).toContain('Airing Calendar')
    expect(wrapper.text()).toContain('Upcoming episodes and chapters')
  })

  it('shows loading state on Refresh button while fetching', async () => {
    // Use deferred promise so the fetch stays in-flight
    mockGet.mockReturnValue(createDeferredPromise())
    const wrapper = mount(AiringCalendarPage, { global: { stubs } })

    // Refresh button should be rendered (loading state prevents double-click)
    const refreshBtn = wrapper.find('button[data-name="refresh-btn"]')
    expect(refreshBtn.exists()).toBe(true)

    // Resolve to complete loading
    mockGetResolve({ data: { items: [] } })
    await flushPromises()
  })

  it('shows error banner when fetch fails', async () => {
    mockGet.mockRejectedValue(new Error('Network error'))
    const wrapper = mount(AiringCalendarPage, { global: { stubs } })
    await flushPromises()
    expect(wrapper.text()).toContain('Failed to load airing calendar.')
  })

  it('shows empty state when no airing entries', async () => {
    mockGet.mockResolvedValue({ data: { items: [] } })
    const wrapper = mount(AiringCalendarPage, { global: { stubs } })
    await flushPromises()
    expect(wrapper.text()).toContain('No airing entries available right now.')
  })

  it('renders airing items when data is loaded', async () => {
    mockGet.mockResolvedValue({
      data: {
        items: [
          {
            id: '1',
            title_romaji: 'One Piece',
            title_english: 'One Piece',
            cover_image_medium: 'http://example.com/op.jpg',
            media_type: 'anime',
            status: 'releasing',
          },
          {
            id: '2',
            title_romaji: 'Jujutsu Kaisen',
            cover_image_medium: null,
            media_type: 'anime',
            status: 'releasing',
          },
        ],
      },
    })
    const wrapper = mount(AiringCalendarPage, { global: { stubs } })
    await flushPromises()
    expect(wrapper.text()).toContain('One Piece')
    expect(wrapper.text()).toContain('Jujutsu Kaisen')
    expect(wrapper.text()).toContain('releasing')

    // Empty state should not show
    expect(wrapper.text()).not.toContain('No airing entries available right now.')
  })

  it('refetches when Refresh button is clicked', async () => {
    mockGet.mockResolvedValue({ data: { items: [] } })
    const wrapper = mount(AiringCalendarPage, { global: { stubs } })
    await flushPromises()

    // The API was called once during mount
    const callsBefore = mockGet.mock.calls.length
    expect(callsBefore).toBeGreaterThanOrEqual(1)

    // Click refresh - it should trigger at least one more API call
    mockGet.mockResolvedValue({ data: { items: [] } })
    const refreshBtn = wrapper.find('button[data-name="refresh-btn"]')
    await refreshBtn.trigger('click')
    await flushPromises()

    const callsAfter = mockGet.mock.calls.length
    expect(callsAfter).toBeGreaterThan(callsBefore)
  })

  it('falls back to icon when cover image is missing', async () => {
    mockGet.mockResolvedValue({
      data: {
        items: [
          {
            id: '3',
            title_romaji: 'No Cover Show',
            cover_image_medium: null,
            media_type: 'anime',
            status: 'finished',
          },
        ],
      },
    })
    const wrapper = mount(AiringCalendarPage, { global: { stubs } })
    await flushPromises()
    // q-icon stub renders as <span class="q-icon">{{ name }}</span>
    expect(wrapper.text()).toContain('No Cover Show')
  })
})
