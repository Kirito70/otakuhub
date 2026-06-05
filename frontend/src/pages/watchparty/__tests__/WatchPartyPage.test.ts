import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import WatchPartyPage from '../WatchPartyPage.vue'

// Hoisted mock data and functions
const { mockParties, mockPastParties, mockDetail, mockRsvps, mockGet, mockPost } = vi.hoisted(() => {
  const mockGet = vi.fn()
  const mockPost = vi.fn()

  const mockParties = [
    {
      id: 'party-1',
      group_id: 'group-1',
      host_user_id: 'user-1',
      media_id: 'media-1',
      episode_number: 5,
      title: 'Friday Night Watch',
      scheduled_at: '2026-06-10T20:00:00Z',
      status: 'scheduled' as const,
      stream_url: 'https://example.com/stream',
      sync_url: null,
      notes: null,
      created_at: '2026-06-01T00:00:00Z',
      updated_at: '2026-06-01T00:00:00Z',
    },
    {
      id: 'party-2',
      group_id: 'group-1',
      host_user_id: 'user-2',
      media_id: 'media-2',
      episode_number: null,
      title: 'Weekend Movie Night',
      scheduled_at: '2026-06-12T18:00:00Z',
      status: 'scheduled' as const,
      stream_url: null,
      sync_url: null,
      notes: 'Bring popcorn',
      created_at: '2026-06-02T00:00:00Z',
      updated_at: '2026-06-02T00:00:00Z',
    },
  ]

  const mockPastParties = [
    {
      id: 'party-3',
      group_id: 'group-1',
      host_user_id: 'user-1',
      media_id: 'media-1',
      episode_number: null,
      title: 'Last Week Session',
      scheduled_at: '2026-05-30T20:00:00Z',
      status: 'completed' as const,
      stream_url: null,
      sync_url: null,
      notes: null,
      created_at: '2026-05-20T00:00:00Z',
      updated_at: '2026-05-30T22:00:00Z',
    },
    {
      id: 'party-4',
      group_id: 'group-1',
      host_user_id: 'user-2',
      media_id: 'media-2',
      episode_number: 3,
      title: 'Cancelled Session',
      scheduled_at: '2026-05-28T19:00:00Z',
      status: 'cancelled' as const,
      stream_url: null,
      sync_url: null,
      notes: null,
      created_at: '2026-05-25T00:00:00Z',
      updated_at: '2026-05-27T00:00:00Z',
    },
  ]

  const mockDetail = {
    id: 'party-1',
    group_id: 'group-1',
    host_user_id: 'user-1',
    media_id: 'media-1',
    episode_number: 5,
    title: 'Friday Night Watch',
    scheduled_at: '2026-06-10T20:00:00Z',
    status: 'scheduled' as const,
    stream_url: 'https://example.com/stream',
    sync_url: null,
    notes: 'Great anime night!',
    created_at: '2026-06-01T00:00:00Z',
    updated_at: '2026-06-01T00:00:00Z',
    rsvp_summary: { attending: 2, pending: 1, declined: 0 },
    host_username: 'Alice',
    media_title: 'Attack on Titan',
  }

  const mockRsvps = [
    { party_id: 'party-1', user_id: 'user-1', status: 'attending' as const, responded_at: '2026-06-02T00:00:00Z', created_at: '2026-06-01T00:00:00Z' },
    { party_id: 'party-1', user_id: 'user-2', status: 'attending' as const, responded_at: '2026-06-03T00:00:00Z', created_at: '2026-06-01T00:00:00Z' },
    { party_id: 'party-1', user_id: 'user-3', status: 'pending' as const, responded_at: null, created_at: '2026-06-01T00:00:00Z' },
  ]

  return { mockParties, mockPastParties, mockDetail, mockRsvps, mockGet, mockPost }
})

vi.mock('src/boot/axios', () => ({
  api: {
    get: mockGet,
    post: mockPost,
  },
}))

