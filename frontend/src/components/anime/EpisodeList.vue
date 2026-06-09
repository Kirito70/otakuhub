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

    <div class="episode-filter-bar">
      <button
        v-for="f in languageFilterOptions"
        :key="f.value"
        class="filter-pill"
        :class="{ active: selectedLanguageFilter === f.value }"
        @click="$emit('language-filter', f.value)"
      >
        {{ f.label }}
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
  selectedLanguageFilter?: 'all' | 'sub' | 'dub'
}

const props = withDefaults(defineProps<EpisodeListProps>(), {
  watchedEpisodeNumbers: () => [],
  selectedEpisodeNumber: null,
  sortOrder: 'asc',
  selectedLanguageFilter: 'all',
})

const languageFilterOptions = [
  { label: 'All', value: 'all' as const },
  { label: 'SUB', value: 'sub' as const },
  { label: 'DUB', value: 'dub' as const },
]

defineEmits<{
  select: [episodeNumber: number]
  play: [episodeNumber: number]
  retry: []
  'toggle-sort': []
  'language-filter': [filter: 'all' | 'sub' | 'dub']
}>()

const sortedItems = computed(() => {
  let filtered = [...props.items]

  // Apply language filter
  if (props.selectedLanguageFilter === 'sub') {
    filtered = filtered.filter((e) => e.language === 'sub')
  } else if (props.selectedLanguageFilter === 'dub') {
    filtered = filtered.filter((e) => e.language === 'dub')
  }

  // Apply sort
  if (props.sortOrder === 'desc') {
    filtered.sort((a, b) => b.episodeNumber - a.episodeNumber)
  } else {
    filtered.sort((a, b) => a.episodeNumber - b.episodeNumber)
  }
  return filtered
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

  .episode-filter-bar {
    display: flex;
    gap: $space-2;
    margin-bottom: $space-4;

    .filter-pill {
      padding: $space-1 $space-3;
      border-radius: 999px;
      border: $border-subtle;
      background: none;
      color: $text-secondary;
      font-size: $font-size-xs;
      font-weight: 600;
      cursor: pointer;
      transition: all $transition;

      &:hover {
        border-color: $accent-primary;
        color: $accent-primary;
      }

      &.active {
        background: $accent-primary;
        border-color: $accent-primary;
        color: white;
      }
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
