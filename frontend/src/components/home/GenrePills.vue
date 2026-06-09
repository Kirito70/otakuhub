<template>
  <section class="genre-pills-section">
    <div v-if="loading" class="genre-pills-skeleton">
      <span v-for="n in 6" :key="n" class="pill skeleton"></span>
    </div>
    <div v-else-if="error" class="genre-pills-error">{{ error }}</div>
    <div v-else-if="items.length === 0" class="genre-pills-error">No genres available.</div>
    <div v-else class="genre-pills-grid">
      <button
        v-for="genre in items"
        :key="genre.id"
        class="pill"
        @click="$emit('select', genre.slug)"
      >
        {{ genre.name }}
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { GenreItem } from 'src/types/home'

defineProps<{
  items: GenreItem[]
  loading: boolean
  error: string | null
}>()

defineEmits<{
  select: [slug: string]
}>()
</script>

<style scoped lang="scss">
@use 'src/css/tokens' as *;

.genre-pills-section {
  .genre-pills-grid {
    display: flex;
    flex-wrap: wrap;
    gap: $space-2;
  }

  .genre-pills-skeleton {
    display: flex;
    flex-wrap: wrap;
    gap: $space-2;
  }

  .genre-pills-error {
    color: $text-muted;
    font-size: $font-size-sm;
    padding: $space-4 0;
    text-align: center;
  }

  .pill {
    padding: $space-2 $space-4;
    border-radius: 999px;
    border: 1px solid $border-default;
    background: $bg-secondary;
    color: $text-primary;
    font-size: $font-size-sm;
    font-weight: 500;
    cursor: pointer;
    transition: all $transition;

    &:hover {
      border-color: $accent-primary;
      color: $accent-primary;
      background: rgba($accent-primary, 0.1);
    }

    &.skeleton {
      min-width: 70px;
      height: 34px;
      border: none;
      background: linear-gradient(90deg, $bg-elevated 25%, $bg-hover 50%, $bg-elevated 75%);
      background-size: 200% 100%;
      animation: shimmer 1.5s infinite;
      pointer-events: none;
    }
  }
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
