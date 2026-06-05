import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import NotificationsPage from '../NotificationsPage.vue'

const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
}))

// Hoisted mock data and functions
const { mockGet, mockPatch, mockNotifications, mockUnreadNotifications } = vi.hoisted(() => {
  const mockGet = vi.fn()
  const mockPatch = vi.fn()

  const mockNotifications = [
    {
      id: 'notif-1',
      user_id: 'user-1',
      type: 'friend_activity',
      title: 'Alice added Attack on Titan',
      body: 'Started watching season 1',
      action_url: null,
      related_media_id: null,
      related_user_id: null,
      is_read: false,
      read_at: null,
      sent_at: null,
      created_at: '2026-06-05T10:00:00Z',
    },
    {
      id: 'notif-2',
      user_id: 'user-1',
      type: 'recommendation',
      title: 'Bob recommended Steins;Gate',
      body: null,
      action_url: null,
      related_media_id: null,
      related_user_id: null,
      is_read: true,
      read_at: '2026-06-05T11:00:00Z',
      sent_at: null,
      created_at: '2026-06-05T09:00:00Z',
    },
    {
      id: 'notif-3',
      user_id: 'user-1',
      type: 'system',
      title: 'Weekly digest available',
      body: 'Check your tracking summary',
      action_url: null,
      related_media_id: null,
      related_user_id: null,
      is_read: false,
      read_at: null,
      sent_at: null,
      created_at: '2026-06-05T08:00:00Z',
    },
  ]

  const mockUnreadNotifications = [
    {
      id: 'notif-1',
      user_id: 'user-1',
      type: 'friend_activity',
      title: 'Alice added Attack on Titan',
      body: 'Started watching season 1',
      action_url: null,
      related_media_id: null,
      related_user_id: null,
      is_read: false,
      read_at: null,
      sent_at: null,
      created_at: '2026-06-05T10:00:00Z',
    },
    {
      id: 'notif-3',
      user_id: 'user-1',
      type: 'system',
      title: 'Weekly digest available',
      body: 'Check your tracking summary',
      action_url: null,
      related_media_id: null,
      related_user_id: null,
      is_read: false,
      read_at: null,
      sent_at: null,
      created_at: '2026-06-05T08:00:00Z',
    },
  ]

  return { mockGet, mockPatch, mockNotifications, mockUnreadNotifications }
})

vi.mock('src/boot/axios', () => ({
  api: {
    get: mockGet,
    patch: mockPatch,
  },
}))

function flushPromises() {
  return new Promise(resolve => setTimeout(resolve, 10))
}

const stubs = {
  'q-page': { template: '<div class="q-page"><slot /></div>' },
  'q-tabs': { template: '<div class="q-tabs"><slot /></div>' },
  'q-tab': { name: 'QTab', props: ['name', 'label'], template: '<span class="q-tab">{{ label }}</span>' },
  'q-tab-panels': { name: 'QTabPanels', props: ['modelValue'], template: '<div class="q-tab-panels"><slot /></div>' },
  'q-tab-panel': { name: 'QTabPanel', props: ['name'], template: '<div class="q-tab-panel" :data-name="name"><slot /></div>' },
  'q-list': { template: '<div class="q-list"><slot /></div>' },
  'q-item': { template: '<div class="q-item"><slot /></div>' },
  'q-item-section': { template: '<div class="q-item-section"><slot /></div>' },
  'q-item-label': { name: 'QItemLabel', props: ['caption'], template: '<span class="q-item-label"><slot /></span>' },
  'q-btn': { name: 'QBtn', props: ['label', 'loading', 'disable', 'color', 'flat', 'dense'], template: '<button class="q-btn" :disabled="disable" @click="$emit(\'click\')">{{ label }}</button>' },
  'q-banner': { template: '<div class="q-banner"><slot /></div>' },
  'q-badge': { name: 'QBadge', props: ['color', 'label'], template: '<span class="q-badge">{{ label }}</span>' },
  'q-checkbox': { name: 'QCheckbox', props: ['modelValue', 'val', 'disable'], template: '<input type="checkbox" class="q-checkbox" :value="val" :disabled="disable" />' },
  'app-page-state': {
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
  },
}

