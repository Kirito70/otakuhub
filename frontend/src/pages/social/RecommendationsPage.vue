<template>
  <q-page class="q-pa-md">
    <q-tabs v-model="activeTab" class="q-mb-md" dense>
      <q-tab name="inbox" label="Inbox" />
      <q-tab name="sent" label="Sent" />
    </q-tabs>

    <q-tab-panels v-model="activeTab" animated>
      <!-- Inbox Tab -->
      <q-tab-panel name="inbox" class="q-pa-none">
        <app-page-state
          :is-loading="store.inboxIsLoading"
          :error="store.inboxError"
          :is-empty="store.inboxItems.length === 0 && !store.inboxIsLoading"
          empty-label="No recommendations in your inbox yet."
          loading-label="Loading inbox..."
          @retry="store.fetchInbox()"
        >
          <recommend-card
            v-for="rec in store.inboxItems"
            :key="rec.id"
            :rec="rec"
            direction="incoming"
            :is-acknowledging="store.acknowledgeStatus[rec.id] === 'loading'"
            @acknowledge="store.acknowledgeRecommendation(rec.id)"
            @view-media="navigateToMedia(rec.media_id)"
          />

          <div v-if="store.inboxHasMore" class="text-center q-mt-md">
            <q-btn
              flat
              color="primary"
              label="Load More"
              :loading="store.inboxIsLoading"
              :disable="store.inboxIsLoading"
              @click="store.fetchInbox(50, store.inboxOffset)"
            />
          </div>
        </app-page-state>
      </q-tab-panel>

      <!-- Sent Tab -->
      <q-tab-panel name="sent" class="q-pa-none">
        <app-page-state
          :is-loading="store.sentIsLoading"
          :error="store.sentError"
          :is-empty="store.sentItems.length === 0 && !store.sentIsLoading"
          empty-label="You haven't sent any recommendations yet."
          loading-label="Loading sent recommendations..."
          @retry="store.fetchSent()"
        >
          <recommend-card
            v-for="rec in store.sentItems"
            :key="rec.id"
            :rec="rec"
            direction="sent"
            @view-media="navigateToMedia(rec.media_id)"
          />

          <div v-if="store.sentHasMore" class="text-center q-mt-md">
            <q-btn
              flat
              color="primary"
              label="Load More"
              :loading="store.sentIsLoading"
              :disable="store.sentIsLoading"
              @click="store.fetchSent(50, store.sentOffset)"
            />
          </div>
        </app-page-state>
      </q-tab-panel>
    </q-tab-panels>
  </q-page>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

import AppPageState from 'src/components/AppPageState.vue'
import RecommendCard from 'src/components/social/RecommendCard.vue'
import { useSocialStore } from 'src/stores/social'
import { ref } from 'vue'

const router = useRouter()
const store = useSocialStore()

const activeTab = ref<'inbox' | 'sent'>('inbox')

// Fetch inbox on mount if empty
if (store.inboxItems.length === 0) {
  store.fetchInbox(50, 0)
}

function navigateToMedia(mediaId: string): void {
  router.push({ name: 'media-detail', params: { id: mediaId } })
}
</script>
