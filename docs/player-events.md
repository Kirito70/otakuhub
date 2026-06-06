# OtakuHub — Player Event Contract (MegaPlay / Future Providers)

> **Status**: Draft — for review before any frontend playback integration.
> **Applies to**: Embed-based playback providers (MegaPlay, future).

---

## 1. Purpose

When a user plays an episode/chapter inside an OtakuHub page, the content loads in a **sandboxed `<iframe>`** pointing to the provider's embed URL. The provider's player communicates with the parent page via `postMessage` events. This document defines:

- Which events are expected from each provider.
- How the OtakuHub frontend **must validate** event origin before trusting the data.
- How listenable events map to OtakuHub tracking actions (progress, completion, errors).

---

## 2. Embed Flow

```
User taps "Play" on an episode
    │
    ▼
OtakuHub resolves embed_url from media_source_episodes.embed_url
    │
    ▼
Frontend renders <iframe> with src = embed_url
    │
    ▼
Provider player loads and sends postMessage events to parent window
    │
    ▼
OtakuHub event listener validates event.origin, then processes
```

**Rule**: No direct stream URLs (`m3u8`, `mp4`, `hls`, `dash`) are ever exposed to the frontend or stored in the DB. The `embed_url` stored in `media_source_episodes` is always an HTML page URL (MegaPlay embed page), never a raw media segment URL.

---

## 3. Origin Validation (Mandatory)

Every `postMessage` event **must** be validated against the provider's allowed origin before any data is used:

```typescript
// In a composable: composables/usePlayerListener.ts

const ALLOWED_PLAYER_ORIGINS = new Set([
  "https://megaplay.buzz",
  "https://www.megaplay.buzz",
])

function handlePlayerEvent(event: MessageEvent): void {
  // ── Reject unverified origins ──────────────────────────────────
  if (!ALLOWED_PLAYER_ORIGINS.has(event.origin)) {
    return  // silently ignore
  }

  // ── Parse payload ──────────────────────────────────────────────
  let data: unknown
  if (typeof event.data === "string") {
    try { data = JSON.parse(event.data) } catch { return }
  } else {
    data = event.data
  }

  // ── Route by event type ────────────────────────────────────────
  if (typeof data !== "object" || data === null) return
  const msg = data as Record<string, unknown>

  if (msg.channel === "megacloud") {
    // MegaPlay-specific channel
    console.debug("[player] megacloud event", msg)
  }

  if (msg.event === "time") {
    onProgress(msg as ProgressEvent)
  } else if (msg.event === "complete") {
    onComplete(msg as CompleteEvent)
  } else if (msg.event === "error") {
    onError(msg as ErrorEvent)
  } else if (msg.type === "watching-log") {
    onWatchingLog(msg as WatchingLogEvent)
  }
}
```

---

## 4. Event Types (MegaPlay)

MegaPlay emits the following `postMessage` events from its embed iframe:

### 4.1 `time` — Playback position update

```typescript
interface ProgressEvent {
  event: "time"
  time: number       // current playhead position in seconds
  duration: number   // total duration in seconds
  percent: number    // 0–100
}
```

**OtakuHub action**: When `percent >= 80`, mark episode as "almost complete" (optional pre-read/pre-watch signal). Debounce updates to at most once per 30 seconds to avoid excessive API calls.

### 4.2 `complete` — Episode finished

```typescript
interface CompleteEvent {
  event: "complete"
}
```

**OtakuHub action**: Call `PATCH /api/v1/lists/{entry_id}/progress` to advance progress by 1. If the episode is the last in the series, set status to `completed`. Fire notification to group if applicable.

### 4.3 `error` — Playback failure

```typescript
interface ErrorEvent {
  event: "error"
}
```

**OtakuHub action**: Surface inline error to user ("Playback error — try a different language or report this episode"). Log to monitoring. Do **not** automatically decrement progress or change list status.

### 4.4 `watching-log` — Heartbeat/watch time

```typescript
interface WatchingLogEvent {
  type: "watching-log"
  currentTime: number
  duration: number
}
```

**OtakuHub action**: Used for analytics and watch-time tracking (future). Currently no action; logged if analytics is enabled.

### 4.5 `megacloud` channel

MegaPlay also sends events on the `megacloud` channel with arbitrary payloads. The OtakuHub listener should **log these but not act** on them — they are internal MegaPlay events.

---

## 5. Provider-Specific Notes

| Provider | Base URL | Allowed Origin(s) | Notes |
|----------|----------|-------------------|-------|
| MegaPlay | `megaplay.buzz` | `https://megaplay.buzz`, `https://www.megaplay.buzz` | Primary provider. Uses legacy HiAnime player server ID system. |

### 5.1 Adding a new provider

1. Register provider name in `database-schema.md` and `media_source_mappings.source`.
2. Add allowed origins to the frontend `ALLOWED_PLAYER_ORIGINS` set.
3. Document the provider's `postMessage` events in this file.
4. Update the `safe_embed_url` validator in the backend if the new provider uses a different embed URL pattern.

---

## 6. Frontend Architecture Contract

### 6.1 Composable: `usePlayerListener`

```
composables/usePlayerListener.ts
```

- Exposes: `isPlaying`, `currentTime`, `duration`, `error`, `onComplete`, `onProgress`
- Accepts: `embedUrl: Ref<string>` (the iframe src)
- Handles: origin validation, event parsing, debounced progress callbacks
- Returns: `{ isPlaying, currentTime, duration, error, attach, detach }`

### 6.2 State contract (Pinia)

No permanent player state in Pinia. The composable manages transient playback state locally. Only completed episodes trigger Pinia `tracking` store actions (progress update, status change).

### 6.3 Error handling

- **Origin mismatch**: silent ignore (no console noise in production).
- **Invalid payload**: logged at `debug` level only.
- **Network/timeout**: if the embed page fails to load (iframe `onerror`), show `AppEmptyState(mode='error')` with retry.
- **Provider 410 Gone**: the availability probe (`MegaPlayAvailabilityClient`) should detect this. Frontend shows "This episode is no longer available" and disables the play button.

---

## 7. Security Rules

1. **Never** store raw stream URLs (`m3u8`, `mp4`, `hls`, `dash`) in the database.
2. **Never** pass stream URLs to the frontend — only embed page URLs.
3. **Always** validate `event.origin` before processing any `postMessage` data.
4. **Never** call `eval()` or `new Function()` on any `postMessage` payload.
5. **Never** send `postMessage` data to the backend API — only use it for local UI state transitions.
6. Progress/completion should only be sent to the API from explicit composable actions, not from raw event handlers without user confirmation (debounce + threshold).

---

## 8. Future Extensions

- **SyncParty / Rave integration**: If a future ADR adds synchronized watch parties, the player composable will need to send/receive sync events. The same `postMessage` listener should be extended with a `sync` event handler.
- **Chromecast / AirPlay**: Would bypass the iframe entirely — handled separately outside this contract.
- **Download tracking**: If OTTHub ever provides download links, those have a separate security contract (direct download URL expiry, IP-bound tokens).
