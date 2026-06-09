<template>
  <div class="anime-grid-section">
    <div v-if="title" class="section-header">
      <h2>{{ title }}</h2>
    </div>
    <div v-if="loading" class="anime-grid" :style="gridStyle">
      <AnimeCard
        v-for="n in 8"
        :key="'skeleton-' + n"
        id=""
        title=""
        :score="null"
        :year="null"
        :episodeCount="null"
        mediaType=""
        format=""
        coverImage=""
        :isNew="false"
        status=""
        class="skeleton"
      />
    </div>
    <div v-else-if="error" class="grid-error">
      <p>{{ error }}</p>
      <button @click="$emit('retry')">Retry</button>
    </div>
    <div v-else-if="items.length === 0" class="grid-empty">
      <p>{{ emptyMessage || 'No items to display' }}</p>
    </div>
    <div v-else class="anime-grid">
      <AnimeCard
        v-for="item in items"
        :key="item.id"
        :id="item.id"
        :title="item.title"
        :coverImage="item.coverImage"
        :mediaType="item.mediaType"
        :format="item.format"
        :score="item.score"
        :year="item.year"
        :episodeCount="item.episodeCount"
        :isNew="false"
        :status="item.status || null"
        @click="$emit('item-click', item.id)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { MediaItem } from 'src/types/media'
import AnimeCard from './AnimeCard.vue'

interface AnimeGridProps {
  items: MediaItem[]
  loading: boolean
  error: string | null
  columns?: {
    default: number
    sm: number
    md: number
    lg: number
  }
  emptyMessage?: string
  title?: string
}

const props = withDefaults(defineProps<AnimeGridProps>(), {
  columns: () => ({
    default: 2,
    sm: 3,
    md: 4,
    lg: 6,
  }),
  emptyMessage: 'No items to display',
})

defineEmits<{
  'item-click': [id: string]
  retry: []
}>()

const gridStyle = computed(() => {
  return {
    '--grid-cols-default': props.columns.default,
    '--grid-cols-sm': props.columns.sm,
    '--grid-cols-md': props.columns.md,
    '--grid-cols-lg': props.columns.lg,
  }
})
</script>

<style lang="scss">
@use 'src/css/tokens' as *;

.anime-grid-section {
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: $space-4;

    h2 {
      font-size: $font-size-xl;
      font-weight: 700;
      color: $text-primary;
      margin: 0;
    }
  }

  .anime-grid {
    display: grid;
    gap: $space-4;
    grid-template-columns: repeat(v-bind('columns.default'), 1fr);

    @include respond-above(xs) {
      grid-template-columns: repeat(v-bind('columns.sm'), 1fr);
    }
    @include respond-above(sm) {
      grid-template-columns: repeat(v-bind('columns.md'), 1fr);
    }
    @include respond-above(md) {
      grid-template-columns: repeat(v-bind('columns.lg'), 1fr);
    }
  }

  .grid-error,
  .grid-empty {
    text-align: center;
    padding: $space-10;
    color: $text-secondary;

    button {
      margin-top: $space-3;
      padding: $space-2 $space-4;
      background: $accent-primary;
      color: white;
      border: none;
      border-radius: $radius-md;
      cursor: pointer;
    }
  }
}
</style>
