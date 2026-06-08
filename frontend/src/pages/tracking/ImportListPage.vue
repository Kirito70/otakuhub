<template>
  <q-page class="q-pa-md">
    <div class="text-h6 q-mb-sm">Import Lists</div>
    <div class="text-caption text-grey-7 q-mb-md">Import your AniList or MyAnimeList list into OtakuHub.</div>

    <!-- Import form -->
    <q-card bordered flat>
      <q-card-section>
        <q-tabs :model-value="provider" dense align="left" active-color="primary" indicator-color="primary">
          <q-route-tab name="anilist" label="AniList" :to="{ name: 'import-list', query: { ...route.query, provider: 'anilist' } }" exact />
          <q-route-tab name="mal" label="MyAnimeList" :to="{ name: 'import-list', query: { ...route.query, provider: 'mal' } }" exact />
        </q-tabs>
      </q-card-section>

      <q-separator />

      <q-form @submit.prevent="onImport" greedy>
        <q-card-section class="q-gutter-md">
          <!-- Provider info banner -->
          <q-banner v-if="provider === 'anilist'" class="bg-blue-1 text-blue-9" rounded dense>
            <template #avatar><q-icon name="info" /></template>
            AniList usernames: 3–20 characters, letters, numbers, dashes, and underscores.
          </q-banner>
          <q-banner v-else class="bg-blue-1 text-blue-9" rounded dense>
            <template #avatar><q-icon name="info" /></template>
            MyAnimeList usernames: 3–16 characters, letters, numbers, and underscores.
          </q-banner>

          <q-input
            v-model="username"
            outlined
            label="Username (optional)"
            :rules="usernameRules"
            lazy-rules
            data-name="import-username"
          />
          <q-toggle v-model="overwriteExisting" label="Overwrite existing entries" data-name="overwrite-toggle" />

          <!-- Error banner -->
          <q-banner v-if="error" class="bg-red-1 text-red-9" rounded data-name="error-banner">
            {{ error }}
          </q-banner>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            color="primary"
            :loading="isImporting"
            :disable="isPolling"
            label="Start Import"
            type="submit"
            data-name="import-btn"
          />
        </q-card-actions>
      </q-form>
    </q-card>

    <!-- Job status card (visible after import starts) -->
    <q-card v-if="activeJob" bordered flat class="q-mt-md" data-name="job-status-card">
      <q-card-section>
        <div class="text-subtitle2 q-mb-sm">Import Status</div>

        <!-- Running state -->
        <template v-if="activeJob.status === 'running'">
          <div class="row items-center q-gutter-sm q-mb-sm">
            <q-spinner size="sm" color="primary" />
            <span class="text-primary">Import in progress…</span>
          </div>
          <q-linear-progress :value="progressRatio" color="primary" class="q-mb-sm" />
          <div class="text-caption text-grey-7">
            {{ activeJob.processed_items }} item{{ activeJob.processed_items !== 1 ? 's' : '' }} processed<span v-if="activeJob.total_items"> of {{ activeJob.total_items }}</span>
          </div>
        </template>

        <!-- Completed state -->
        <template v-else-if="activeJob.status === 'completed'">
          <div class="row items-center q-gutter-sm q-mb-sm">
            <q-icon name="check_circle" color="positive" size="sm" />
            <span class="text-positive">Import completed</span>
          </div>
          <div class="text-caption text-grey-7">
            {{ activeJob.processed_items }} item{{ activeJob.processed_items !== 1 ? 's' : '' }} imported.
          </div>
        </template>

        <!-- Partial state -->
        <template v-else-if="activeJob.status === 'partial'">
          <div class="row items-center q-gutter-sm q-mb-sm">
            <q-icon name="warning" color="warning" size="sm" />
            <span class="text-warning">Import completed with errors</span>
          </div>
          <div class="text-caption text-grey-7">
            {{ activeJob.processed_items }} item{{ activeJob.processed_items !== 1 ? 's' : '' }} imported,
            {{ activeJob.failed_items }} failed.
          </div>
        </template>

        <!-- Failed state -->
        <template v-else-if="activeJob.status === 'failed'">
          <div class="row items-center q-gutter-sm q-mb-sm">
            <q-icon name="error" color="negative" size="sm" />
            <span class="text-negative">Import failed</span>
          </div>
          <div v-if="activeJob.error_log" class="text-caption text-negative q-mb-sm">
            {{ activeJob.error_log }}
          </div>
        </template>

        <div class="text-caption text-grey-5 q-mt-xs">
          Job ID: {{ activeJob.id }}
        </div>
      </q-card-section>

      <q-card-actions v-if="activeJob.status !== 'running'" align="right">
        <q-btn flat label="Start New Import" color="primary" @click="resetImport" data-name="new-import-btn" />
      </q-card-actions>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { api } from 'src/boot/axios'
