import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import VideoPlayer from '../VideoPlayer.vue'

// Mock the composable so lifecycle hooks don't interfere with tests
vi.mock('src/composables/usePlayerListener', () => ({
  usePlayerListener: () => ({
    lastEvent: ref(null),
    isPlayerReady: ref(false),
    isPlaying: ref(false),
    currentTime: ref(0),
    error: ref(null),
    sendCommand: vi.fn(),
    togglePlay: vi.fn(),
    seek: vi.fn(),
  }),
}))

describe('VideoPlayer', () => {
  it('renders empty state when no embedUrl', () => {
    const wrapper = mount(VideoPlayer, {
      props: { embedUrl: null, title: 'Test' },
    })
    expect(wrapper.text()).toContain(
      'Select an episode and server to start watching.',
    )
  })

  it('renders iframe when embedUrl provided', () => {
    const wrapper = mount(VideoPlayer, {
      props: { embedUrl: 'https://example.com/embed', title: 'Test' },
    })
    expect(wrapper.find('iframe').exists()).toBe(true)
    expect(wrapper.find('iframe').attributes('src')).toBe(
      'https://example.com/embed',
    )
  })

  it('renders loading state', () => {
    const wrapper = mount(VideoPlayer, {
      props: { embedUrl: null, title: 'Test', isLoading: true },
    })
    expect(wrapper.text()).toContain('Loading player')
    expect(wrapper.find('.spinner').exists()).toBe(true)
  })

  it('renders error state from prop', () => {
    const wrapper = mount(VideoPlayer, {
      props: {
        embedUrl: 'https://example.com',
        title: 'Test',
        error: 'Stream error',
      },
    })
    expect(wrapper.text()).toContain('Stream error')
  })

  it('emits retry on error retry click', async () => {
    const wrapper = mount(VideoPlayer, {
      props: {
        embedUrl: 'https://example.com',
        title: 'Test',
        error: 'Error',
      },
    })
    // Find the PlayerError component and emit retry from it
    const errorBtn = wrapper.find('.player-error-retry')
    await errorBtn.trigger('click')
    expect(wrapper.emitted('retry')).toBeTruthy()
  })

  it('renders PlayerControls when embedUrl provided and no error', () => {
    const wrapper = mount(VideoPlayer, {
      props: {
        embedUrl: 'https://example.com',
        title: 'Test',
        qualities: ['720p', '1080p'],
        quality: '720p',
      },
    })
    const controls = wrapper.findComponent({ name: 'PlayerControls' })
    expect(controls.exists()).toBe(true)
    expect(controls.props('title')).toBe('Test')
    expect(controls.props('qualities')).toEqual(['720p', '1080p'])
  })

  it('does not render PlayerControls when error is present', () => {
    const wrapper = mount(VideoPlayer, {
      props: {
        embedUrl: 'https://example.com',
        title: 'Test',
        error: 'Something broke',
      },
    })
    const controls = wrapper.findComponent({ name: 'PlayerControls' })
    expect(controls.exists()).toBe(false)
  })

  it('does not render PlayerControls when embedUrl is null', () => {
    const wrapper = mount(VideoPlayer, {
      props: { embedUrl: null, title: 'Test' },
    })
    const controls = wrapper.findComponent({ name: 'PlayerControls' })
    expect(controls.exists()).toBe(false)
  })

  it('shows loading over empty state when both are set', () => {
    const wrapper = mount(VideoPlayer, {
      props: {
        embedUrl: null,
        title: 'Test',
        isLoading: true,
        error: null,
      },
    })
    // Loading should take priority over empty state
    expect(wrapper.find('.player-loading').exists()).toBe(true)
    expect(wrapper.find('.player-empty').exists()).toBe(false)
  })

  it('emits play event from PlayerControls toggle-play', async () => {
    const wrapper = mount(VideoPlayer, {
      props: { embedUrl: 'https://example.com', title: 'Test' },
    })
    const controls = wrapper.findComponent({ name: 'PlayerControls' })
    await controls.vm.$emit('toggle-play')
    expect(wrapper.emitted('play')).toBeTruthy()
  })

  it('emits set-quality from PlayerControls', async () => {
    const wrapper = mount(VideoPlayer, {
      props: {
        embedUrl: 'https://example.com',
        title: 'Test',
        qualities: ['720p', '1080p'],
        quality: '720p',
      },
    })
    const controls = wrapper.findComponent({ name: 'PlayerControls' })
    await controls.vm.$emit('set-quality', '1080p')
    expect(wrapper.emitted('set-quality')).toBeTruthy()
    expect(wrapper.emitted('set-quality')![0]).toEqual(['1080p'])
  })

  it('has correct CSS class structure', () => {
    const wrapper = mount(VideoPlayer, {
      props: { embedUrl: null, title: 'Test' },
    })
    expect(wrapper.find('.video-player').exists()).toBe(true)
    expect(wrapper.find('.player-empty').exists()).toBe(true)
  })
})
