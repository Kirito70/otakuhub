<template>
  <q-page class="q-pa-md">
    <div class="search-results-header">
      <h1 class="search-results-title">Search Results</h1>
      <p v-if="query && !isLoading && !error" class="search-results-meta">
        {{ total }} result(s) for "{{ query }}"
      </p>
    </div>

    <div v-if="!query" class="search-prompt">
      <p>Enter a search term to find anime, manga, or manhwa.</p>
    </div>

    <app-page-state
      v-else
      :is-loading="isLoading"
      :error="error"
      :is-empty="items.length === 0 && !isLoading"
      empty-label="No results found. Try a different search term."
      loading-label="Searching..."
      @retry="onSearch"
    >
      <div class="row q-col-gutter-md">
        <div
          v-for="item in items"
          :key="item.id"
          class="col-6 col-sm-4 col-md-3 col-lg-2"
        >
          <anime-card v-bind="item" @click="goToMedia(item.id)" />
        </div>
      </div>
    </app-page-state>
  </q-page>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AppPageState from 'src/components/AppPageState.vue'
import AnimeCard from 'src/components/anime/AnimeCard.vue'
import { useMediaSearch } from 'src/composables/useMediaSearch'

const route = useRoute()
const router = useRouter()

const query = ref('')

const { data, total, isLoading, error, search } = useMediaSearch()
const items = computed(() => data.value)

function goToMedia(id: string): void {
  router.push({ name: 'media-detail', params: { id } }).catch(() => undefined)
}

async function onSearch(): Promise<void> {
  if (!query.value.trim()) return
  await search({
    query: query.value.trim(),
    page: 1,
  })
}

// Sync from route query param
watch(
  () => route.query.q,
  (newQ) => {
    const q = typeof newQ === 'string' ? newQ : ''
    if (q !== query.value) {
      query.value = q
      if (q.trim()) onSearch()
    }
  },
  { immediate: true },
)
</script>

<style scoped lang="scss">
@use 'src/css/tokens' as *;

.search-results-header {
  margin-bottom: $space-4;
}

.search-results-title {
  font-size: $font-size-xl;
  font-weight: 700;
  color: $text-primary;
  margin: 0 0 $space-1;
}

.search-results-meta {
  font-size: $font-size-sm;
  color: $text-muted;
  margin: 0;
}

.search-prompt {
  text-align: center;
  padding: $space-10 0;
  color: $text-muted;
  font-size: $font-size-md;
}
</style>
