import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import MyListPage from '../MyListPage.vue'

const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush.mockResolvedValue(undefined) }),
  useRoute: () => ({ params: { status: 'watching' } }),
}))

// Hoisted mock data and functions
const { mockGet } = vi.hoisted(() => {
  const mockGet = vi.fn()

  const mockHistoryItems = [
    {
      id: 'hist-1',
      entry_id: 'entry-1',
      media_id: 'media-1',
      event_type: 'added',
      old_status: null,
      new_status: 'watching',
      old_progress: null,
      new_progress: 1,
      old_score: null,
      new_score: null,
      note: null,
      created_at: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
    },
    {
      id: 'hist-2',
      entry_id: 'entry-1',
      media_id: 'media-1',
      event_type: 'progress_updated',
      old_status: null,
      new_status: null,
      old_progress: 1,
      new_progress: 5,
      old_score: null,
      new_score: null,
      note: null,
      created_at: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
    },
    {
      id: 'hist-3',
      entry_id: 'entry-2',
      media_id: 'media-3',
      event_type: 'status_changed',
      old_status: 'plan_to_watch',
      new_status: 'watching',
      old_progress: null,
      new_progress: null,
      old_score: null,
      new_score: null,
      note: null,
      created_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
    },
  ]

  return { mockGet, mockHistoryItems }
})

vi.mock('src/boot/axios', () => ({
  api: {
    get: mockGet,
    patch: vi.fn(),
  },
}))

function flushPromises(): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, 10))
}

const stubs = {
  'q-page': { template: '<div><slot /></div>' },
  'q-banner': { template: '<div class="q-banner"><slot /><slot name="action" /></div>' },
  'q-tabs': { template: '<div class="q-tabs"><slot /></div>' },
  'q-tab': true,
  'q-route-tab': true,
  'q-separator': true,
  'q-spinner': true,
  'q-list': { template: '<div class="q-list"><slot /></div>' },
  'q-item': { template: '<div class="q-item"><slot /></div>' },
  'q-item-section': { template: '<div class="q-item-section"><slot /></div>' },
  'q-avatar': { template: '<div><slot /></div>' },
  'q-icon': true,
  'q-item-label': { props: ['caption'], template: '<span class="q-item-label"><slot /></span>' },
  'q-card': { template: '<div class="q-card"><slot /></div>' },
  'q-card-section': { template: '<div class="q-card-section"><slot /></div>' },
  'q-input': true,
  'q-btn': { props: ['label', 'loading', 'disable', 'flat', 'dense', 'color'], template: '<button :disabled="disable" @click="$emit(\'click\')">{{ label }}</button>' },
  'q-dialog': { template: '<div><slot /></div>' },
  'q-card-actions': { template: '<div><slot /></div>' },
  'q-chip': { props: ['color', 'size', 'dense', 'outline', 'textColor'], template: '<span class="q-chip"><slot /></span>' },
  ProgressWidget: true,
  ScoreWidget: true,
}

