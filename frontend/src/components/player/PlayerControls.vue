<template>
  <div class="player-controls" @click.stop>
    <div class="controls-top">
      <span class="controls-title">{{ title }}</span>
    </div>

    <div class="controls-bottom">
      <div class="progress-bar" ref="progressBarRef" @click="onProgressClick">
        <div class="progress-track">
          <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
          <div class="progress-thumb" :style="{ left: progressPercent + '%' }"></div>
        </div>
      </div>

      <div class="controls-row">
        <div class="controls-left">
          <button class="control-btn" @click="$emit('toggle-play')" :aria-label="isPlaying ? 'Pause' : 'Play'">
            {{ isPlaying ? '\u23F8' : '\u25B6' }}
          </button>
          <span class="time-display">{{ formatTime(currentTime) }} / {{ formatTime(duration || 0) }}</span>
        </div>

        <div class="controls-right">
          <div v-if="qualities.length > 0" class="quality-selector">
            <button
              v-for="q in qualities"
              :key="q"
              class="quality-btn"
              :class="{ active: q === quality }"
              @click="$emit('set-quality', q)"
            >
              {{ q }}
            </button>
          </div>
          <button class="control-btn" @click="$emit('toggle-fullscreen')" :aria-label="isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'">
            {{ '\u26F6' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface PlayerControlsProps {
  isPlaying: boolean
  currentTime: number
  duration: number | null
  isFullscreen?: boolean
  quality?: string | null
  qualities?: string[]
  title?: string
}

const props = withDefaults(defineProps<PlayerControlsProps>(), {
  isFullscreen: false,
  quality: null,
  qualities: () => [],
  title: '',
})

const emit = defineEmits<{
  'toggle-play': []
  seek: [time: number]
  'toggle-fullscreen': []
  'set-quality': [quality: string]
}>()

const progressBarRef = ref<HTMLDivElement | null>(null)

const progressPercent = computed(() => {
  if (!props.duration) return 0
  return Math.min(100, (props.currentTime / props.duration) * 100)
})

function formatTime(seconds: number): string {
  if (!isFinite(seconds) || seconds < 0) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
}

function onProgressClick(event: MouseEvent) {
  const target = event.currentTarget as HTMLElement | null
  if (!target) return
  const rect = target.getBoundingClientRect()
  const x = event.clientX - rect.left
  const fraction = x / rect.width
  const time = fraction * (props.duration || 0)
  emit('seek', time)
}
</script>

<style lang="scss">
@use 'src/css/tokens' as *;

.player-controls {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: $space-4;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.85) 0%, transparent 40%, transparent 60%, rgba(0, 0, 0, 0.4) 100%);
  opacity: 0;
  transition: opacity $transition;

  &:hover {
    opacity: 1;
  }

  .controls-top {
    .controls-title {
      font-size: $font-size-sm;
      font-weight: 600;
      color: white;
      text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8);
    }
  }

  .controls-bottom {
    display: flex;
    flex-direction: column;
    gap: $space-2;

    .progress-bar {
      width: 100%;
      height: 4px;
      cursor: pointer;
      position: relative;

      &:hover {
        height: 6px;
      }

      .progress-track {
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 2px;
        position: relative;

        .progress-fill {
          height: 100%;
          background: $accent-primary;
          border-radius: 2px;
          transition: width 0.1s linear;
        }

        .progress-thumb {
          position: absolute;
          top: 50%;
          transform: translate(-50%, -50%);
          width: 12px;
          height: 12px;
          border-radius: 50%;
          background: $accent-primary;
          opacity: 0;
          transition: opacity $transition;
        }
      }

      &:hover .progress-thumb {
        opacity: 1;
      }
    }

    .controls-row {
      display: flex;
      align-items: center;
      justify-content: space-between;

      .controls-left,
      .controls-right {
        display: flex;
        align-items: center;
        gap: $space-2;
      }

      .control-btn {
        background: none;
        border: none;
        color: white;
        font-size: 1.2rem;
        cursor: pointer;
        padding: 4px 8px;
        border-radius: $radius-sm;
        transition: background $transition;

        &:hover {
          background: rgba(255, 255, 255, 0.15);
        }
      }

      .time-display {
        font-size: $font-size-sm;
        color: white;
        font-weight: 500;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
      }

      .quality-selector {
        display: flex;
        gap: 2px;

        .quality-btn {
          padding: 2px 6px;
          font-size: $font-size-xs;
          font-weight: 600;
          background: rgba(255, 255, 255, 0.15);
          color: white;
          border: none;
          border-radius: 2px;
          cursor: pointer;

          &.active {
            background: $accent-primary;
          }

          &:hover:not(.active) {
            background: rgba(255, 255, 255, 0.25);
          }
        }
      }
    }
  }
}
</style>
