<template>
  <div class="video-player" ref="containerRef">
    <!-- Loading overlay -->
    <div v-if="isLoading" class="player-loading">
      <div class="spinner"></div>
      <span>Loading player...</span>
    </div>

    <!-- Error state -->
    <PlayerError
      v-else-if="computedError"
      :message="computedError"
      @retry="$emit('retry')"
    />

    <!-- Empty state -->
    <div v-else-if="!embedUrl" class="player-empty">
      <p>Select an episode and server to start watching.</p>
    </div>

    <!-- Video iframe -->
    <iframe
      v-else
      ref="iframeRef"
      :src="embedUrl"
      class="player-iframe"
      allow="autoplay; fullscreen; encrypted-media"
      allowfullscreen
      frameborder="0"
    ></iframe>

    <!-- Controls overlay -->
    <PlayerControls
      v-if="embedUrl && !computedError"
      :is-playing="isPlaying"
      :current-time="currentTime"
      :duration="null"
      :title="title"
      :qualities="qualities"
      :quality="quality"
      @toggle-play="emit('play')"
      @set-quality="(q: string) => emit('set-quality', q)"
      @toggle-fullscreen="toggleFullscreen"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { usePlayerListener } from 'src/composables/usePlayerListener'
import PlayerError from './PlayerError.vue'
import PlayerControls from './PlayerControls.vue'

interface VideoPlayerProps {
  embedUrl: string | null
  title: string
  autoplay?: boolean
  qualities?: string[]
  quality?: string | null
  isLoading?: boolean
  error?: string | null
}

const props = withDefaults(defineProps<VideoPlayerProps>(), {
  autoplay: false,
  qualities: () => [],
  quality: null,
  isLoading: false,
  error: null,
})

const emit = defineEmits<{
  play: []
  pause: []
  ended: []
  timeupdate: [time: number]
  error: [message: string]
  retry: []
  'toggle-fullscreen': []
  'set-quality': [quality: string]
}>()

const containerRef = ref<HTMLDivElement | null>(null)
const iframeRef = ref<HTMLIFrameElement | null>(null)

const { isPlayerReady, isPlaying, currentTime, error: listenerError } = usePlayerListener({
  iframeRef,
})

const computedError = computed(() => props.error ?? listenerError.value)

function toggleFullscreen() {
  if (!containerRef.value) return
  if (document.fullscreenElement) {
    void document.exitFullscreen()
  } else {
    void containerRef.value.requestFullscreen()
  }
  emit('toggle-fullscreen')
}
</script>

<style lang="scss">
@use 'src/css/tokens' as *;

.video-player {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  background: black;
  border-radius: $radius-lg;
  overflow: hidden;

  .player-iframe {
    width: 100%;
    height: 100%;
    border: none;
  }

  .player-loading {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: $space-3;
    background: $bg-primary;
    color: $text-muted;

    .spinner {
      width: 40px;
      height: 40px;
      border: 3px solid $bg-hover;
      border-top-color: $accent-primary;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
  }

  .player-empty {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: $bg-secondary;
    color: $text-muted;

    p {
      margin: 0;
      font-size: $font-size-md;
    }
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
