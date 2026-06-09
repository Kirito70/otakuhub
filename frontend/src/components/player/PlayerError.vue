<template>
  <div class="player-error">
    <div class="player-error-icon">&#9888;</div>
    <h3 class="player-error-title">Playback Error</h3>
    <p class="player-error-message">{{ message }}</p>
    <button class="player-error-retry" @click="$emit('retry')">
      {{ retryLabel }}
    </button>
  </div>
</template>

<script setup lang="ts">
interface PlayerErrorProps {
  message: string
  retryLabel?: string
}

withDefaults(defineProps<PlayerErrorProps>(), {
  retryLabel: 'Try Again',
})

defineEmits<{
  retry: []
}>()
</script>

<style lang="scss">
@use 'src/css/tokens' as *;

.player-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: $space-3;
  padding: $space-10;
  background: $bg-secondary;
  border-radius: $radius-lg;
  min-height: 300px;

  .player-error-icon {
    font-size: 3rem;
    color: $accent-danger;
  }

  .player-error-title {
    font-size: $font-size-lg;
    font-weight: 700;
    color: $text-primary;
    margin: 0;
  }

  .player-error-message {
    font-size: $font-size-sm;
    color: $text-muted;
    text-align: center;
    max-width: 400px;
    margin: 0;
  }

  .player-error-retry {
    margin-top: $space-2;
    padding: $space-2 $space-5;
    background: $accent-primary;
    color: white;
    border: none;
    border-radius: $radius-md;
    font-size: $font-size-sm;
    font-weight: 600;
    cursor: pointer;
    transition: background $transition;

    &:hover {
      background: lighten($accent-primary, 10%);
    }
  }
}
</style>
