<template>
  <div class="episode-list-section">
    <div class="episode-list-header">
      <div class="episode-list-title">
        <h3>Episodes</h3>
        <span class="episode-count">{{ totalCount }} episodes</span>
      </div>
      <button class="sort-toggle" @click="$emit('toggle-sort')">
        {{ sortOrder === 'asc' ? '▼ Oldest first' : '▲ Newest first' }}
      </button>
    </div>

    <div v-if="loading" class="episode-list-skeleton">
      <div v-for="n in 5" :key="n" class="skeleton-row">
        <div class="skeleton-thumb"></div>
        <div class="skeleton-text">
          <div class="skeleton-line short"></div>
          <div class="skeleton-line"></div>
        </div>
      </div>
    </div>

    <div v-else-if="error" class="episode-list-state">
      <p>{{ error }}</p>
      <button @click="$emit('retry')">Retry</button>
    </div>

    <div v-else-if="items.length === 0" class="episode-list-state">
      <p>No episodes available.</p>
    </div>

    <div v-else class="episode-list">
      <EpisodeItem
        v-for="item in sortedItems"
        :key="item.id"
        :episodeNumber="item.episodeNumber"
        :title="item.title"
        :thumbnailUrl="item.thumbnailUrl"
        :durationMinutes="item.durationMinutes"
        :airDate="item.airDate"
        :isWatched="watchedEpisodeNumbers.includes(item.episodeNumber)"
        :isSelected="selectedEpisodeNumber === item.episodeNumber"
        @click="$emit('select', item.episodeNumber)"
        @play="$emit('play', item.episodeNumber)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { EpisodeItem as EpisodeItemType } from 'src/types/media'
import EpisodeItem from './EpisodeItem.vue'

interface EpisodeListProps {
  items: EpisodeItemType[]
  loading: boolean
  error: string | null
  watchedEpisodeNumbers?: number[]
  selectedEpisodeNumber?: number | null
  totalCount: number
  sortOrder?: 'asc' | 'desc'
}

const props = withDefaults(defineProps<EpisodeListProps>(), {
  watchedEpisodeNumbers: () => [],
  selectedEpisodeNumber: null,
  sortOrder: 'asc',
})

defineEmits<{
  select: [episodeNumber: number]
  play: [episodeNumber: number]
  retry: []
  'toggle-sort': []
}>()

const sortedItems = computed(() => {
  const sorted = [...props.items]
  if (props.sortOrder === 'desc') {
    sorted.sort((a, b) => b.episodeNumber - a.episodeNumber)
  } else {
    sorted.sort((a, b) => a.episodeNumber - b.episodeNumber)
  }
  return sorted
})
</script>

<style lang="scss">
@use 'src/css/tokens' as *;

.episode-list-section {
  .episode-list-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: $space-4;

    .episode-list-title {
      display: flex;
      align-items: baseline;
      gap: $space-2;

      h3 {
        font-size: $font-size-lg;
        font-weight: 700;
        color: $text-primary;
        margin: 0;
      }

      .episode-count {
        font-size: $font-size-sm;
        color: $text-muted;
      }
    }

    .sort-toggle {
      background: none;
      border: 1px solid $border-default;
      border-radius: $radius-md;
      padding: $space-1 $space-3;
      color: $text-secondary;
      font-size: $font-size-sm;
      cursor: pointer;
      transition: all $transition;

      &:hover {
        border-color: $accent-primary;
        color: $accent-primary;
      }
    }
  }

  .episode-list-state {
    text-align: center;
    padding: $space-8;
    color: $text-muted;

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

  .episode-list-skeleton {
    .skeleton-row {
      display: flex;
      gap: $space-3;
      padding: $space-3;

      .skeleton-thumb {
        width: 180px;
        height: 101px;
        border-radius: $radius-sm;
        background: linear-gradient(90deg, $bg-elevated 25%, $bg-hover 50%, $bg-elevated 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
      }

      .skeleton-text {
        flex: 1;

        .skeleton-line {
          height: 14px;
          background: $bg-elevated;
          border-radius: $radius-sm;
          margin-bottom: 8px;

          &.short {
            width: 40%;
          }
        }
      }
    }
  }

  .episode-list {
    display: flex;
    flex-direction: column;
    gap: $space-1;
  }
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
