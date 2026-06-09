# ADR 081 — Frontend Player Architecture

**Status**: Proposed
**Date**: 2026-06-08

## Context

The player event contract (`docs/player-events.md`) defines the postMessage protocol for MegaPlay embeds, but no frontend code implements it. To enable episode playback, the frontend needs:

1. A composable that listens to provider postMessage events with origin validation
2. A sandboxed iframe player component
3. Integration with the Pinia tracking store for auto-advance progress
4. Episode-to-episode navigation (next episode, previous episode)
5. Language switching (sub ↔ dub) per episode
6. Error states and fallback when embeds fail

The player will be a **full-page or large-sheet overlay**, not an inline widget, matching the aniwave-style immersive playback experience.

## Decision

### 1. Composable: `usePlayerListener`

Location: `frontend/src/composables/usePlayerListener.ts`

Exposes reactive state for the currently-playing episode and handles all postMessage events:

```typescript
interface UsePlayerListenerReturn {
  // Reactive state
  isPlaying: Ref<boolean>
  currentTime: Ref<number>
  duration: Ref<number>
  percent: Ref<number>          // 0–100
  error: Ref<string | null>

  // Lifecycle
  attach: (iframeWindow: Window, allowedOrigins: string[]) => void
  detach: () => void

  // Callbacks (set by consumer)
  onProgress?: (percent: number) => void
  onComplete?: () => void        // auto-advance to next episode
  onError?: (error: string) => void
}
```

**Behavior contract:**
- Origin validation: only accepts messages from `ALLOWED_PLAYER_ORIGINS` (currently `https://megaplay.buzz`, `https://www.megaplay.buzz`)
- Debounce: progress events throttle to at most 1 per 30 seconds
- Completion: when `event === "complete"` fires `onComplete` callback
- Error: when `event === "error"` sets `error` ref, does NOT auto-retry
- Watching-log events: logged at debug, no action
- Cleanup: `detach()` removes the message event listener

### 2. Component: `VideoPlayer.vue`

Location: `frontend/src/components/player/VideoPlayer.vue`

A full-viewport overlay component that renders the MegaPlay iframe:

```vue
<template>
  <!-- Full-screen overlay on media detail page -->
  <div v-if="visible" class="player-overlay">
    <!-- Close/minimize button -->
    <button class="player-close" @click="close">
      <ChevronDownIcon />
    </button>

    <!-- Episode info bar -->
    <div class="player-info-bar">
      <span class="ep-title">Episode {{ episodeNumber }}</span>
      <span class="ep-lang-badge">{{ language === 'sub' ? 'SUB' : 'DUB' }}</span>
    </div>

    <!-- Sandboxed iframe -->
    <iframe
      v-if="embedUrl"
      :src="embedUrl"
      class="player-iframe"
      sandbox="allow-scripts allow-same-origin allow-forms"
      allow="autoplay; fullscreen"
      referrerpolicy="no-referrer"
      @load="onIframeLoad"
    />

    <!-- Error state -->
    <PlayerError v-else-if="error" :message="error" @retry="reload" />

    <!-- Loading / unavailable state -->
    <div v-else class="player-loading">
      <q-spinner size="48px" color="white" />
    </div>

    <!-- Next episode button (appears near end) -->
    <button v-if="showNextEp" class="btn-next-ep" @click="playNext">
      Next Episode →
    </button>
  </div>
</template>
```

**Props:**
- `embedUrl: string | null`
- `episodeNumber: number`
- `title: string | null`
- `language: 'sub' | 'dub'`
- `visible: boolean`

**Emits:**
- `close` — user dismissed player
- `next-episode` — episode completed or user clicked next
- `previous-episode` — user clicked previous
- `progress` — debounced progress percent

### 3. Component: `ServerSelector.vue`

Location: `frontend/src/components/anime/ServerSelector.vue`

Lets users switch between mirror servers and sub/dub:

