import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { api } from 'src/boot/axios'
import type {
  NotificationItem,
  NotificationListResponse,
  NotificationMarkReadResponse,
  NotificationPreferences,
  NotificationPreferencesUpdateRequest,
} from 'src/types/notification'

export const useNotificationsStore = defineStore('notifications', () => {
  const items = ref<NotificationItem[]>([])
  const total = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const preferences = ref<NotificationPreferences | null>(null)
  const isSavingPreferences = ref(false)
  const preferencesError = ref<string | null>(null)

  const unreadCount = computed(() => items.value.filter((item) => !item.is_read).length)

  async function fetchNotifications(limit = 50, offset = 0): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get<NotificationListResponse>('/api/v1/notifications', {
        params: { limit, offset },
      })
      items.value = response.data.items ?? []
      total.value = response.data.total ?? items.value.length
    } catch {
      items.value = []
      total.value = 0
      error.value = 'Failed to load notifications.'
    } finally {
      isLoading.value = false
    }
  }

  async function markAsRead(notificationIds: string[]): Promise<number> {
    if (notificationIds.length === 0) {
      return 0
    }

    isLoading.value = true
    error.value = null
    try {
      const response = await api.patch<NotificationMarkReadResponse>('/api/v1/notifications/read', {
        notification_ids: notificationIds,
      })

      const markedSet = new Set(notificationIds)
      const nowIso = new Date().toISOString()
      items.value = items.value.map((item) =>
        markedSet.has(item.id) ? { ...item, is_read: true, read_at: item.read_at ?? nowIso } : item,
      )

      return response.data.updated_count
    } catch {
      error.value = 'Failed to mark notifications as read.'
      throw new Error('mark_notifications_read_failed')
    } finally {
      isLoading.value = false
    }
  }

  async function fetchPreferences(): Promise<void> {
    preferencesError.value = null
    try {
      const response = await api.get<NotificationPreferences>('/api/v1/notifications/preferences')
      preferences.value = response.data
    } catch {
      preferencesError.value = 'Failed to load notification preferences.'
      throw new Error('load_notification_preferences_failed')
    }
  }

  async function savePreferences(payload: NotificationPreferencesUpdateRequest): Promise<void> {
    isSavingPreferences.value = true
    preferencesError.value = null
    try {
      const response = await api.patch<NotificationPreferences>('/api/v1/notifications/preferences', payload)
      preferences.value = response.data
    } catch {
      preferencesError.value = 'Failed to save notification preferences.'
      throw new Error('save_notification_preferences_failed')
    } finally {
      isSavingPreferences.value = false
    }
  }

  return {
    items,
    total,
    isLoading,
    error,
    unreadCount,
    preferences,
    isSavingPreferences,
    preferencesError,
    fetchNotifications,
    markAsRead,
    fetchPreferences,
    savePreferences,
  }
})
