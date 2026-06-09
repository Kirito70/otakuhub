import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { defineComponent, ref } from 'vue'
import { mount } from '@vue/test-utils'
import { usePlayerListener } from '../usePlayerListener'

/**
 * Helper: mounts a minimal wrapper component so that onMounted/onBeforeUnmount
 * lifecycle hooks run.
 */
function mountComposable<T extends Record<string, unknown>>(setup: () => T) {
  const result = {} as T
  const wrapper = mount(
    defineComponent({
      setup() {
        Object.assign(result, setup())
        return () => null
      },
      template: '<div />',
    }),
  )
  return { wrapper, result }
}

describe('usePlayerListener', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('exports all expected symbols', () => {
    expect(usePlayerListener).toBeDefined()
    expect(typeof usePlayerListener).toBe('function')
  })

  it('adds message event listener on mount', () => {
    const addSpy = vi.spyOn(window, 'addEventListener')
    const { wrapper } = mountComposable(() => usePlayerListener())
    expect(addSpy).toHaveBeenCalledWith('message', expect.any(Function))
    wrapper.unmount()
  })

  it('removes message event listener on unmount', () => {
    const removeSpy = vi.spyOn(window, 'removeEventListener')
    const { wrapper } = mountComposable(() => usePlayerListener())
    wrapper.unmount()
    expect(removeSpy).toHaveBeenCalledWith('message', expect.any(Function))
  })

  it('handles ready event correctly', () => {
    const { result } = mountComposable(() => usePlayerListener())
    window.dispatchEvent(
      new MessageEvent('message', {
        data: { type: 'ready' },
        origin: '*',
      }),
    )
    expect(result.isPlayerReady?.value).toBe(true)
    expect(result.lastEvent?.value?.type).toBe('ready')
  })

  it('handles play event', () => {
    const { result } = mountComposable(() => usePlayerListener())
    window.dispatchEvent(
      new MessageEvent('message', {
        data: { type: 'play' },
        origin: '*',
      }),
    )
    expect(result.isPlaying?.value).toBe(true)
  })

  it('handles pause event', () => {
    const { result } = mountComposable(() => usePlayerListener())
    window.dispatchEvent(
      new MessageEvent('message', {
        data: { type: 'pause' },
        origin: '*',
      }),
    )
    expect(result.isPlaying?.value).toBe(false)
  })

  it('handles ended event after play', () => {
    const { result } = mountComposable(() => usePlayerListener())
    // Start playing first
    window.dispatchEvent(
      new MessageEvent('message', {
        data: { type: 'play' },
        origin: '*',
      }),
    )
    expect(result.isPlaying?.value).toBe(true)

    // Then end
    window.dispatchEvent(
      new MessageEvent('message', {
        data: { type: 'ended' },
        origin: '*',
      }),
    )
    expect(result.isPlaying?.value).toBe(false)
  })

  it('handles timeupdate event', () => {
    const { result } = mountComposable(() => usePlayerListener())
    window.dispatchEvent(
      new MessageEvent('message', {
        data: { type: 'timeupdate', data: { currentTime: 42.5 } },
        origin: '*',
      }),
    )
    expect(result.currentTime?.value).toBe(42.5)
  })

  it('handles error event', () => {
    const { result } = mountComposable(() => usePlayerListener())
    window.dispatchEvent(
      new MessageEvent('message', {
        data: { type: 'error', data: 'Stream unavailable' },
        origin: '*',
      }),
    )
    expect(result.error?.value).toBe('Stream unavailable')
  })

  it('handles error event with non-string data', () => {
    const { result } = mountComposable(() => usePlayerListener())
    window.dispatchEvent(
      new MessageEvent('message', {
        data: { type: 'error', data: { code: 500 } },
        origin: '*',
      }),
    )
    expect(result.error?.value).toBe('Player error')
  })

  it('validates origin when allowedOrigin is set', () => {
    const { result } = mountComposable(() =>
      usePlayerListener({ allowedOrigin: 'https://example.com' }),
    )

    // Message from different origin should be ignored
    window.dispatchEvent(
      new MessageEvent('message', {
        data: { type: 'ready' },
        origin: 'https://evil.com',
      }),
    )
    expect(result.isPlayerReady?.value).toBe(false)

    // Message from allowed origin should be processed
    window.dispatchEvent(
      new MessageEvent('message', {
        data: { type: 'ready' },
        origin: 'https://example.com',
      }),
    )
    expect(result.isPlayerReady?.value).toBe(true)
  })

  it('ignores messages with invalid data', () => {
    const { result } = mountComposable(() => usePlayerListener())

    // Null data
    window.dispatchEvent(
      new MessageEvent('message', {
        data: null,
        origin: '*',
      }),
    )
    expect(result.lastEvent?.value).toBeNull()

    // Missing type
    window.dispatchEvent(
      new MessageEvent('message', {
        data: { foo: 'bar' },
        origin: '*',
      }),
    )
    expect(result.lastEvent?.value).toBeNull()
  })

  it('calls onEvent callback when provided', () => {
    const callback = vi.fn()
    const { result } = mountComposable(() => usePlayerListener({ onEvent: callback }))

    window.dispatchEvent(
      new MessageEvent('message', {
        data: { type: 'play' },
        origin: '*',
      }),
    )

    expect(callback).toHaveBeenCalledTimes(1)
    expect(callback).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'play' }),
    )
  })

  it('sendCommand does nothing when iframeRef is null', () => {
    const { result } = mountComposable(() => usePlayerListener())
    // Should not throw
    result.sendCommand?.('play')
  })

  it('sendCommand posts message to iframe', () => {
    const postSpy = vi.fn()
    const iframeRef = ref<HTMLIFrameElement | null>({
      contentWindow: { postMessage: postSpy },
    } as unknown as HTMLIFrameElement)

    const { result } = mountComposable(() => usePlayerListener({ iframeRef }))
    result.sendCommand?.('play')

    expect(postSpy).toHaveBeenCalledWith(
      { command: 'play', payload: undefined },
      '*',
    )
  })

  it('sendCommand posts message with custom origin', () => {
    const postSpy = vi.fn()
    const iframeRef = ref<HTMLIFrameElement | null>({
      contentWindow: { postMessage: postSpy },
    } as unknown as HTMLIFrameElement)

    const { result } = mountComposable(() =>
      usePlayerListener({ iframeRef, allowedOrigin: 'https://player.example.com' }),
    )
    result.sendCommand?.('seek', { time: 30 })

    expect(postSpy).toHaveBeenCalledWith(
      { command: 'seek', payload: { time: 30 } },
      'https://player.example.com',
    )
  })

  it('togglePlay sends pause when already playing', () => {
    const postSpy = vi.fn()
    const iframeRef = ref<HTMLIFrameElement | null>({
      contentWindow: { postMessage: postSpy },
    } as unknown as HTMLIFrameElement)

    const { result } = mountComposable(() => usePlayerListener({ iframeRef }))

    // Set playing state
    window.dispatchEvent(
      new MessageEvent('message', {
        data: { type: 'play' },
        origin: '*',
      }),
    )

    result.togglePlay?.()
    expect(postSpy).toHaveBeenCalledWith(
      { command: 'pause', payload: undefined },
      '*',
    )
  })

  it('togglePlay sends play when not playing', () => {
    const postSpy = vi.fn()
    const iframeRef = ref<HTMLIFrameElement | null>({
      contentWindow: { postMessage: postSpy },
    } as unknown as HTMLIFrameElement)

    const { result } = mountComposable(() => usePlayerListener({ iframeRef }))

    result.togglePlay?.()
    expect(postSpy).toHaveBeenCalledWith(
      { command: 'play', payload: undefined },
      '*',
    )
  })

  it('seek sends seek command with time', () => {
    const postSpy = vi.fn()
    const iframeRef = ref<HTMLIFrameElement | null>({
      contentWindow: { postMessage: postSpy },
    } as unknown as HTMLIFrameElement)

    const { result } = mountComposable(() => usePlayerListener({ iframeRef }))

    result.seek?.(90)
    expect(postSpy).toHaveBeenCalledWith(
      { command: 'seek', payload: { time: 90 } },
      '*',
    )
  })
})