```vue
<template>
  <div class="server-selector">
    <!-- Language toggle -->
    <div class="lang-toggle">
      <button :class="{ active: language === 'sub' }" @click="$emit('lang-change', 'sub')">SUB</button>
      <button :class="{ active: language === 'dub' }" @click="$emit('lang-change', 'dub')">DUB</button>
    </div>

    <!-- Server mirror list -->
    <div class="server-list">
      <button
        v-for="server in servers"
        :key="server.id"
        :class="{ active: selectedServer === server.id }"
        @click="$emit('server-change', server)"
      >
        {{ server.name }}
        <span v-if="!server.is_available" class="offline-tag">Offline</span>
      </button>
    </div>
  </div>
</template>
```

### 4. Pinia store integration

No dedicated player Pinia store. Transient playback state lives in the composable. Only **terminal events** touch Pinia:

- **On episode complete** (`onComplete`):
  - `trackingStore.updateProgress(mediaId, episodeNumber)` — advance progress to this episode number
  - If last episode → `trackingStore.updateStatus(mediaId, 'completed')`
  - If applicable → create activity feed entry

- **On manual episode navigation**:
  - `playerStore.currentMediaId` — single ref in a lightweight `player.ts` store
  - `playerStore.currentEpisode` — episode number
  - `playerStore.history: number[]` — recently watched episode numbers (for back navigation)

```typescript
// stores/player.ts — minimal, just for cross-component state
export const usePlayerStore = defineStore('player', () => {
  const currentMediaId = ref<string | null>(null)
  const currentEpisode = ref<number>(0)
  const history = ref<number[]>([])

  function setCurrent(mediaId: string, episode: number) {
    if (currentMediaId.value === mediaId) {
      history.value.push(currentEpisode.value)
    } else {
      history.value = [currentEpisode.value]
      currentMediaId.value = mediaId
    }
    currentEpisode.value = episode
  }

  return { currentMediaId, currentEpisode, history, setCurrent }
})
```

### 5. Layout: Player sheet vs full page

Two modes, selected by viewport:

| Breakpoint | Player display |
|-----------|---------------|
| **xs-sm** (< 1024px) | Full-screen overlay (portrait-optimized) |
| **md+** (≥ 1024px) | Large centered sheet with episode list side panel |

The side panel on desktop shows the episode list so users can navigate without leaving the player.

### 6. Error handling matrix

| Scenario | User sees | Action |
|----------|-----------|--------|
| iframe fails to load (timeout) | "Could not load player. Try a different server." | Retry button → switch to next available server |
| postMessage `error` event | "Playback error — try switching to SUB/DUB or a different server." | Language toggle or server selector visible |
| embed URL is `null`/unavailable | "No playback source available for this episode." | Disabled play button on episode list |
| Provider returns 410 Gone | "This episode is no longer available on this server." | Availability probe detected; episode marked unavailable |

### 7. Testing contract

- `usePlayerListener.test.ts`: origin validation (allowed/rejected), event parsing (time/complete/error/watching-log), debounce timing, cleanup on detach
- `VideoPlayer.test.ts`: rendering states (loading/playing/error), emit events, close button
- `ServerSelector.test.ts`: language toggle, server selection, offline badge rendering
- Player integration test: mock postMessage events → verify progress callback fires

## Consequences

**Good**:
- Clear separation: composable owns protocol, component owns UI, store owns cross-component state
- Origin validation prevents XSS from rogue iframe messages
- Debounced progress prevents excessive API calls
- No persistent player state to manage (tracking only updates on completion)

**Bad**:
- postMessage API is provider-specific — switching providers requires new event parsers
- iframe sandbox limits what the player can do (no localStorage in sandbox, etc.)
- Full-screen overlay on mobile may conflict with system UI

**Neutral**:
- Player consumes the Source Provider API (ADR 080) to resolve embed URLs
- Future providers (SyncParty, Rave, Chromecast) will need separate handlers
