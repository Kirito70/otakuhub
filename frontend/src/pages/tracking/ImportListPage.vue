<template>
  <q-page class="q-pa-md">
    <div class="text-h6 q-mb-sm">Import Lists</div>
    <div class="text-caption text-grey-7 q-mb-md">Import your AniList or MyAnimeList list into OtakuHub.</div>

    <q-card bordered flat>
      <q-card-section>
        <q-tabs :model-value="provider" dense align="left" active-color="primary" indicator-color="primary">
          <q-route-tab name="anilist" label="AniList" :to="{ name: 'import-list', query: { ...route.query, provider: 'anilist' } }" exact />
          <q-route-tab name="mal" label="MyAnimeList" :to="{ name: 'import-list', query: { ...route.query, provider: 'mal' } }" exact />
        </q-tabs>
      </q-card-section>

      <q-separator />

      <q-card-section class="q-gutter-md">
        <q-input v-model="username" outlined label="Username (optional)" />
        <q-toggle v-model="overwriteExisting" label="Overwrite existing entries" />

        <q-banner v-if="error" class="bg-red-1 text-red-9" rounded>{{ error }}</q-banner>
        <q-banner v-if="successMessage" class="bg-green-1 text-green-9" rounded>{{ successMessage }}</q-banner>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn color="primary" :loading="isLoading" label="Start Import" @click="onImport" />
      </q-card-actions>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

import { api } from 'src/boot/axios'

type Provider = 'anilist' | 'mal'

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
const username = ref('')
const overwriteExisting = ref(false)
const isLoading = ref(false)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)

async function onImport(): Promise<void> {
  isLoading.value = true
  error.value = null
  successMessage.value = null

  try {
    const endpoint = provider.value === 'anilist' ? '/api/v1/sync/import/anilist' : '/api/v1/sync/import/mal'
    const response = await api.post(endpoint, {
      username: username.value.trim() || undefined,
      overwrite_existing: overwriteExisting.value,
    })

    const jobId = response.data?.job_id ?? 'unknown'
    successMessage.value = `Import started successfully. Job ID: ${jobId}`
  } catch {
    error.value = 'Failed to start import. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>
