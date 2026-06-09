import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PlayerError from '../PlayerError.vue'

describe('PlayerError', () => {
  it('renders error message', () => {
    const wrapper = mount(PlayerError, {
      props: { message: 'Failed to load stream' },
    })
    expect(wrapper.text()).toContain('Failed to load stream')
  })

  it('renders title', () => {
    const wrapper = mount(PlayerError, {
      props: { message: 'Error' },
    })
    expect(wrapper.text()).toContain('Playback Error')
  })

  it('renders retry button with default label', () => {
    const wrapper = mount(PlayerError, {
      props: { message: 'Error' },
    })
    expect(wrapper.text()).toContain('Try Again')
  })

  it('renders retry button with custom label', () => {
    const wrapper = mount(PlayerError, {
      props: { message: 'Error', retryLabel: 'Reload' },
    })
    expect(wrapper.text()).toContain('Reload')
  })

  it('emits retry on button click', async () => {
    const wrapper = mount(PlayerError, {
      props: { message: 'Error' },
    })
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('retry')).toBeTruthy()
  })

  it('applies correct CSS classes', () => {
    const wrapper = mount(PlayerError, {
      props: { message: 'Test error' },
    })
    expect(wrapper.find('.player-error').exists()).toBe(true)
    expect(wrapper.find('.player-error-title').exists()).toBe(true)
    expect(wrapper.find('.player-error-message').exists()).toBe(true)
    expect(wrapper.find('.player-error-retry').exists()).toBe(true)
  })
})
