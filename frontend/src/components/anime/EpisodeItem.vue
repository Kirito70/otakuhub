<template>
  <div
    class="episode-item"
    :class="{ watched: isWatched, selected: isSelected }"
    @click="$emit('click')"
  >
    <div class="episode-thumb">
      <img
        v-if="thumbnailUrl"
        :src="thumbnailUrl"
        :alt="'Episode ' + episodeNumber"
        loading="lazy"
      />
      <div v-else class="episode-thumb-fallback">{{ episodeNumber }}</div>
      <div class="episode-overlay" @click.stop="$emit('play')">
        <span class="play-icon">▶</span>
      </div>
    </div>
    <div class="episode-info">
      <span class="episode-number">Episode {{ episodeNumber }}</span>
      <h4 class="episode-title text-truncate">{{ title || 'Episode ' + episodeNumber }}</h4>
      <div class="episode-meta">
        <span v-if="durationMinutes" class="episode-duration">{{ durationMinutes }} min</span>
        <span v-if="airDate" class="episode-date">{{ formatDate(airDate) }}</span>
      </div>
    </div>
    <div v-if="isWatched" class="episode-check">
      <span class="check-icon">✓</span>
    </div>
  </div>
</template>

<script setup lang="ts">
export interface EpisodeItemProps {
  episodeNumber: number
  title: string | null
  thumbnailUrl: string | null
  durationMinutes: number | null
  airDate: string | null
  isWatched?: boolean
  isSelected?: boolean
}

withDefaults(defineProps<EpisodeItemProps>(), {
  isWatched: false,
  isSelected: false,
})

defineEmits<{
  click: []
  play: []
}>()

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  } catch {
    return dateStr
  }
}
</script>

<style lang="scss">
@use 'src/css/tokens' as *;

.episode-item {
  display: flex;
  gap: $space-3;
  padding: $space-3;
  border-radius: $radius-md;
  cursor: pointer;
  transition: background $transition;
  align-items: flex-start;

  &:hover {
    background: $bg-hover;
  }

  &.selected {
    background: rgba($accent-primary, 0.15);
    border: 1px solid rgba($accent-primary, 0.3);
  }

  &.watched {
    .episode-title {
      color: $text-muted;
    }
    .episode-number {
      color: $text-muted;
    }
  }

  .episode-thumb {
    position: relative;
    flex-shrink: 0;
    width: 180px;
    height: 101px;
    border-radius: $radius-sm;
    overflow: hidden;
    background: $bg-elevated;

    @include respond-below(sm) {
      width: 120px;
      height: 68px;
    }

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .episode-thumb-fallback {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: $font-size-2xl;
      font-weight: 700;
      color: $text-muted;
      background: $bg-elevated;
    }

    .episode-overlay {
      position: absolute;
      inset: 0;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity $transition;

      .play-icon {
        color: white;
        font-size: 1.5rem;
      }
    }

    &:hover .episode-overlay {
      opacity: 1;
    }
  }

  .episode-info {
    flex: 1;
    min-width: 0;

    .episode-number {
      font-size: $font-size-xs;
      color: $accent-primary;
      font-weight: 600;
      text-transform: uppercase;
    }

    .episode-title {
      font-size: $font-size-sm;
      font-weight: 600;
      color: $text-primary;
      margin: $space-1 0;
      line-height: 1.3;
    }

    .episode-meta {
      display: flex;
      gap: $space-3;
      font-size: $font-size-xs;
      color: $text-muted;
    }
  }

  .episode-check {
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: $accent-success;
    display: flex;
    align-items: center;
    justify-content: center;

    .check-icon {
      color: white;
      font-size: 0.75rem;
      font-weight: 700;
    }
  }
}
</style>