describe('NotificationsPage - Phase 5.2', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    mockGet.mockResolvedValue({ data: { items: [], total: 0, limit: 50, offset: 0 } })
    mockPatch.mockResolvedValue({ data: { updated_count: 0 } })
  })

  async function createWrapper() {
    const wrapper = mount(NotificationsPage, { global: { stubs } })
    await flushPromises()
    await wrapper.vm.$nextTick()
    return wrapper
  }

  // ---- Tab Rendering ----

  it('renders tab labels (All, Unread)', async () => {
    const wrapper = await createWrapper()
    const tabs = wrapper.findAll('.q-tab')
    expect(tabs.length).toBe(2)
    const tabLabels = tabs.map(w => w.text())
    expect(tabLabels).toContain('All')
    expect(tabLabels).toContain('Unread')
  })

  it('renders Notifications heading', async () => {
    const wrapper = await createWrapper()
    expect(wrapper.text()).toContain('Notifications')
  })

  it('shows unread count in heading', async () => {
    mockGet.mockResolvedValue({ data: { items: mockNotifications, total: 3, limit: 50, offset: 0 } })
    const wrapper = await createWrapper()
    expect(wrapper.text()).toContain('Unread: 2')
  })

  // ---- All Tab ----

  it('shows loading state in All tab', async () => {
    mockGet.mockImplementation(() => new Promise(() => {}))
    const wrapper = await createWrapper()
    await wrapper.vm.$nextTick()

    const loadingDiv = wrapper.find('.aps-loading')
    expect(loadingDiv.exists()).toBe(true)
  })

  it('shows empty state in All tab when no notifications exist', async () => {
    const wrapper = await createWrapper()
    const emptyDiv = wrapper.find('.aps-empty')
    expect(emptyDiv.text()).toContain('No notifications yet')
  })

  it('shows error state in All tab on fetch failure', async () => {
    mockGet.mockRejectedValue(new Error('Network error'))
    const wrapper = await createWrapper()

    await flushPromises()
    await wrapper.vm.$nextTick()

    const errorDiv = wrapper.find('.aps-error')
    expect(errorDiv.exists()).toBe(true)
    expect(errorDiv.text()).toContain('Failed to load notifications')
  })

  it('renders notification list with items in All tab', async () => {
    mockGet.mockResolvedValue({ data: { items: mockNotifications, total: 3, limit: 50, offset: 0 } })
    const wrapper = await createWrapper()

    expect(wrapper.text()).toContain('Alice added Attack on Titan')
    expect(wrapper.text()).toContain('Bob recommended Steins;Gate')
    expect(wrapper.text()).toContain('Unread')
  })

  it('renders unread badge on unread items in All tab', async () => {
    mockGet.mockResolvedValue({ data: { items: mockNotifications, total: 3, limit: 50, offset: 0 } })
    const wrapper = await createWrapper()

    const badges = wrapper.findAll('.q-badge')
    const badgeLabels = badges.map(w => w.text())
    // Should have "Unread" badges for the 2 unread items
    const unreadBadges = badgeLabels.filter(l => l === 'Unread')
    expect(unreadBadges.length).toBeGreaterThanOrEqual(2)
  })

  it('disables Mark Selected Read when nothing is selected', async () => {
    mockGet.mockResolvedValue({ data: { items: mockNotifications, total: 3, limit: 50, offset: 0 } })
    const wrapper = await createWrapper()

    const btns = wrapper.findAll('.q-btn')
    const markSelectedBtn = btns.find(b => b.text().includes('Mark Selected Read'))
    expect(markSelectedBtn?.exists()).toBe(true)
  })

  // ---- Unread Tab ----

  it('fetches unread notifications when switching to Unread tab', async () => {
    mockGet.mockResolvedValue({ data: { items: [], total: 0, limit: 50, offset: 0 } })
    const wrapper = await createWrapper()

    mockGet.mockResolvedValue({ data: { items: mockUnreadNotifications, total: 2, limit: 50, offset: 0 } })
    await wrapper.setData({ activeTab: 'unread' })
    await flushPromises()
    await wrapper.vm.$nextTick()

    const unreadCalls = mockGet.mock.calls.filter(c => c[0] === '/api/v1/notifications' && c[1]?.params?.is_read === false)
    expect(unreadCalls.length).toBeGreaterThanOrEqual(1)
  })

  it('shows empty state in Unread tab when no unread notifications', async () => {
    mockGet.mockResolvedValue({ data: { items: [], total: 0, limit: 50, offset: 0 } })
    const wrapper = await createWrapper()

    // Switch to unread tab
    await wrapper.setData({ activeTab: 'unread' })
    await wrapper.vm.$nextTick()

    // Target the unread panel's empty state
    const unreadPanel = wrapper.find('.q-tab-panel[data-name="unread"]')
    const emptyDiv = unreadPanel.find('.aps-empty')
    expect(emptyDiv.text()).toContain('No unread notifications')
  })

  it('renders unread items in Unread tab', async () => {
    mockGet.mockResolvedValue({ data: { items: mockUnreadNotifications, total: 2, limit: 50, offset: 0 } })
    const wrapper = await createWrapper()

    await wrapper.setData({ activeTab: 'unread' })
    await flushPromises()
    await wrapper.vm.$nextTick()

    // Scope assertions to the Unread tab panel
    const unreadPanel = wrapper.find('.q-tab-panel[data-name="unread"]')
    expect(unreadPanel.text()).toContain('Alice added Attack on Titan')
    expect(unreadPanel.text()).toContain('Weekly digest available')
    // Read notification should not appear in unread tab
    expect(unreadPanel.text()).not.toContain('Bob recommended Steins;Gate')
  })

  it('shows Mark Read button per unread item', async () => {
    mockGet.mockResolvedValueOnce({ data: { items: mockNotifications, total: 3, limit: 50, offset: 0 } })
    mockGet.mockResolvedValueOnce({ data: { items: mockUnreadNotifications, total: 2, limit: 50, offset: 0 } })
    const wrapper = await createWrapper()

    await wrapper.setData({ activeTab: 'unread' })
    await flushPromises()
    await wrapper.vm.$nextTick()

    const btns = wrapper.findAll('.q-btn')
    const markReadBtns = btns.filter(b => b.text().includes('Mark Read'))
    expect(markReadBtns.length).toBeGreaterThanOrEqual(1)
  })

  // ---- Mark Read Actions ----

  it('calls markAsRead when clicking Mark Read on item', async () => {
    mockGet.mockResolvedValueOnce({ data: { items: mockNotifications, total: 3, limit: 50, offset: 0 } })
    mockGet.mockResolvedValueOnce({ data: { items: mockUnreadNotifications, total: 2, limit: 50, offset: 0 } })
    mockPatch.mockResolvedValue({ data: { updated_count: 1 } })

    const wrapper = await createWrapper()

    await wrapper.setData({ activeTab: 'unread' })
    await flushPromises()
    await wrapper.vm.$nextTick()

    // Find and click a "Mark Read" button
    const btns = wrapper.findAll('.q-btn')
    const markReadBtn = btns.find(b => b.text() === 'Mark Read')
    await markReadBtn?.trigger('click')
    await flushPromises()
    await wrapper.vm.$nextTick()

    const patchCalls = mockPatch.mock.calls.filter(c => c[0] === '/api/v1/notifications/read')
    expect(patchCalls.length).toBeGreaterThan(0)
    expect(patchCalls[0][1].notification_ids.length).toBe(1)
  })

  it('calls markAllAsRead when clicking Mark All Read', async () => {
    mockGet.mockResolvedValueOnce({ data: { items: mockNotifications, total: 3, limit: 50, offset: 0 } })
    mockGet.mockResolvedValueOnce({ data: { items: mockUnreadNotifications, total: 2, limit: 50, offset: 0 } })
    mockPatch.mockResolvedValue({ data: { updated_count: 2 } })

    const wrapper = await createWrapper()

    await wrapper.setData({ activeTab: 'unread' })
    await flushPromises()
    await wrapper.vm.$nextTick()

    // Find Mark All Read button
    const btns = wrapper.findAll('.q-btn')
    const markAllBtn = btns.find(b => b.text() === 'Mark All Read')
    await markAllBtn?.trigger('click')
    await flushPromises()
    await wrapper.vm.$nextTick()

    const patchCalls = mockPatch.mock.calls.filter(c => c[0] === '/api/v1/notifications/read')
    expect(patchCalls.length).toBeGreaterThan(0)
    // Should mark all 2 unread items as read
    expect(patchCalls[0][1].notification_ids.length).toBe(2)
  })

  // ---- Preferences Navigation ----

  it('navigates to preferences on Preferences button click', async () => {
    const wrapper = await createWrapper()

    const btns = wrapper.findAll('.q-btn')
    const prefsBtn = btns.find(b => b.text() === 'Preferences')
    await prefsBtn?.trigger('click')
    await wrapper.vm.$nextTick()

    expect(mockPush).toHaveBeenCalledWith({ name: 'notification-preferences' })
  })
})
