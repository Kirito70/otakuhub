<template>
  <div class="related-carousel">
    <h3 class="related-title">Related Media</h3>

    <!-- Loading state -->
    <div v-if="isLoading" class="carousel-skeleton">
      <div v-for="n in 5" :key="n" class="skeleton-card">
        <div class="skeleton-cover"></div>
        <div class="skeleton-label"></div>
      </div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="carousel-state">
      <p>{{ error }}</p>
      <button @click="$emit('retry')">Retry</button>
    </div>

    <!-- Empty state -->
    <div v-else-if="items.length === 0" class="carousel-state">
      <p>No related media.</p>
    </div>

    <!-- Carousel track -->
    <div v-else class="carousel-track" ref="trackRef">
      <div
        v-for="item in items"
        :key="item.id"
        class="carousel-card"
        @click="$emit('navigate', item.id)"
      >
        <div class="card-cover">
          <img
            v-if="item.coverImage"
            :src="item.coverImage"
            :alt="item.title"
            @error="(e: Event) => { (e.target as HTMLImageElement).style.display = 'none' }"
          />
          <div v-else class="cover-placeholder">No Cover</div>
          <span class="relation-badge">{{ relationLabel(item.relationType) }}</span>
        </div>
        <p class="card-title">{{ item.title }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface RelatedMediaItem {
  id: string
  title: string
  coverImage: string | null
  relationType: string
}

interface RelatedMediaCarouselProps {
  items: RelatedMediaItem[]
  isLoading: boolean
  error: string | null
}

defineProps<RelatedMediaCarouselProps>()

defineEmits<{
  retry: []
  navigate: [id: string]
}>()

function relationLabel(type: string): string {
  const labels: Record<string, string> = {
    sequel: 'Sequel',
    prequel: 'Prequel',
    side_story: 'Side Story',
    parent: 'Parent',
    summary: 'Summary',
    alternative: 'Alternative',
    spin_off: 'Spin-off',
    adaptation: 'Adaptation',
    character: 'Character',
    other: 'Other',
  }
  return labels[type] ?? type
}
</script>

<style lang="scss">
@use 'src/css/tokens' as *;

.related-carousel {
  .related-title {
    font-size: $font-size-lg;
    font-weight: 700;
    color: $text-primary;
    margin: 0 0 $space-4;
  }

  .carousel-track {
    display: flex;
    gap: $space-4;
    overflow-x: auto;
    padding-bottom: $space-2;
    scrollbar-width: thin;
    scrollbar-color: $bg-hover transparent;

    &::-webkit-scrollbar {
      height: 6px;
    }
    &::-webkit-scrollbar-thumb {
      background: $bg-hover;
      border-radius: 3px;
    }
  }

  .carousel-card {
    flex-shrink: 0;
    width: 150px;
    cursor: pointer;
    transition: transform 0.2s ease;

    &:hover {
      transform: translateY(-4px);
    }

    .card-cover {
      position: relative;
      width: 150px;
      height: 225px;
      border-radius: $radius-md;
      overflow: hidden;
      background: $bg-elevated;
      margin-bottom: $space-2;

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .cover-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: $text-muted;
        font-size: $font-size-xs;
      }

      .relation-badge {
        position: absolute;
        top: $space-2;
        left: $space-2;
        padding: 2px 8px;
        border-radius: $radius-sm;
        font-size: $font-size-xs;
        font-weight: 700;
        background: rgba(0, 0, 0, 0.7);
        color: $accent-primary;
        border: 1px solid $accent-primary;
      }
    }

    .card-title {
      font-size: $font-size-xs;
      color: $text-secondary;
      margin: 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

  .carousel-state {
    text-align: center;
    padding: $space-8;
    color: $text-muted;

    p {
      margin: 0 0 $space-3;
    }

    button {
      padding: $space-2 $space-4;
      background: $accent-primary;
      color: white;
      border: none;
      border-radius: $radius-md;
      cursor: pointer;
      font-size: $font-size-sm;
    }
  }

  .carousel-skeleton {
    display: flex;
    gap: $space-4;

    .skeleton-card {
      flex-shrink: 0;
      width: 150px;

      .skeleton-cover {
        width: 150px;
        height: 225px;
        border-radius: $radius-md;
        background: linear-gradient(90deg, $bg-elevated 25%, $bg-hover 50%, $bg-elevated 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
      }

      .skeleton-label {
        height: 12px;
        margin-top: $space-2;
        border-radius: $radius-sm;
        background: $bg-elevated;
      }
    }
  }
}
</style>
