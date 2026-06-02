<template>
  <q-page class="q-pa-md">
    <div class="text-h6 q-mb-md">My List</div>

    <q-banner v-if="error" class="bg-red-1 text-red-9 q-mb-md" rounded>{{ error }}</q-banner>

    <q-tabs :model-value="activeStatus" align="left" dense active-color="primary" indicator-color="primary" class="text-capitalize">
      <q-route-tab
        v-for="status in statuses"
        :key="status"
        :name="status"
        :label="statusLabel(status)"
        :to="{ name: 'my-list-status', params: { status } }"
        exact
      />
    </q-tabs>

    <q-separator class="q-my-sm" />

    <div v-if="isLoading" class="row justify-center q-my-lg">
      <q-spinner color="primary" size="34px" />
    </div>

    <q-list v-else bordered separator>
      <q-item v-for="entry in currentItems" :key="entry.id">
        <q-item-section avatar top>
          <q-avatar rounded size="52px">
            <img v-if="entry.cover_image_medium" :src="entry.cover_image_medium" alt="cover" />
            <q-icon v-else name="movie" />
          </q-avatar>
        </q-item-section>
        <q-item-section>
          <q-item-label class="cursor-pointer" @click="goToMedia(entry.media_id)">{{ entry.title || entry.media_id }}</q-item-label>
          <q-item-label caption class="q-mt-xs">Progress</q-item-label>
          <progress-widget
            :model-value="entry.progress"
            @change="(value) => onProgressChange(entry.media_id, value)"
          />

          <q-item-label caption class="q-mt-sm">Score</q-item-label>
          <score-widget
            :model-value="entry.score ?? null"
            @change="(value) => onScoreChange(entry.media_id, value)"
          />
        </q-item-section>
      </q-item>
    </q-list>

    <div v-if="!isLoading && currentItems.length === 0" class="text-grey-7 q-mt-md">No entries for this status yet.</div>

    <q-separator class="q-my-lg" />

    <div class="text-subtitle1 q-mb-sm">Custom Lists</div>
    <q-card bordered flat class="q-mb-md">
      <q-card-section class="row q-col-gutter-md">
        <div class="col-12 col-md-4">
          <q-input v-model="customListName" outlined label="List name" />
        </div>
        <div class="col-12 col-md-6">
          <q-input v-model="customListDescription" outlined label="Description (optional)" />
        </div>
        <div class="col-12 col-md-2">
          <q-btn color="primary" class="full-width" label="Create" :loading="isCreatingCustomList" @click="onCreateCustomList" />
        </div>
      </q-card-section>
    </q-card>

    <q-list bordered separator>
      <q-item v-for="list in customLists" :key="list.id">
        <q-item-section>
          <q-item-label>{{ list.name }}</q-item-label>
          <q-item-label caption>{{ list.description || 'No description' }}</q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-btn flat dense icon="playlist_add" label="Set entries" @click="openManageEntries(list.id)" />
        </q-item-section>
      </q-item>
    </q-list>

    <q-dialog v-model="showManageEntriesDialog">
      <q-card style="min-width: 360px; max-width: 560px; width: 100%">
        <q-card-section>
          <div class="text-h6">Set Custom List Entries</div>
          <div class="text-caption text-grey-7">Paste media IDs separated by commas.</div>
        </q-card-section>
        <q-card-section>
          <q-input v-model="entryIdsCsv" type="textarea" outlined autogrow label="Media IDs" />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Save" :loading="isSavingEntries" @click="onSaveCustomListEntries" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import ProgressWidget from 'src/components/tracking/ProgressWidget.vue'
import ScoreWidget from 'src/components/tracking/ScoreWidget.vue'
import { useTrackingStore } from 'src/stores/tracking'
import type { WatchStatus } from 'src/types/tracking'

const route = useRoute()
const router = useRouter()

const trackingStore = useTrackingStore()
const statuses: WatchStatus[] = [
  'watching',
  'reading',
  'completed',
  'paused',
  'dropped',
  'plan_to_watch',
  'plan_to_read',
  'rewatching',
  'rereading',
]

const defaultStatus: WatchStatus = 'watching'

const activeStatus = computed<WatchStatus>(() => {
  const raw = route.params.status
  const status = Array.isArray(raw) ? raw[0] : raw
  if (typeof status === 'string' && statuses.includes(status as WatchStatus)) {
    return status as WatchStatus
  }

  return defaultStatus
})
const customListName = ref('')
const customListDescription = ref('')
const isCreatingCustomList = ref(false)
const isSavingEntries = ref(false)
const showManageEntriesDialog = ref(false)
const selectedCustomListId = ref<string | null>(null)
const entryIdsCsv = ref('')

const currentItems = computed(() => trackingStore.byStatus[activeStatus.value] ?? [])
const isLoading = computed(() => trackingStore.isLoading)
const error = computed(() => trackingStore.error)
const customLists = computed(() => trackingStore.customLists)

function statusLabel(status: WatchStatus): string {
  return status.replaceAll('_', ' ')
}

async function onProgressChange(mediaId: string, progress: number): Promise<void> {
  await trackingStore.updateEntry(mediaId, { progress })
}

async function onScoreChange(mediaId: string, score: number | null): Promise<void> {
  await trackingStore.updateEntry(mediaId, { score })
}

function goToMedia(mediaId: string): void {
  router.push({ name: 'media-detail', params: { id: mediaId } }).catch(() => undefined)
}

async function onCreateCustomList(): Promise<void> {
  if (!customListName.value.trim()) {
    return
  }

  isCreatingCustomList.value = true
  try {
    await trackingStore.createCustomList({
      name: customListName.value.trim(),
      description: customListDescription.value.trim() || undefined,
    })

    customListName.value = ''
    customListDescription.value = ''
  } finally {
    isCreatingCustomList.value = false
  }
}

function openManageEntries(listId: string): void {
  selectedCustomListId.value = listId
  entryIdsCsv.value = ''
  showManageEntriesDialog.value = true
}

async function onSaveCustomListEntries(): Promise<void> {
  if (!selectedCustomListId.value) {
    return
  }

  const mediaIds = entryIdsCsv.value
    .split(',')
    .map((id) => id.trim())
    .filter((id) => id.length > 0)

  isSavingEntries.value = true
  try {
    await trackingStore.replaceCustomListEntries(selectedCustomListId.value, {
      entries: mediaIds.map((mediaId, index) => ({ media_id: mediaId, sort_order: index })),
    })

    showManageEntriesDialog.value = false
  } finally {
    isSavingEntries.value = false
  }
}

// Fetch list data on mount and whenever the route param (tab) changes.
// Using immediate: true ensures the initial mount also triggers the watch.
watch(
  () => route.params.status,
  async () => {
    await trackingStore.fetchMyList(activeStatus.value)
  },
  { immediate: true },
)
</script>
