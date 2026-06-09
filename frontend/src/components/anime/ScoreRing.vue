<template>
  <div class="score-ring" :style="ringStyle">
    <svg :width="size" :height="size" viewBox="0 0 36 36">
      <circle class="score-bg" cx="18" cy="18" r="15.9" fill="none" stroke-width="2.8" />
      <circle
        class="score-fill"
        cx="18"
        cy="18"
        r="15.9"
        fill="none"
        stroke-width="2.8"
        :stroke="color"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="dashOffset"
        stroke-linecap="round"
        transform="rotate(-90, 18, 18)"
      />
    </svg>
    <span v-if="showLabel" class="score-label" :style="{ color }">{{ score.toFixed(1) }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface ScoreRingProps {
  score: number
  size?: number
  showLabel?: boolean
}

const props = withDefaults(defineProps<ScoreRingProps>(), {
  size: 64,
  showLabel: true,
})

const circumference = 2 * Math.PI * 15.9

const dashOffset = computed(() => {
  return circumference - (props.score / 10) * circumference
})

const color = computed(() => {
  if (props.score >= 8) return '#22c55e'
  if (props.score >= 6.5) return '#f59e0b'
  if (props.score >= 4) return '#eab308'
  return '#ef4444'
})

const ringStyle = computed(() => ({
  width: props.size + 'px',
  height: props.size + 'px',
}))
</script>

<style lang="scss">
@use 'src/css/tokens' as *;

.score-ring {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;

  svg {
    .score-bg {
      stroke: rgba(255, 255, 255, 0.1);
    }
    .score-fill {
      transition: stroke-dashoffset 0.6s ease, stroke 0.3s ease;
    }
  }

  .score-label {
    position: absolute;
    font-size: v-bind('size < 48 ? "0.65rem" : "0.85rem"');
    font-weight: 800;
  }
}
</style>
