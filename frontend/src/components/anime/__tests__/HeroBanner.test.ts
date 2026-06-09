import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import HeroBanner from '../HeroBanner.vue'

describe('HeroBanner', () => {
  const defaultProps = {
    title: 'Attack on Titan',
    titleEnglish: 'Shingeki no Kyojin',
    synopsis: 'A long synopsis that exceeds three hundred characters. '.repeat(10).trim(),
    score: 9.0,
    year: 2013,
    mediaType: 'anime',
    format: 'TV',
    status: 'finished',
    episodeCount: 25,
    genres: ['Action', 'Drama', 'Fantasy'],
  }

  it('renders title and english title', () => {
    const wrapper = mount(HeroBanner, { props: defaultProps })
    expect(wrapper.text()).toContain('Attack on Titan')
    expect(wrapper.text()).toContain('Shingeki no Kyojin')
  })

  it('renders tags for media type, format, status, year, episodes', () => {
    const wrapper = mount(HeroBanner, { props: defaultProps })
    expect(wrapper.text()).toContain('anime')
    expect(wrapper.text()).toContain('TV')
    expect(wrapper.text()).toContain('finished')
    expect(wrapper.text()).toContain('2013')
    expect(wrapper.text()).toContain('25 eps')
  })

  it('renders genre chips', () => {
    const wrapper = mount(HeroBanner, { props: defaultProps })
    expect(wrapper.text()).toContain('Action')
    expect(wrapper.text()).toContain('Drama')
    expect(wrapper.text()).toContain('Fantasy')
  })

  it('emits synopsis-toggle when read more clicked', async () => {
    const wrapper = mount(HeroBanner, { props: defaultProps })
    const btn = wrapper.find('.synopsis-toggle')
    expect(btn.exists()).toBe(true)
    await btn.trigger('click')
    expect(wrapper.emitted('synopsis-toggle')).toBeTruthy()
  })

  it('does not show synopsis toggle for short synopsis', () => {
    const wrapper = mount(HeroBanner, {
      props: { ...defaultProps, synopsis: 'Short.' },
    })
    expect(wrapper.find('.synopsis-toggle').exists()).toBe(false)
  })

  it('shows fallback text when synopsis is null', () => {
    const wrapper = mount(HeroBanner, {
      props: { ...defaultProps, synopsis: null },
    })
    expect(wrapper.text()).toContain('No synopsis available')
  })

  it('renders ScoreRing when score is not null', () => {
    const wrapper = mount(HeroBanner, { props: defaultProps })
    expect(wrapper.findComponent({ name: 'ScoreRing' }).exists()).toBe(true)
  })

  it('renders with banner background style', () => {
    const wrapper = mount(HeroBanner, {
      props: { ...defaultProps, bannerImage: 'https://example.com/banner.jpg' },
    })
    const bg = wrapper.find('.hero-bg')
    expect(bg.exists()).toBe(true)
  })

  it('changes synopsis toggle text based on expanded state', () => {
    const wrapperExpanded = mount(HeroBanner, {
      props: { ...defaultProps, isSynopsisExpanded: true },
    })
    expect(wrapperExpanded.text()).toContain('Show less')

    const wrapperCollapsed = mount(HeroBanner, {
      props: { ...defaultProps, isSynopsisExpanded: false },
    })
    expect(wrapperCollapsed.text()).toContain('Read more')
  })
})
