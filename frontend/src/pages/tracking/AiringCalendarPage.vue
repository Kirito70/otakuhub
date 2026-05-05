<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-col-gutter-md q-mb-md">
      <div class="col">
        <div class="text-h6">Airing Calendar</div>
        <div class="text-caption text-grey-7">Upcoming episodes and chapters</div>
      </div>
      <div class="col-auto">
        <q-btn outline color="primary" icon="refresh" label="Refresh" :loading="isLoading" @click="fetchAiring" />
      </div>
    </div>

    <q-banner v-if="error" class="bg-red-1 text-red-9 q-mb-md" rounded>{{ error }}</q-banner>

    <q-list bordered separator>
      <q-item v-for="item in items" :key="item.id" clickable :to="{ name: 'media-detail', params: { id: item.id } }">
        <q-item-section avatar>
          <q-avatar rounded size="56px">
            <img v-if="item.cover_image_medium" :src="item.cover_image_medium" alt="cover" />
            <q-icon v-else name="event" />
          </q-avatar>
        </q-item-section>
        <q-item-section>
          <q-item-label>{{ item.title_english || item.title_romaji }}</q-item-label>
          <q-item-label caption>
            {{ item.media_type || 'Unknown' }} • {{ item.status || 'Unknown status' }}
          </q-item-label>
        </q-item-section>
      </q-item>
    </q-list>

    <div v-if="!isLoading && items.length === 0" class="text-grey-7 q-mt-md">
      No airing entries available right now.
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { api } from 'src/boot/axios'
import type { MediaSearchItem } from 'src/types/media'

const items = ref<MediaSearchItem[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)

async function fetchAiring(): Promise<void> {
  isLoading.value = true
  error.value = null

  try {
    const response = await api.get('/api/v1/media/airing', {
      params: { page: 1, per_page: 50 },
    })

    const rawItems = Array.isArray(response.data?.items) ? response.data.items : []
    items.value = rawItems.map((item: Record<string, unknown>) => ({
      id: String(item.id ?? ''),
      title_romaji: String(item.title_romaji ?? item.title ?? 'Untitled'),
      title_english: (item.title_english as string | null | undefined) ?? null,
      cover_image_medium: (item.cover_image_medium as string | null | undefined) ?? null,
      media_type: (item.media_type as string | null | undefined) ?? null,
      format: (item.format as string | null | undefined) ?? null,
      average_score: (item.average_score as number | null | undefined) ?? null,
      status: (item.status as string | null | undefined) ?? null,
    }))
  } catch {
    error.value = 'Failed to load airing calendar.'
    items.value = []
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await fetchAiring()
})
</script>
