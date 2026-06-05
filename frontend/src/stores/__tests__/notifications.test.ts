import { flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { useNotificationsStore } from '../notifications'

const { mockGet, mockPatch } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPatch: vi.fn(),
}))

vi.mock('src/boot/axios', () => ({
  api: {
    get: mockGet,
    patch: mockPatch,
  },
}))

const sampleItems = [
  { id: 'n1', type: 'friend_activity', title: 'John watched Naruto EP220', is_read: false, created_at: '2026-06-05T12:00:00Z' },
  { id: 'n2', type: 'recommendation', title: 'Jane recommended One Piece', is_read: true, read_at: '2026-06-05T13:00:00Z', created_at: '2026-06-05T11:00:00Z' },
  { id: 'n3', type: 'new_episode', title: 'Bleach EP381 aired', is_read: false, created_at: '2026-06-04T10:00:00Z' },
]

const samplePreferences = {
  new_episode: true,
  new_chapter: true,
  friend_activity: false,
  recommendations: true,
  watch_party_invite: true,
  watch_party_reminder: false,
  discord_webhook: '',
  telegram_chat_id: '',
  email_enabled: false,
  push_enabled: true,
}

describe('useNotificationsStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetchNotifications loads items', async () => {
    mockGet.mockResolvedValue({ data: { items: sampleItems, total: 3 } })
    const store = useNotificationsStore()

    await store.fetchNotifications()
    expect(mockGet).toHaveBeenCalledWith('/api/v1/notifications', expect.any(Object))
    expect(store.items).toHaveLength(3)
    expect(store.total).toBe(3)
    expect(store.isLoading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('fetchNotifications handles error', async () => {
    mockGet.mockRejectedValue(new Error('API error'))
    const store = useNotificationsStore()

    await store.fetchNotifications()
    expect(store.error).toBe('Failed to load notifications.')
    expect(store.items).toHaveLength(0)
  })

  it('fetchUnreadNotifications loads unread', async () => {
    mockGet.mockResolvedValue({ data: { items: [sampleItems[0]], total: 1 } })
    const store = useNotificationsStore()

    await store.fetchUnreadNotifications()
    expect(mockGet).toHaveBeenCalledWith('/api/v1/notifications', expect.objectContaining({
      params: expect.objectContaining({ is_read: false }),
    }))
    expect(store.unreadItems).toHaveLength(1)
    expect(store.unreadIsLoading).toBe(false)
  })

  it('fetchUnreadNotifications handles error', async () => {
    mockGet.mockRejectedValue(new Error('API error'))
    const store = useNotificationsStore()

    await store.fetchUnreadNotifications()
    expect(store.unreadError).toBe('Failed to load unread notifications.')
    expect(store.unreadItems).toHaveLength(0)
  })

  it('unreadCount computed from items', async () => {
    mockGet.mockResolvedValue({ data: { items: sampleItems, total: 3 } })
    const store = useNotificationsStore()
    await store.fetchNotifications()

    expect(store.unreadCount).toBe(2) // n1 and n3 are unread
  })

  it('markAsRead sends PATCH and updates local state', async () => {
    mockGet.mockResolvedValue({ data: { items: sampleItems, total: 3 } })
    const store = useNotificationsStore()
    await store.fetchNotifications()

    mockPatch.mockResolvedValue({ data: { updated_count: 1 } })
    const updatedCount = await store.markAsRead(['n1'])
    expect(updatedCount).toBe(1)
    expect(mockPatch).toHaveBeenCalledWith('/api/v1/notifications/read', {
      notification_ids: ['n1'],
    })

    // n1 should now be marked read
    const n1 = store.items.find((i) => i.id === 'n1')
    expect(n1?.is_read).toBe(true)
  })

  it('markAsRead returns 0 for empty array', async () => {
    const store = useNotificationsStore()
    const result = await store.markAsRead([])
    expect(result).toBe(0)
    expect(mockPatch).not.toHaveBeenCalled()
  })

  it('markAsRead throws on error', async () => {
    mockGet.mockResolvedValue({ data: { items: sampleItems, total: 3 } })
    const store = useNotificationsStore()
    await store.fetchNotifications()

    mockPatch.mockRejectedValue(new Error('API error'))

    await expect(store.markAsRead(['n1'])).rejects.toThrow('mark_notifications_read_failed')
    expect(store.error).toBe('Failed to mark notifications as read.')
  })

  it('markAllAsRead collects unread IDs and calls markAsRead', async () => {
    mockGet.mockResolvedValue({ data: { items: sampleItems, total: 3 } })
    const store = useNotificationsStore()
    await store.fetchNotifications()

    mockPatch.mockResolvedValue({ data: { updated_count: 2 } })
    const count = await store.markAllAsRead()
    expect(count).toBe(2)
    expect(mockPatch).toHaveBeenCalledWith('/api/v1/notifications/read', {
      notification_ids: ['n1', 'n3'],
    })
  })

  it('markAllAsRead returns 0 when nothing unread', async () => {
    mockGet.mockResolvedValue({
      data: { items: [{ ...sampleItems[0], is_read: true }], total: 1 },
    })
    const store = useNotificationsStore()
    await store.fetchNotifications()

    const count = await store.markAllAsRead()
    expect(count).toBe(0)
  })

  it('fetchPreferences loads preferences', async () => {
    mockGet.mockResolvedValue({ data: samplePreferences })
    const store = useNotificationsStore()

    await store.fetchPreferences()
    expect(mockGet).toHaveBeenCalledWith('/api/v1/notifications/preferences')
    expect(store.preferences?.new_episode).toBe(true)
    expect(store.preferences?.friend_activity).toBe(false)
  })

  it('fetchPreferences throws on error', async () => {
    mockGet.mockRejectedValue(new Error('API error'))
    const store = useNotificationsStore()

    await expect(store.fetchPreferences()).rejects.toThrow('load_notification_preferences_failed')
    expect(store.preferencesError).toBe('Failed to load notification preferences.')
  })

  it('savePreferences sends PATCH and updates state', async () => {
    const updatedPrefs = { ...samplePreferences, friend_activity: true }
    mockPatch.mockResolvedValue({ data: updatedPrefs })
    const store = useNotificationsStore()

    await store.savePreferences({ friend_activity: true })
    expect(mockPatch).toHaveBeenCalledWith('/api/v1/notifications/preferences', {
      friend_activity: true,
    })
    expect(store.preferences?.friend_activity).toBe(true)
    expect(store.isSavingPreferences).toBe(false)
  })

  it('savePreferences throws on error', async () => {
    mockPatch.mockRejectedValue(new Error('API error'))
    const store = useNotificationsStore()

    await expect(store.savePreferences({ friend_activity: true }))
      .rejects.toThrow('save_notification_preferences_failed')
    expect(store.preferencesError).toBe('Failed to save notification preferences.')
  })
})
