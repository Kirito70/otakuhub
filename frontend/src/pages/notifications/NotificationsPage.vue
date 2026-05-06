<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5">Notification Bell</div>
        <div class="text-caption text-grey-7">Unread: {{ notificationsStore.unreadCount }}</div>
      </div>
      <div class="row q-gutter-sm">
        <q-btn flat color="primary" label="Preferences" @click="goToPreferences" />
        <q-btn flat color="primary" label="Refresh" :loading="notificationsStore.isLoading" @click="refresh" />
      </div>
    </div>

    <q-banner v-if="notificationsStore.error" class="bg-negative text-white q-mb-md" dense>
      {{ notificationsStore.error }}
    </q-banner>

    <div v-if="notificationsStore.isLoading" class="text-grey-7">Loading notifications...</div>

    <template v-else>
      <div class="row items-center q-gutter-sm q-mb-md">
        <q-btn
          color="primary"
          label="Mark Selected Read"
          :disable="selectedIds.length === 0"
          :loading="notificationsStore.isLoading"
          @click="markSelectedRead"
        />
        <q-btn
          flat
          color="primary"
          label="Mark All Unread Read"
          :disable="unreadIds.length === 0"
          :loading="notificationsStore.isLoading"
          @click="markAllUnreadRead"
        />
      </div>

      <q-list v-if="notificationsStore.items.length > 0" bordered separator>
        <q-item v-for="item in notificationsStore.items" :key="item.id">
          <q-item-section avatar>
            <q-checkbox v-model="selectedIds" :val="item.id" :disable="item.is_read" />
          </q-item-section>
          <q-item-section>
            <q-item-label class="row items-center q-gutter-sm">
              <span>{{ item.title }}</span>
              <q-badge v-if="!item.is_read" color="accent" label="Unread" />
            </q-item-label>
            <q-item-label caption v-if="item.body">{{ item.body }}</q-item-label>
            <q-item-label caption>{{ formatDate(item.created_at) }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>

      <div v-else class="text-grey-7">No notifications yet.</div>
    </template>
  </q-page>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useNotificationsStore } from 'src/stores/notifications'

const router = useRouter()
const notificationsStore = useNotificationsStore()
const selectedIds = ref<string[]>([])

const unreadIds = computed(() => notificationsStore.items.filter((item) => !item.is_read).map((item) => item.id))

function formatDate(value: string): string {
  return new Date(value).toLocaleString()
}

async function refresh(): Promise<void> {
  await notificationsStore.fetchNotifications()
}

async function markSelectedRead(): Promise<void> {
  try {
    await notificationsStore.markAsRead(selectedIds.value)
    selectedIds.value = []
  } catch {
    // Store state already includes error message.
  }
}

async function markAllUnreadRead(): Promise<void> {
  try {
    await notificationsStore.markAsRead(unreadIds.value)
    selectedIds.value = []
  } catch {
    // Store state already includes error message.
  }
}

async function goToPreferences(): Promise<void> {
  await router.push({ name: 'notification-preferences' })
}

onMounted(async () => {
  await notificationsStore.fetchNotifications()
})
</script>