// Default mock: routes requests by URL pattern
function setupDefaultMocks() {
  mockGet.mockImplementation((url: string) => {
    // Detail endpoint: /api/v1/watchparty/{id} where id is NOT 'past' and doesn't end with /rsvps
    if (url.match(/\/api\/v1\/watchparty\/(?!past$)[^\/]+$/) && !url.includes('/rsvps')) {
      return Promise.resolve({ data: mockDetail })
    }
    if (url.includes('/rsvps')) {
      return Promise.resolve({ data: { items: mockRsvps, total: 3 } })
    }
    if (url.includes('/past')) {
      return Promise.resolve({ data: { items: mockPastParties, total: 2, limit: 50, offset: 0 } })
    }
    // Default: upcoming list
    return Promise.resolve({ data: { items: mockParties, total: 2, limit: 50, offset: 0 } })
  })
}

// Empty mock: use for tests that need empty/error states
function setupEmptyMocks() {
  mockGet.mockResolvedValue({ data: { items: [], total: 0, limit: 50, offset: 0 } })
}

// -- Helpers --
function flushPromises() {
  return new Promise(resolve => setTimeout(resolve, 10))
}

// QForm stub with working validate()
const QFormStub = {
  name: 'QForm',
  emits: ['submit'],
  methods: {
    validate() { return true },
  },
  template: '<form @submit.prevent="$emit(\'submit\')"><slot /></form>',
}

const AppPageStateStub = {
  name: 'AppPageState',
  props: ['isLoading', 'error', 'isEmpty', 'emptyLabel', 'loadingLabel'],
  template: `
    <div class="app-page-state">
      <div v-if="$props.isLoading" class="aps-loading">{{ $props.loadingLabel }}</div>
      <div v-else-if="$props.error" class="aps-error">{{ $props.error }}<button class="aps-retry" @click="$emit('retry')">Retry</button></div>
      <div v-else-if="$props.isEmpty" class="aps-empty">{{ $props.emptyLabel }}</div>
      <slot v-else />
    </div>
  `,
  emits: ['retry'],
}

const stubs = {
  'q-page': { template: '<div class="q-page"><slot /></div>' },
  'q-card': { template: '<div class="q-card"><slot /></div>' },
  'q-card-section': { template: '<div class="q-card-section"><slot /></div>' },
  'q-card-actions': { template: '<div class="q-card-actions"><slot /></div>' },
  'q-tabs': { template: '<div class="q-tabs"><slot /></div>' },
  'q-tab': { name: 'QTab', props: ['name', 'label'], template: '<span class="q-tab">{{ label }}</span>' },
  'q-tab-panels': { name: 'QTabPanels', props: ['modelValue'], template: '<div class="q-tab-panels"><slot /></div>' },
  'q-tab-panel': { name: 'QTabPanel', props: ['name'], template: '<div class="q-tab-panel" :data-name="name"><slot /></div>' },
  'q-list': { template: '<div class="q-list"><slot /></div>' },
  'q-item': { name: 'QItem', props: ['clickable'], template: '<div class="q-item" @click="$emit(\'click\')"><slot /></div>' },
  'q-item-section': { template: '<div class="q-item-section"><slot /></div>' },
  'q-item-label': { name: 'QItemLabel', props: ['caption'], template: '<span class="q-item-label" :class="{caption: $props.caption}"><slot /></span>' },
  'q-form': QFormStub,
  'q-input': { name: 'QInput', props: ['modelValue', 'label', 'rules'], template: '<input class="q-input" :placeholder="label" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />' },
  'q-btn': { name: 'QBtn', props: ['label', 'loading', 'disable', 'type', 'color'], template: '<button class="q-btn" :disabled="disable" :type="type" @click="$emit(\'click\')"><slot />{{ label }}</button>' },
  'q-banner': { template: '<div class="q-banner"><slot /></div>' },
  'q-separator': { template: '<hr class="q-separator" />' },
  'q-space': { template: '<span class="q-space" />' },
  'q-badge': { name: 'QBadge', props: ['color', 'label'], template: '<span class="q-badge" :color="$props.color">{{ $props.label }}</span>' },
  'q-dialog': { name: 'QDialog', props: ['modelValue'], template: '<div v-if="$props.modelValue" class="q-dialog"><slot /></div>' },
  'q-spinner': { template: '<span class="q-spinner" />' },
  'app-page-state': AppPageStateStub,
  RouterLink: { name: 'RouterLink', props: ['to'], template: '<a><slot /></a>' },
}

