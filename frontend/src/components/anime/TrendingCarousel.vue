<template>
  <div class="trending-carousel">
    <div class="carousel-header">
      <h2 class="carousel-title">{{ title }}</h2>
      <div class="carousel-arrows" v-if="!loading && items.length > 0">
        <button class="arrow-btn" @click="scroll(-1)" :disabled="atStart">
          ‹
        </button>
        <button class="arrow-btn" @click="scroll(1)" :disabled="atEnd">
          ›
        </button>
      </div>
    </div>

    <div class="carousel-viewport" ref="viewportRef">
      <div v-if="loading" class="carousel-skeleton">
        <div v-for="n in 7" :key="n" class="skeleton-card">
          <div class="skeleton-cover"></div>
          <div class="skeleton-info">
            <div class="skeleton-line"></div>
            <div class="skeleton-line short"></div>
          </div>
        </div>
      </div>

      <div v-else-if="error" class="carousel-state">
        <p>{{ error }}</p>
        <button @click="$emit('retry')">Retry</button>
      </div>

      <div v-else-if="items.length === 0" class="carousel-state">
        <p>No trending items available.</p>
      </div>

      <div
        v-else
        class="carousel-track"
        ref="trackRef"
        @scroll="onScroll"
      >
        <AnimeCard
          v-for="item in items"
          :key="item.id"
          :id="item.id"
          :title="item.title"
          :cover-image="item.coverImage"
          :media-type="item.mediaType"
          :format="item.format"
          :score="item.score"
          :year="item.year"
          :episode-count="item.episodeCount"
          :is-new="false"
          :status="item.status"
          class="carousel-card"
          :style="{ minWidth: itemWidth + 'px', maxWidth: itemWidth + 'px' }"
          @click="$emit('item-click', item.id)"
        />
      </div>

      <!-- Gradient fades on edges -->
      <div class="carousel-fade carousel-fade-left"></div>
      <div class="carousel-fade carousel-fade-right"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import type { MediaItem } from 'src/types/media'
import AnimeCard from './AnimeCard.vue'

interface TrendingCarouselProps {
  items: MediaItem[]
  loading: boolean
  error: string | null
  title?: string
  itemWidth?: number
}

const props = withDefaults(defineProps<TrendingCarouselProps>(), {
  title: 'Trending Now',
  itemWidth: 180,
})

const emit = defineEmits<{
  'item-click': [id: string]
  retry: []
}>()

const viewportRef = ref<HTMLElement | null>(null)
const trackRef = ref<HTMLElement | null>(null)
const scrollPos = ref(0)
const maxScroll = ref(0)

const atStart = computed(() => scrollPos.value <= 10)
const atEnd = computed(() => scrollPos.value >= maxScroll.value - 10)

function scroll(direction: number) {
  if (!trackRef.value) return
  trackRef.value.scrollBy({
    left: props.itemWidth * 3 * direction,
    behavior: 'smooth',
  })
}

function onScroll() {
  if (!trackRef.value) return
  scrollPos.value = trackRef.value.scrollLeft
}

function updateMaxScroll() {
  if (!trackRef.value || !viewportRef.value) return
  maxScroll.value = trackRef.value.scrollWidth - viewportRef.value.clientWidth
}

function onResize() {
  updateMaxScroll()
}

onMounted(() => {
  updateMaxScroll()
  window.addEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
})
</script>

<style lang="scss">
@use 'src/css/tokens' as *;

.trending-carousel {
  .carousel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: $space-4;

    .carousel-title {
      font-size: $font-size-xl;
      font-weight: 700;
      color: $text-primary;
      margin: 0;
    }

    .carousel-arrows {
      display: flex;
      gap: $space-2;

      .arrow-btn {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        border: 1px solid $border-default;
        background: $bg-secondary;
        color: $text-primary;
        font-size: 1.3rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all $transition;

        &:hover:not(:disabled) {
          border-color: $accent-primary;
          color: $accent-primary;
          background: rgba($accent-primary, 0.1);
        }

        &:disabled {
          opacity: 0.3;
          cursor: not-allowed;
        }
      }
    }
  }

  .carousel-viewport {
    position: relative;
    overflow: hidden;

    .carousel-track {
      display: flex;
      gap: $space-4;
      overflow-x: auto;
      scroll-behavior: smooth;
      scrollbar-width: none;
      -ms-overflow-style: none;
      padding: $space-2 0;

      &::-webkit-scrollbar {
        display: none;
      }

      .carousel-card {
        flex-shrink: 0;
      }
    }

    .carousel-fade {
      position: absolute;
      top: 0;
      bottom: 0;
      width: 60px;
      pointer-events: none;
      z-index: 2;

      &-left {
        left: 0;
        background: linear-gradient(to right, $bg-primary 0%, transparent 100%);
      }

      &-right {
        right: 0;
        background: linear-gradient(to left, $bg-primary 0%, transparent 100%);
      }
    }

    .carousel-state {
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

    .carousel-skeleton {
      display: flex;
      gap: $space-4;

      .skeleton-card {
        min-width: 180px;

        .skeleton-cover {
          aspect-ratio: 3/4;
          border-radius: $radius-md;
          background: linear-gradient(90deg, $bg-elevated 25%, $bg-hover 50%, $bg-elevated 75%);
          background-size: 200% 100%;
          animation: shimmer 1.5s infinite;
        }

        .skeleton-info {
          padding: $space-2 0;

          .skeleton-line {
            height: 12px;
            background: $bg-elevated;
            border-radius: $radius-sm;
            margin-bottom: 6px;

            &.short {
              width: 60%;
            }
          }
        }
      }
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
