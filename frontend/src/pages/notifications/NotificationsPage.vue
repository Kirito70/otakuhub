<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5">Notifications</div>
        <div class="text-caption text-grey-7">Unread: {{ notificationsStore.unreadCount }}</div>
      </div>
      <div class="row q-gutter-sm">
        <q-btn flat color="primary" label="Preferences" @click="goToPreferences" />
        <q-btn flat color="primary" label="Refresh" :loading="notificationsStore.isLoading" @click="refresh" />
      </div>
    </div>

    <q-tabs v-model="activeTab" class="q-mb-md" dense>
      <q-tab name="all" label="All" />
      <q-tab name="unread" label="Unread" />
    </q-tabs>

    <q-tab-panels v-model="activeTab" animated>
      <!-- All Tab -->
      <q-tab-panel name="all" class="q-pa-none">
        <app-page-state
          :is-loading="notificationsStore.isLoading"
          :error="notificationsStore.error"
          :is-empty="notificationsStore.items.length === 0 && !notificationsStore.isLoading"
          empty-label="No notifications yet."
          loading-label="Loading notifications..."
          @retry="refresh"
        >
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
              label="Mark All Read"
              :disable="notificationsStore.unreadCount === 0"
              :loading="notificationsStore.isLoading"
              @click="markAllUnreadRead"
            />
          </div>

          <q-list bordered separator>
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
        </app-page-state>
      </q-tab-panel>

      <!-- Unread Tab -->
      <q-tab-panel name="unread" class="q-pa-none">
        <app-page-state
          :is-loading="notificationsStore.unreadIsLoading"
          :error="notificationsStore.unreadError"
          :is-empty="notificationsStore.unreadItems.length === 0 && !notificationsStore.unreadIsLoading"
          empty-label="No unread notifications."
          loading-label="Loading unread notifications..."
          @retry="fetchUnread"
        >
          <q-list bordered separator>
            <q-item v-for="item in notificationsStore.unreadItems" :key="item.id">
              <q-item-section>
                <q-item-label>
                  <q-badge color="accent" label="Unread" class="q-mr-xs" />
                  {{ item.title }}
                </q-item-label>
                <q-item-label caption v-if="item.body">{{ item.body }}</q-item-label>
                <q-item-label caption class="text-grey-7">{{ formatDate(item.created_at) }}</q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-btn flat dense color="primary" label="Mark Read" @click="markItemRead(item.id)" />
              </q-item-section>
            </q-item>
          </q-list>

          <div class="row justify-center q-mt-md" v-if="notificationsStore.unreadItems.length > 0">
            <q-btn
              flat
              color="primary"
              label="Mark All Read"
              :loading="notificationsStore.isLoading"
              @click="markAllUnreadRead"
            />
          </div>
        </app-page-state>
      </q-tab-panel>
    </q-tab-panels>
  </q-page>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import AppPageState from 'src/components/AppPageState.vue'
import { useNotificationsStore } from 'src/stores/notifications'

const router = useRouter()
const notificationsStore = useNotificationsStore()
const activeTab = ref<'all' | 'unread'>('all')
const selectedIds = ref<string[]>([])

const unreadIds = computed(() => notificationsStore.items.filter((item) => !item.is_read).map((item) => item.id))

function formatDate(value: string): string {
  return new Date(value).toLocaleString()
}

async function refresh(): Promise<void> {
  await notificationsStore.fetchNotifications()
  if (activeTab.value === 'unread') {
    await notificationsStore.fetchUnreadNotifications()
  }
}

async function fetchUnread(): Promise<void> {
  await notificationsStore.fetchUnreadNotifications()
}

async function markSelectedRead(): Promise<void> {
  try {
    await notificationsStore.markAsRead(selectedIds.value)
    selectedIds.value = []
  } catch {
    // Store state already includes error message.
  }
}

async function markItemRead(id: string): Promise<void> {
  try {
    await notificationsStore.markAsRead([id])
  } catch {
    // Store state already includes error message.
  }
}

async function markAllUnreadRead(): Promise<void> {
  try {
    await notificationsStore.markAllAsRead()
    selectedIds.value = []
  } catch {
    // Store state already includes error message.
  }
}

async function goToPreferences(): Promise<void> {
  await router.push({ name: 'notification-preferences' })
}

// Fetch unread when switching to Unread tab
watch(activeTab, (tab) => {
  if (tab === 'unread' && notificationsStore.unreadItems.length === 0) {
    notificationsStore.fetchUnreadNotifications()
  }
})

onMounted(async () => {
  await notificationsStore.fetchNotifications()
})
</script>