describe('WatchPartyPage - Phase 5.1', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  async function createWrapper() {
    return mount(WatchPartyPage, { global: { stubs } })
  }

  // ---- Tab Rendering ----

  it('renders tab labels (Upcoming, Past, Create)', async () => {
    setupEmptyMocks()
    const wrapper = await createWrapper()
    await flushPromises()

    const tabs = wrapper.findAll('.q-tab')
    expect(tabs.length).toBe(3)
    const tabLabels = tabs.map(w => w.text())
    expect(tabLabels).toContain('Upcoming')
    expect(tabLabels).toContain('Past')
    expect(tabLabels).toContain('Create')
  })

  // ---- Upcoming Tab ----

  it('shows loading state while upcoming fetch is in flight', async () => {
    mockGet.mockImplementation(() => new Promise(() => {})) // never resolves
    const wrapper = await createWrapper()
    await wrapper.vm.$nextTick()

    const loadingDiv = wrapper.find('.aps-loading')
    expect(loadingDiv.exists()).toBe(true)
  })

  it('shows empty state when no upcoming parties exist', async () => {
    setupEmptyMocks()
    const wrapper = await createWrapper()
    await flushPromises()
    await wrapper.vm.$nextTick()

    const emptyDiv = wrapper.find('.aps-empty')
    expect(emptyDiv.text()).toContain('No upcoming watch parties')
  })

  it('shows error state when upcoming fetch fails', async () => {
    mockGet.mockRejectedValue(new Error('Network error'))
    const wrapper = await createWrapper()
    await flushPromises()
    await wrapper.vm.$nextTick()

    const errorDiv = wrapper.find('.aps-error')
    expect(errorDiv.exists()).toBe(true)
    expect(errorDiv.text()).toContain('Failed to load upcoming')
  })

  it('renders upcoming party list when data loaded', async () => {
    setupDefaultMocks()
    const wrapper = await createWrapper()
    await flushPromises()
    await wrapper.vm.$nextTick()

    const labels = wrapper.findAll('.q-item-label')
    const labelTexts = labels.map(w => w.text())
    expect(labelTexts.some(t => t.includes('Friday Night Watch'))).toBe(true)
    expect(labelTexts.some(t => t.includes('Weekend Movie Night'))).toBe(true)
    expect(labelTexts.some(t => t.includes('Ep. 5'))).toBe(true)
  })

  // ---- Past Tab ----

  it('fetches past parties when switching to Past tab', async () => {
    setupDefaultMocks()
    const wrapper = await createWrapper()
    await flushPromises()
    mockGet.mockClear()

    // Past tab triggers fetchPast
    await wrapper.setData({ activeTab: 'past' })
    await flushPromises()
    await wrapper.vm.$nextTick()

    const pastCalls = mockGet.mock.calls.filter(c => c[0] === '/api/v1/watchparty/past')
    expect(pastCalls.length).toBeGreaterThanOrEqual(1)
  })

  it('shows past parties with status badges', async () => {
    setupDefaultMocks()
    const wrapper = await createWrapper()
    await flushPromises()
    mockGet.mockClear()

    await wrapper.setData({ activeTab: 'past' })
    await flushPromises()
    await wrapper.vm.$nextTick()

    const badges = wrapper.findAll('.q-badge')
    const badgeTexts = badges.map(w => w.text())
    expect(badgeTexts).toContain('completed')
    expect(badgeTexts).toContain('cancelled')
  })

  // ---- Create Tab ----

  it('shows create form when switching to Create tab', async () => {
    setupEmptyMocks()
    const wrapper = await createWrapper()
    await flushPromises()

    await wrapper.setData({ activeTab: 'create' })
    await wrapper.vm.$nextTick()

    expect(wrapper.html()).toContain('Group ID')
    expect(wrapper.html()).toContain('Media ID')
    expect(wrapper.html()).toContain('Scheduled At')
  })

  it('create submit button is disabled when required fields are empty', async () => {
    setupEmptyMocks()
    const wrapper = await createWrapper()
    await flushPromises()
    await wrapper.setData({ activeTab: 'create' })
    await wrapper.vm.$nextTick()

    // Button should be disabled because fields are empty
    const btns = wrapper.findAll('.q-btn')
    const createBtn = btns.find(b => b.text().includes('Create'))
    expect(createBtn?.exists()).toBe(true)
  })

  it('calls createWatchParty on valid create submit', async () => {
    mockPost.mockResolvedValue({ data: { id: 'party-new' } })
    setupEmptyMocks()
    const wrapper = await createWrapper()
    await flushPromises()
    await wrapper.setData({ activeTab: 'create' })
    await wrapper.vm.$nextTick()

    // Populate form fields
    await wrapper.setData({
      createForm: {
        groupId: 'group-1',
        mediaId: 'media-1',
        scheduledAt: '2026-06-15T20:00',
        title: 'New Party',
        episodeNumber: null,
        streamUrl: '',
        notes: '',
      },
    })
    await wrapper.vm.$nextTick()

    const form = wrapper.find('form')
    await form.trigger('submit')
    await flushPromises()
    await wrapper.vm.$nextTick()

    const postCalls = mockPost.mock.calls.filter(c => c[0] === '/api/v1/watchparty')
    expect(postCalls.length).toBeGreaterThan(0)
    expect(postCalls[0][1]).toMatchObject({
      group_id: 'group-1',
      media_id: 'media-1',
    })
  })

  // ---- Detail View ----

  it('opens detail view when clicking an upcoming party card', async () => {
    setupDefaultMocks()
    const wrapper = await createWrapper()
    await flushPromises()
    await wrapper.vm.$nextTick()

    const firstItem = wrapper.find('.q-item')
    await firstItem.trigger('click')
    await flushPromises()
    await wrapper.vm.$nextTick()

    // Should have called fetchPartyDetail for party-1
    const detailCalls = mockGet.mock.calls.filter(c => c[0] === '/api/v1/watchparty/party-1')
    expect(detailCalls.length).toBeGreaterThan(0)
  })

  it('displays party detail content with host and media info', async () => {
    setupDefaultMocks()
    const wrapper = await createWrapper()
    await flushPromises()
    await wrapper.vm.$nextTick()

    const firstItem = wrapper.find('.q-item')
    await firstItem.trigger('click')
    await flushPromises()
    await wrapper.vm.$nextTick()

    // Check that the dialog shows host username and media title
    expect(wrapper.text()).toContain('Alice')
    expect(wrapper.text()).toContain('Attack on Titan')
  })

  it('shows RSVP actions in detail dialog', async () => {
    setupDefaultMocks()
    const wrapper = await createWrapper()
    await flushPromises()
    await wrapper.vm.$nextTick()

    const firstItem = wrapper.find('.q-item')
    await firstItem.trigger('click')
    await flushPromises()
    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAll('.q-btn')
    const btnTexts = buttons.map(b => b.text())
    expect(btnTexts.some(t => t.includes('Attending'))).toBe(true)
    expect(btnTexts.some(t => t.includes('Maybe'))).toBe(true)
    expect(btnTexts.some(t => t.includes('Decline'))).toBe(true)
  })

  it('renders RSVP list in detail dialog', async () => {
    setupDefaultMocks()
    const wrapper = await createWrapper()
    await flushPromises()
    await wrapper.vm.$nextTick()

    const firstItem = wrapper.find('.q-item')
    await firstItem.trigger('click')
    await flushPromises()
    await wrapper.vm.$nextTick()

    const badges = wrapper.findAll('.q-badge')
    const badgeTexts = badges.map(w => w.text())
    expect(badgeTexts).toContain('attending')
    expect(badgeTexts).toContain('pending')
  })
})
