<template>
  <q-page class="q-pa-md">
    <q-tabs v-model="activeTab" class="q-mb-md" dense>
      <q-tab name="group" label="Group Activity" />
      <q-tab name="my" label="My Activity" />
    </q-tabs>

    <q-tab-panels v-model="activeTab" animated>
      <!-- Group Activity Tab -->
      <q-tab-panel name="group" class="q-pa-none">
        <app-page-state
          :is-loading="store.feedIsLoading"
          :error="store.feedError"
          :is-empty="store.feedItems.length === 0 && !store.feedIsLoading"
          empty-label="No group activity yet. Join a group to see what others are watching."
          loading-label="Loading feed..."
          @retry="store.fetchFeed()"
        >
          <q-list separator>
            <activity-feed-item
              v-for="item in store.feedItems"
              :key="item.id"
              :item="item"
              @click="navigateToMedia(item.media_id)"
            />
          </q-list>

          <div v-if="store.feedHasMore" class="text-center q-mt-md">
            <q-btn
              flat
              color="primary"
              label="Load More"
              :loading="store.feedIsLoading"
              :disable="store.feedIsLoading"
              @click="store.fetchFeed(50, store.feedOffset)"
            />
          </div>
        </app-page-state>
      </q-tab-panel>

      <!-- My Activity Tab -->
      <q-tab-panel name="my" class="q-pa-none">
        <app-page-state
          :is-loading="myActivityIsLoading"
          :error="myActivityError"
          :is-empty="myActivityItems.length === 0 && !myActivityIsLoading"
          empty-label="You haven't logged any activity yet. Start tracking anime or manga!"
          loading-label="Loading your activity..."
          @retry="fetchMyActivity()"
        >
          <q-list separator>
            <activity-feed-item
              v-for="item in myActivityItems"
              :key="item.id"
              :item="item"
              @click="navigateToMedia(item.media_id)"
            />
          </q-list>

          <div v-if="myActivityHasMore" class="text-center q-mt-md">
            <q-btn
              flat
              color="primary"
              label="Load More"
              :loading="myActivityIsLoading"
              :disable="myActivityIsLoading"
              @click="fetchMyActivity(myActivityItems.length + 50)"
            />
          </div>
        </app-page-state>
      </q-tab-panel>
    </q-tab-panels>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { api } from 'src/boot/axios'
import AppPageState from 'src/components/AppPageState.vue'
import ActivityFeedItem from 'src/components/social/ActivityFeedItem.vue'
import { useSocialStore } from 'src/stores/social'
import type { FeedActivityItem, SocialFeedResponse } from 'src/types/social'

const router = useRouter()
const store = useSocialStore()

const activeTab = ref<'group' | 'my'>('group')

// My activity uses separate local state since it's a different endpoint
const myActivityItems = ref<FeedActivityItem[]>([])
const myActivityIsLoading = ref(false)
const myActivityError = ref<string | null>(null)
const myActivityHasMore = ref(true)
const PAGE_SIZE = 50

// Fetch group activity on mount if empty
if (store.feedItems.length === 0) {
  store.fetchFeed(PAGE_SIZE, 0)
}

async function fetchMyActivity(limit = PAGE_SIZE): Promise<void> {
  if (myActivityIsLoading.value) return
  myActivityIsLoading.value = true
  myActivityError.value = null
  try {
    const { data } = await api.get<SocialFeedResponse>('/api/v1/lists/me/history', {
      params: { limit },
    })
    myActivityItems.value = data.items
    myActivityHasMore.value = data.items.length < data.total
  } catch (e) {
    myActivityError.value = e instanceof Error ? e.message : 'Failed to load activity'
  } finally {
    myActivityIsLoading.value = false
  }
}

function navigateToMedia(mediaId: string): void {
  router.push({ name: 'media-detail', params: { id: mediaId } })
}

// Fetch my activity on tab switch
// We watch the activeTab in the template via a lazy approach:
// fetch when panel shows and items are empty.
// For simplicity, we use a quick watcher
import { watch } from 'vue'
watch(activeTab, (tab) => {
  if (tab === 'my' && myActivityItems.value.length === 0) {
    fetchMyActivity()
  }
})
</script>
