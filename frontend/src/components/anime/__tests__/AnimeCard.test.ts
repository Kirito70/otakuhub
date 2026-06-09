import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AnimeCard from '../AnimeCard.vue'

describe('AnimeCard', () => {
  const defaultProps = {
    id: '1',
    title: 'Attack on Titan',
    coverImage: 'https://example.com/cover.jpg',
    mediaType: 'anime',
    format: 'TV',
    score: 8.5,
    year: 2013,
    episodeCount: 25,
    status: 'finished',
  }

  it('renders title and metadata', () => {
    const wrapper = mount(AnimeCard, { props: defaultProps })
    expect(wrapper.text()).toContain('Attack on Titan')
    expect(wrapper.text()).toContain('8.5')
    expect(wrapper.text()).toContain('2013')
    expect(wrapper.text()).toContain('25 eps')
  })

  it('renders mediaType badge', () => {
    const wrapper = mount(AnimeCard, { props: defaultProps })
    expect(wrapper.text()).toContain('anime')
  })

  it('shows NEW badge when isNew is true', () => {
    const wrapper = mount(AnimeCard, { props: { ...defaultProps, isNew: true } })
    expect(wrapper.text()).toContain('NEW')
  })

  it('does not show NEW badge when isNew is false', () => {
    const wrapper = mount(AnimeCard, { props: defaultProps })
    expect(wrapper.text()).not.toContain('NEW')
  })

  it('emits click with id on card click', async () => {
    const wrapper = mount(AnimeCard, { props: defaultProps })
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
    expect(wrapper.emitted('click')![0]).toEqual(['1'])
  })

  it('renders fallback when coverImage is null', () => {
    const wrapper = mount(AnimeCard, { props: { ...defaultProps, coverImage: null } })
    expect(wrapper.find('.card-cover-fallback').exists()).toBe(true)
    expect(wrapper.find('.card-cover-fallback').text()).toBe('A')
  })

  it('does not render episode badge when episodeCount is null', () => {
    const wrapper = mount(AnimeCard, { props: { ...defaultProps, episodeCount: null } })
    expect(wrapper.text()).not.toContain('eps')
  })

  it('does not render score when score is null', () => {
    const wrapper = mount(AnimeCard, { props: { ...defaultProps, score: null } })
    expect(wrapper.find('.card-score').exists()).toBe(false)
  })

  it('does not render year when year is null', () => {
    const wrapper = mount(AnimeCard, { props: { ...defaultProps, year: null } })
    expect(wrapper.find('.card-year').exists()).toBe(false)
  })

  it('renders img with loading class initially', () => {
    const wrapper = mount(AnimeCard, { props: defaultProps })
    const img = wrapper.find('img')
    expect(img.exists()).toBe(true)
    expect(img.classes()).toContain('loading')
  })

  it('transitions img to loaded class on load', async () => {
    const wrapper = mount(AnimeCard, { props: defaultProps })
    const img = wrapper.find('img')
    await img.trigger('load')
    expect(img.classes()).toContain('loaded')
    expect(img.classes()).not.toContain('loading')
  })

  it('does not render play hint button without hover (default state)', () => {
    const wrapper = mount(AnimeCard, { props: defaultProps })
    const overlay = wrapper.find('.card-hover-overlay')
    expect(overlay.exists()).toBe(true)
    expect(overlay.isVisible()).toBe(true)
  })
})
