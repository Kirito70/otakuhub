<template>
  <div class="anime-card" @click="$emit('click', id)">
    <div class="card-cover">
      <img
        v-if="coverImage"
        :src="coverImage"
        :alt="title"
        :class="['card-image', imageLoaded ? 'loaded' : 'loading']"
        loading="lazy"
        @load="onImgLoad"
        @error="onImgError"
      />
      <div v-else class="card-cover-fallback">{{ title.charAt(0) }}</div>
      <div class="card-badges">
        <span v-if="mediaType" class="badge-type">{{ mediaType }}</span>
        <span v-if="episodeCount" class="badge-eps">{{ episodeCount }} eps</span>
      </div>
      <div class="card-hover-overlay">
        <span class="btn-play-hint">▶ Play</span>
      </div>
      <!-- Progress bar overlay for Continue Watching -->
      <div v-if="showProgressBar" class="card-progress-bar">
        <div class="card-progress-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>
    </div>
    <div class="card-info">
      <h3 class="card-title text-truncate">{{ title }}</h3>
      <div class="card-meta">
        <span v-if="hasScore" class="card-score">{{ score!.toFixed(1) }}</span>
        <span v-if="year" class="card-year">{{ year }}</span>
        <span v-if="isNew" class="badge-new">NEW</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface AnimeCardProps {
  id: string
  title: string
  coverImage: string | null
  mediaType: string
  format: string | null
  score: number | null
  year: number | null
  episodeCount: number | null
  isNew?: boolean
  status: string | null
  progress?: number | null
  totalEpisodes?: number | null
}

const props = withDefaults(defineProps<AnimeCardProps>(), {
  isNew: false,
  progress: null,
  totalEpisodes: null,
})

defineEmits<{
  click: [id: string]
}>()

const imageLoaded = ref(false)
const imageError = ref(false)

const hasScore = computed(() => props.score !== null && props.score !== undefined)

const showProgressBar = computed(() => {
  return props.progress !== null && props.progress !== undefined && props.progress > 0
})

const progressPercent = computed(() => {
  if (!showProgressBar.value) return 0
  const total = props.totalEpisodes ?? props.episodeCount ?? 1
  if (total <= 0) return 0
  return Math.min(100, Math.round((props.progress! / total) * 100))
})

function onImgLoad() {
  imageLoaded.value = true
}

function onImgError() {
  imageError.value = true
  imageLoaded.value = true
}
</script>

<style lang="scss">
@use 'src/css/tokens' as *;

.anime-card {
  cursor: pointer;
  border-radius: $radius-md;
  overflow: hidden;
  background: $bg-secondary;
  transition: transform $transition, box-shadow $transition;

  &:hover {
    transform: translateY(-4px);
    box-shadow: $shadow-lg, $glow-purple;
  }

  .card-cover {
    position: relative;
    aspect-ratio: 3 / 4;
    overflow: hidden;
    background: $bg-elevated;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: opacity $transition;

      &.loading {
        opacity: 0;
      }
      &.loaded {
        opacity: 1;
      }
    }

    .card-cover-fallback {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: $font-size-3xl;
      font-weight: 700;
      color: $text-muted;
      background: linear-gradient(135deg, $bg-elevated, $bg-hover);
    }

    .card-badges {
      position: absolute;
      top: $space-2;
      left: $space-2;
      display: flex;
      gap: $space-1;

      .badge-type,
      .badge-eps {
        padding: 2px 6px;
        border-radius: $radius-sm;
        font-size: $font-size-xs;
        font-weight: 600;
        text-transform: uppercase;
      }
      .badge-type {
        background: $accent-primary;
        color: white;
      }
      .badge-eps {
        background: rgba(0, 0, 0, 0.7);
        color: $text-primary;
      }
    }

    .card-hover-overlay {
      position: absolute;
      inset: 0;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity $transition;

      .btn-play-hint {
        color: white;
        font-size: $font-size-lg;
        font-weight: 600;
        padding: $space-2 $space-4;
        border-radius: $radius-md;
        background: rgba($accent-primary, 0.8);
      }
    }

    &:hover .card-hover-overlay {
      opacity: 1;
    }

    .card-progress-bar {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: rgba(255, 255, 255, 0.15);
      z-index: 2;

      .card-progress-fill {
        height: 100%;
        background: $accent-primary;
        transition: width 0.3s ease;
        border-radius: 0 2px 0 0;
      }
    }
  }

  .card-info {
    padding: $space-3;

    .card-title {
      font-size: $font-size-sm;
      font-weight: 600;
      color: $text-primary;
      margin: 0 0 $space-1;
      line-height: 1.3;
    }

    .card-meta {
      display: flex;
      align-items: center;
      gap: $space-2;
      font-size: $font-size-xs;

      .card-score {
        color: $accent-warm;
        font-weight: 700;
      }
      .card-year {
        color: $text-muted;
      }
      .badge-new {
        background: $accent-success;
        color: white;
        padding: 1px 5px;
        border-radius: $radius-sm;
        font-weight: 700;
        font-size: 10px;
      }
    }
  }

  &.skeleton {
    pointer-events: none;

    .card-cover {
      background: linear-gradient(90deg, $bg-elevated 25%, $bg-hover 50%, $bg-elevated 75%);
      background-size: 200% 100%;
      animation: shimmer 1.5s infinite;
    }

    .card-title,
    .card-meta span {
      background: $bg-elevated;
      border-radius: $radius-sm;
      color: transparent;
    }

    .card-title {
      height: 14px;
      margin-bottom: 8px;
    }
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
