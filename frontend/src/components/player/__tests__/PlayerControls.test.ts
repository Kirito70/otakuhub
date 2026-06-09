import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import PlayerControls from '../PlayerControls.vue'

describe('PlayerControls', () => {
  const defaultProps = {
    isPlaying: false,
    currentTime: 60,
    duration: 1200,
    title: 'Test Episode',
  }

  it('renders title', () => {
    const wrapper = mount(PlayerControls, { props: defaultProps })
    expect(wrapper.text()).toContain('Test Episode')
  })

  it('shows play icon when not playing', () => {
    const wrapper = mount(PlayerControls, { props: defaultProps })
    expect(wrapper.text()).toContain('\u25B6')
  })

  it('shows pause icon when playing', () => {
    const wrapper = mount(PlayerControls, {
      props: { ...defaultProps, isPlaying: true },
    })
    expect(wrapper.text()).toContain('\u23F8')
  })

  it('emits toggle-play on play button click', async () => {
    const wrapper = mount(PlayerControls, { props: defaultProps })
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('toggle-play')).toBeTruthy()
  })

  it('displays formatted time', () => {
    const wrapper = mount(PlayerControls, { props: defaultProps })
    expect(wrapper.text()).toContain('01:00')
    expect(wrapper.text()).toContain('20:00')
  })

  it('formats zero time correctly', () => {
    const wrapper = mount(PlayerControls, {
      props: { ...defaultProps, currentTime: 0, duration: 0 },
    })
    expect(wrapper.text()).toContain('00:00')
  })

  it('renders quality buttons when qualities provided', () => {
    const wrapper = mount(PlayerControls, {
      props: {
        ...defaultProps,
        qualities: ['360p', '720p', '1080p'],
        quality: '720p',
      },
    })
    expect(wrapper.text()).toContain('360p')
    expect(wrapper.text()).toContain('720p')
    expect(wrapper.text()).toContain('1080p')
  })

  it('emits set-quality on quality button click', async () => {
    const wrapper = mount(PlayerControls, {
      props: {
        ...defaultProps,
        qualities: ['360p', '720p'],
        quality: '360p',
      },
    })
    const btns = wrapper.findAll('.quality-btn')
    await btns[1].trigger('click')
    expect(wrapper.emitted('set-quality')).toBeTruthy()
    expect(wrapper.emitted('set-quality')![0]).toEqual(['720p'])
  })

  it('marks active quality', () => {
    const wrapper = mount(PlayerControls, {
      props: {
        ...defaultProps,
        qualities: ['360p', '720p', '1080p'],
        quality: '720p',
      },
    })
    const btns = wrapper.findAll('.quality-btn')
    expect(btns[1].classes()).toContain('active')
    expect(btns[0].classes()).not.toContain('active')
    expect(btns[2].classes()).not.toContain('active')
  })

  it('emits toggle-fullscreen', async () => {
    const wrapper = mount(PlayerControls, { props: defaultProps })
    const buttons = wrapper.findAll('button')
    // The fullscreen button is the last one
    const fullscreenBtn = buttons[buttons.length - 1]
    await fullscreenBtn.trigger('click')
    expect(wrapper.emitted('toggle-fullscreen')).toBeTruthy()
  })

  it('calculates progress percentage', () => {
    const wrapper = mount(PlayerControls, {
      props: { ...defaultProps, currentTime: 300, duration: 600 },
    })
    const fill = wrapper.find('.progress-fill')
    expect(fill.attributes('style')).toContain('50%')
  })

  it('progress is 0 when no duration', () => {
    const wrapper = mount(PlayerControls, {
      props: { ...defaultProps, duration: null, currentTime: 100 },
    })
    const fill = wrapper.find('.progress-fill')
    expect(fill.attributes('style')).toContain('0%')
  })

  it('does not exceed 100% progress', () => {
    const wrapper = mount(PlayerControls, {
      props: { ...defaultProps, currentTime: 500, duration: 300 },
    })
    const fill = wrapper.find('.progress-fill')
    // currentTime exceeds duration, should cap at 100%
    expect(fill.attributes('style')).toContain('100%')
  })

  it('emits seek on progress bar click', async () => {
    const wrapper = mount(PlayerControls, { props: defaultProps })
    const progressBar = wrapper.find('.progress-bar')
    // Mock getBoundingClientRect for the event target
    const rect = { left: 0, width: 400 } as DOMRect
    vi.spyOn(progressBar.element, 'getBoundingClientRect').mockReturnValue(rect)

    await progressBar.trigger('click', { clientX: 200 })
    expect(wrapper.emitted('seek')).toBeTruthy()
    // 200/400 = 0.5, 0.5 * 1200 = 600
    expect(wrapper.emitted('seek')![0]).toEqual([600])
  })
})