describe('MyListPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('renders my list heading', async () => {
    mockGet.mockImplementation((url: string) => {
      if (url.includes('/history')) {
        return Promise.resolve({ data: { items: [], total: 0, limit: 20 } })
      }
      return Promise.resolve({ data: { items: [], total: 0 } })
    })
    const wrapper = mount(MyListPage, { global: { stubs } })
    await flushPromises()

    expect(wrapper.text()).toContain('My List')
  })

  it('shows stats card when entries exist', async () => {
    const mockEntries = [
      { id: 'e1', media_id: 'm1', status: 'watching', progress: 5, score: null, title: 'A', cover_image_medium: null, notes: null },
      { id: 'e2', media_id: 'm2', status: 'completed', progress: 24, score: 8, title: 'B', cover_image_medium: null, notes: null },
    ]
    mockGet.mockImplementation((url: string) => {
      if (url.includes('/history')) {
        return Promise.resolve({ data: { items: [], total: 0, limit: 20 } })
      }
      return Promise.resolve({ data: { items: mockEntries, total: 2 } })
    })
    const wrapper = mount(MyListPage, { global: { stubs } })
    await flushPromises()

    const chips = wrapper.findAll('.q-chip')
    expect(chips.length).toBeGreaterThan(0)
    expect(wrapper.text()).toContain('Total: 2')
    expect(wrapper.text()).toContain('Watching: 1')
    expect(wrapper.text()).toContain('Completed: 1')
  })

  it('hides stats card when no entries exist', async () => {
    mockGet.mockImplementation((url: string) => {
      if (url.includes('/history')) {
        return Promise.resolve({ data: { items: [], total: 0, limit: 20 } })
      }
      return Promise.resolve({ data: { items: [], total: 0 } })
    })
    const wrapper = mount(MyListPage, { global: { stubs } })
    await flushPromises()

    expect(wrapper.text()).not.toContain('Total:')
  })

  it('shows history loading state', async () => {
    // Don't resolve the mock immediately to keep loading true
    mockGet.mockReturnValue(new Promise(() => undefined)) // never resolves
    const wrapper = mount(MyListPage, { global: { stubs } })
    await flushPromises()

    expect(wrapper.text()).toContain('Recent Activity')
    // Loading spinner should be present — q-spinner renders
    expect(wrapper.findComponent({ name: 'q-spinner' }).exists()).toBe(true)
  })

  it('shows history error state with retry', async () => {
    mockGet.mockRejectedValue(new Error('Network error'))
    const wrapper = mount(MyListPage, { global: { stubs } })
    await flushPromises()

    expect(wrapper.text()).toContain('Failed to load history.')
    expect(wrapper.text()).toContain('Retry')
  })

  it('shows history empty state when no history', async () => {
    mockGet.mockResolvedValue({ data: { items: [], total: 0, limit: 20 } })
    const wrapper = mount(MyListPage, { global: { stubs } })
    await flushPromises()

    expect(wrapper.text()).toContain('No recent activity.')
  })

  it('renders history items with event descriptions', async () => {
    mockGet.mockImplementation((url: string) => {
      if (url.includes('/history')) {
        return Promise.resolve({ data: { items: [], total: 0, limit: 20 } })
      }
      return Promise.resolve({ data: { items: [], total: 0 } })
    })
    const wrapper = mount(MyListPage, { global: { stubs } })
    await flushPromises()

    // Simulate store having history — directly modify pinia store
    const { useTrackingStore } = await import('src/stores/tracking')
    const store = useTrackingStore()
    store.history = [
      {
        id: 'hist-1',
        entry_id: 'entry-1',
        media_id: 'media-1',
        event_type: 'added',
        old_status: null,
        new_status: 'watching',
        old_progress: null,
        new_progress: 1,
        old_score: null,
        new_score: null,
        note: null,
        created_at: new Date(Date.now() - 3600000).toISOString(),
      },
      {
        id: 'hist-2',
        entry_id: 'entry-2',
        media_id: 'media-2',
        event_type: 'status_changed',
        old_status: 'plan_to_watch',
        new_status: 'watching',
        old_progress: null,
        new_progress: null,
        old_score: null,
        new_score: null,
        note: null,
        created_at: new Date(Date.now() - 86400000).toISOString(),
      },
    ]
    store.historyIsLoading = false
    store.historyError = null

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Added to list')
    expect(wrapper.text()).toContain('Status changed: plan to watch → watching')
  })

  it('shows "just now" for very recent history', async () => {
    mockGet.mockImplementation((url: string) => {
      if (url.includes('/history')) {
        return Promise.resolve({ data: { items: [], total: 0, limit: 20 } })
      }
      return Promise.resolve({ data: { items: [], total: 0 } })
    })
    const wrapper = mount(MyListPage, { global: { stubs } })
    await flushPromises()

    const { useTrackingStore } = await import('src/stores/tracking')
    const store = useTrackingStore()
    store.history = [
      {
        id: 'hist-1',
        entry_id: 'entry-1',
        media_id: 'media-1',
        event_type: 'added',
        old_status: null,
        new_status: 'watching',
        old_progress: null,
        new_progress: 1,
        old_score: null,
        new_score: null,
        note: null,
        created_at: new Date().toISOString(),
      },
    ]
    store.historyIsLoading = false
    store.historyError = null

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Just now')
  })
})
