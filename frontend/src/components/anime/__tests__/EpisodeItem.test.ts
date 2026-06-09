import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import EpisodeItem from '../EpisodeItem.vue'

describe('EpisodeItem', () => {
  const defaultProps = {
    episodeNumber: 1,
    title: 'To You, in 2000 Years',
    thumbnailUrl: 'https://example.com/thumb.jpg',
    durationMinutes: 24,
    airDate: '2013-04-07',
  }

  it('renders episode number and title', () => {
    const wrapper = mount(EpisodeItem, { props: defaultProps })
    expect(wrapper.text()).toContain('Episode 1')
    expect(wrapper.text()).toContain('To You, in 2000 Years')
  })

  it('emits click on click', async () => {
    const wrapper = mount(EpisodeItem, { props: defaultProps })
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })

  it('emits play on play button click', async () => {
    const wrapper = mount(EpisodeItem, { props: defaultProps })
    await wrapper.find('.episode-overlay').trigger('click')
    expect(wrapper.emitted('play')).toBeTruthy()
  })

  it('shows fallback when thumbnail is null', () => {
    const wrapper = mount(EpisodeItem, {
      props: { ...defaultProps, thumbnailUrl: null },
    })
    expect(wrapper.find('.episode-thumb-fallback').exists()).toBe(true)
    expect(wrapper.find('.episode-thumb-fallback').text()).toBe('1')
  })

  it('shows duration when provided', () => {
    const wrapper = mount(EpisodeItem, { props: defaultProps })
    expect(wrapper.text()).toContain('24 min')
  })

  it('does not show duration when null', () => {
    const wrapper = mount(EpisodeItem, {
      props: { ...defaultProps, durationMinutes: null },
    })
    expect(wrapper.text()).not.toContain('min')
  })

  it('applies watched class when isWatched is true', () => {
    const wrapper = mount(EpisodeItem, {
      props: { ...defaultProps, isWatched: true },
    })
    expect(wrapper.find('.episode-check').exists()).toBe(true)
    expect(wrapper.classes()).toContain('watched')
  })

  it('applies selected class when isSelected is true', () => {
    const wrapper = mount(EpisodeItem, {
      props: { ...defaultProps, isSelected: true },
    })
    expect(wrapper.classes()).toContain('selected')
  })

  it('shows fallback title when title is null', () => {
    const wrapper = mount(EpisodeItem, {
      props: { ...defaultProps, title: null, episodeNumber: 5 },
    })
    expect(wrapper.text()).toContain('Episode 5')
  })
})