import type { Provider, SyncImportResponse, SyncJobDetail } from 'src/types/tracking'

const route = useRoute()
const defaultProvider: Provider = 'anilist'

const provider = computed<Provider>(() => {
  const raw = route.query.provider
  const value = Array.isArray(raw) ? raw[0] : raw
  if (value === 'anilist' || value === 'mal') {
    return value
  }
  return defaultProvider
})

// -- Provider-specific validation rules --

const anilistUsernameRules = [
  (val: string) => !val || (val.length >= 3 && val.length <= 20) || '3–20 characters',
  (val: string) => !val || /^[a-zA-Z0-9_-]+$/.test(val) || 'Letters, numbers, dashes, and underscores only',
]

const malUsernameRules = [
  (val: string) => !val || (val.length >= 3 && val.length <= 16) || '3–16 characters',
  (val: string) => !val || /^[a-zA-Z0-9_]+$/.test(val) || 'Letters, numbers, and underscores only',
]

const usernameRules = computed(() =>
  provider.value === 'anilist' ? anilistUsernameRules : malUsernameRules,
)

// -- Form state --

const username = ref('')
const overwriteExisting = ref(false)
const isImporting = ref(false)
const error = ref<string | null>(null)

// -- Job polling state --

const activeJob = ref<SyncJobDetail | null>(null)
const isPolling = ref(false)
const pollTimer = ref<ReturnType<typeof setInterval> | null>(null)

const progressRatio = computed(() => {
  if (!activeJob.value || !activeJob.value.total_items || activeJob.value.total_items === 0) return 0
  return Math.min(activeJob.value.processed_items / activeJob.value.total_items, 1)
})

async function onImport(): Promise<void> {
  // Reset previous job state
  activeJob.value = null
  error.value = null
  isImporting.value = true

  try {
    const endpoint = provider.value === 'anilist' ? '/api/v1/sync/import/anilist' : '/api/v1/sync/import/mal'
    const response = await api.post<SyncImportResponse>(endpoint, {
      username: username.value.trim() || undefined,
      overwrite_existing: overwriteExisting.value,
    })

    const jobId = response.data.job_id
    if (jobId) {
      // Start polling the job status
      startPolling(jobId)
    } else {
      error.value = 'Import started but no job ID was returned.'
    }
  } catch (err: unknown) {
    const status = (err as { response?: { status?: number } })?.response?.status
    if (status === 400) {
      error.value = `Invalid request for ${provider.value === 'anilist' ? 'AniList' : 'MyAnimeList'} import. Check your username.`
    } else if (status === 429) {
      error.value = 'Too many requests. Please wait a moment and try again.'
    } else {
      error.value = 'Failed to start import. Please try again.'
    }
  } finally {
    isImporting.value = false
  }
}

function startPolling(jobId: string): void {
  isPolling.value = true
  pollImmediately(jobId)

  // Poll every 3 seconds
  pollTimer.value = setInterval(() => {
    pollJobStatus(jobId)
  }, 3000)
}

async function pollImmediately(jobId: string): Promise<void> {
  try {
    const response = await api.get<SyncJobDetail>(`/api/v1/sync/jobs/${jobId}`)
    activeJob.value = response.data
    if (response.data.status !== 'running' && pollTimer.value) {
      clearInterval(pollTimer.value)
      pollTimer.value = null
      isPolling.value = false
    }
  } catch {
    // First poll might fail if job not yet visible; continue polling
  }
}

async function pollJobStatus(jobId: string): Promise<void> {
  try {
    const response = await api.get<SyncJobDetail>(`/api/v1/sync/jobs/${jobId}`)
    activeJob.value = response.data

    // Stop polling when job is no longer running
    if (response.data.status !== 'running') {
      if (pollTimer.value) {
        clearInterval(pollTimer.value)
        pollTimer.value = null
      }
      isPolling.value = false
    }
  } catch {
    // Swallow polling errors — retry on next interval
  }
}

function resetImport(): void {
  activeJob.value = null
  isPolling.value = false
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

// Clean up polling on unmount
watch(
  () => provider.value,
  () => {
    resetImport()
  },
)

defineExpose({ onImport })
</script>
