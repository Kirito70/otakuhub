<template>
  <div class="server-selector">
    <h4 class="server-label">Select Server</h4>

    <div v-if="loading" class="server-skeleton">
      <div v-for="n in 3" :key="n" class="server-pill skeleton"></div>
    </div>

    <div v-else-if="error" class="server-error">{{ error }}</div>

    <div v-else-if="servers.length === 0" class="server-empty">
      No servers available for this episode.
    </div>

    <div v-else class="server-grid">
      <button
        v-for="server in servers"
        :key="server.id"
        class="server-pill"
        :class="{
          active: server.id === selectedServerId,
          unavailable: !server.isAvailable,
        }"
        :disabled="!server.isAvailable"
        @click="$emit('select', server.id)"
      >
        <span class="server-source">{{ server.source }}</span>
        <span class="server-lang" :class="server.language">
          {{ server.language === 'sub' ? 'SUB' : 'DUB' }}
        </span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ServerOption } from 'src/types/media'

interface ServerSelectorProps {
  servers: ServerOption[]
  selectedServerId: string | null
  loading: boolean
  error: string | null
}

defineProps<ServerSelectorProps>()

defineEmits<{
  select: [serverId: string]
}>()
</script>

<style lang="scss">
@use 'src/css/tokens' as *;

.server-selector {
  .server-label {
    font-size: $font-size-sm;
    font-weight: 600;
    color: $text-secondary;
    margin: 0 0 $space-3;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .server-grid {
    display: flex;
    flex-wrap: wrap;
    gap: $space-2;
  }

  .server-pill {
    display: flex;
    align-items: center;
    gap: $space-2;
    padding: $space-2 $space-3;
    border-radius: $radius-md;
    border: $border-subtle;
    background: $bg-secondary;
    color: $text-primary;
    cursor: pointer;
    transition: all $transition;
    font-size: $font-size-sm;

    &:hover:not(:disabled) {
      border-color: $accent-primary;
    }

    &.active {
      border-color: $accent-primary;
      background: rgba($accent-primary, 0.15);
      box-shadow: 0 0 8px rgba($accent-primary, 0.3);
    }

    &.unavailable {
      opacity: 0.4;
      cursor: not-allowed;
    }

    &.skeleton {
      min-width: 80px;
      height: 32px;
      background: linear-gradient(90deg, $bg-elevated 25%, $bg-hover 50%, $bg-elevated 75%);
      background-size: 200% 100%;
      animation: shimmer 1.5s infinite;
      border: none;
      pointer-events: none;
    }

    .server-source {
      font-weight: 600;
    }

    .server-lang {
      font-size: $font-size-xs;
      font-weight: 700;
      padding: 1px 6px;
      border-radius: $radius-sm;

      &.sub {
        background: rgba($accent-primary, 0.2);
        color: $accent-primary;
      }

      &.dub {
        background: rgba($accent-warm, 0.2);
        color: $accent-warm;
      }
    }
  }

  .server-error {
    color: $accent-error;
    font-size: $font-size-sm;
  }

  .server-empty {
    color: $text-muted;
    font-size: $font-size-sm;
  }
}
</style>
