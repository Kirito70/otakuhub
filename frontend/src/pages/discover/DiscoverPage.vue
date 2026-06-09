<template>
  <q-page class="q-pa-md">
    <div class="row q-col-gutter-md items-end">
      <div class="col-12 col-md-8">
        <q-input v-model="query" outlined label="Search anime, manga, manhwa" @keyup.enter="onSearch">
          <template #append>
            <q-icon name="search" />
          </template>
        </q-input>
      </div>
      <div class="col-12 col-md-2">
        <q-select
          v-model="mediaType"
          outlined
          label="Type"
          :options="mediaTypeOptions"
          option-label="label"
          option-value="value"
          emit-value
          map-options
        />
      </div>
      <div class="col-12 col-md-2">
        <q-btn color="primary" label="Search" class="full-width" :loading="isLoading" @click="onSearch" />
      </div>
    </div>

    <div class="q-mt-md text-caption text-grey-7" v-if="!isLoading && !error">
      {{ total }} result(s)
    </div>

    <app-page-state
      class="q-mt-sm"
      :is-loading="isLoading"
      :error="error"
      :is-empty="items.length === 0"
      empty-label="No results to display yet."
      loading-label="Searching media..."
      @retry="onSearch"
    >
      <div class="row q-col-gutter-md">
        <div v-for="item in items" :key="item.id" class="col-12 col-sm-6 col-md-4 col-lg-3">
          <q-card bordered flat class="cursor-pointer" @click="goToMedia(item.id)">
            <q-img
              :src="item.cover_image_medium ?? undefined"
              :ratio="2 / 3"
              spinner-color="primary"
              no-transition
            >
              <template #error>
                <div class="absolute-full flex flex-center bg-grey-3 text-grey-7">No Cover</div>
              </template>
            </q-img>
            <q-card-section>
              <div class="text-subtitle2 ellipsis-2-lines">{{ item.title_english || item.title_romaji }}</div>
              <div class="text-caption text-grey-7">
                {{ item.media_type || 'Unknown' }} • {{ item.format || 'N/A' }}
              </div>
              <div class="text-caption text-grey-8">Score: {{ item.average_score ?? 'N/A' }}</div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </app-page-state>
  </q-page>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AppPageState from 'src/components/AppPageState.vue'
import { useMediaSearch } from 'src/composables/useMediaSearch'

const router = useRouter()
const route = useRoute()
const query = ref('')
const mediaType = ref<string | undefined>(undefined)

const mediaTypeOptions = [
  { label: 'All', value: undefined },
  { label: 'Anime', value: 'anime' },
  { label: 'Manga', value: 'manga' },
  { label: 'Manhwa', value: 'manhwa' },
]

const { data, total, isLoading, error, search } = useMediaSearch()
const items = computed(() => data.value)

async function onSearch(): Promise<void> {
  await search({
    query: query.value.trim() || undefined,
    type: mediaType.value,
    page: 1,
  })
}

// Support genre pre-filter from navigation (Phase 27.5)
onMounted(() => {
  const genre = route.query.genre as string | undefined
  if (genre) {
    // Set the genre as the initial query label, executing search by genre
    query.value = genre
    search({ genres: [genre], page: 1 })
  }
})

function goToMedia(id: string): void {
  router.push({ name: 'media-detail', params: { id } }).catch(() => undefined)
}
</script>
