import { ref, onMounted, onBeforeUnmount, type Ref } from 'vue'

export type PlayerEventType = 'ready' | 'play' | 'pause' | 'ended' | 'timeupdate' | 'error' | 'fullscreen' | 'qualitychange'

export interface PlayerEvent {
  type: PlayerEventType
  data?: unknown
  timestamp: number
}

export interface UsePlayerListenerOptions {
  /** Origin to validate messages from (default: '*') */
  allowedOrigin?: string
  /** Iframe ref to send messages to */
  iframeRef?: Ref<HTMLIFrameElement | null>
  /** Callback for all events */
  onEvent?: (event: PlayerEvent) => void
}

export function usePlayerListener(options: UsePlayerListenerOptions = {}) {
  const { allowedOrigin = '*', iframeRef, onEvent } = options
  const lastEvent = ref<PlayerEvent | null>(null)
  const isPlayerReady = ref(false)
  const isPlaying = ref(false)
  const currentTime = ref(0)
  const error = ref<string | null>(null)

  function handleMessage(event: MessageEvent) {
    // Validate origin if specified
    if (allowedOrigin !== '*' && event.origin !== allowedOrigin) return

    const data = event.data as Record<string, unknown> | undefined
    if (!data || typeof data !== 'object') return
    if (!data.type) return

    const playerEvent: PlayerEvent = {
      type: data.type as PlayerEventType,
      data: data.data,
      timestamp: Date.now(),
    }

    lastEvent.value = playerEvent
    onEvent?.(playerEvent)

    // Update reactive state based on event type
    switch (playerEvent.type) {
      case 'ready':
        isPlayerReady.value = true
        error.value = null
        break
      case 'play':
        isPlaying.value = true
        error.value = null
        break
      case 'pause':
        isPlaying.value = false
        break
      case 'ended':
        isPlaying.value = false
        break
      case 'timeupdate':
        if (typeof (data.data as Record<string, unknown> | undefined)?.currentTime === 'number') {
          currentTime.value = (data.data as Record<string, unknown>).currentTime as number
        }
        break
      case 'error':
        error.value = typeof data.data === 'string' ? data.data : 'Player error'
        break
    }
  }

  /** Send a command to the iframe player */
  function sendCommand(command: string, payload?: unknown) {
    if (!iframeRef?.value?.contentWindow) return
    iframeRef.value.contentWindow.postMessage({ command, payload }, allowedOrigin)
  }

  /** Play/pause toggle */
  function togglePlay() {
    sendCommand(isPlaying.value ? 'pause' : 'play')
  }

  /** Seek to a specific time */
  function seek(time: number) {
    sendCommand('seek', { time })
  }

  onMounted(() => {
    window.addEventListener('message', handleMessage)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('message', handleMessage)
  })

  return {
    lastEvent,
    isPlayerReady,
    isPlaying,
    currentTime,
    error,
    sendCommand,
    togglePlay,
    seek,
  }
}
