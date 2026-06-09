import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TrendingCarousel from '../TrendingCarousel.vue'
import AnimeCard from '../AnimeCard.vue'

const sampleItems = [
  {
    id: '1',
    title: 'Naruto',
    coverImage: null,
    mediaType: 'anime',
    format: 'TV',
    score: 7.5,
    year: 2002,
    episodeCount: 220,
    titleEnglish: null,
    coverImageLarge: null,
    season: null,
    status: 'finished',
    synopsis: null,
  },
  {
    id: '2',
    title: 'One Piece',
    coverImage: null,
    mediaType: 'anime',
    format: 'TV',
    score: 8.0,
    year: 1999,
    episodeCount: 1000,
    titleEnglish: null,
    coverImageLarge: null,
    season: null,
    status: 'releasing',
    synopsis: null,
  },
  {
    id: '3',
    title: 'Bleach',
    coverImage: null,
    mediaType: 'anime',
    format: 'TV',
    score: 7.8,
    year: 2004,
    episodeCount: 366,
    titleEnglish: null,
    coverImageLarge: null,
    season: null,
    status: 'finished',
    synopsis: null,
  },
]

describe('TrendingCarousel', () => {
  it('renders title', () => {
    const wrapper = mount(TrendingCarousel, {
      props: { items: [], loading: false, error: null, title: 'Trending Now' },
    })
    expect(wrapper.text()).toContain('Trending Now')
  })

  it('renders default title when not provided', () => {
    const wrapper = mount(TrendingCarousel, {
      props: { items: [], loading: false, error: null },
    })
    expect(wrapper.text()).toContain('Trending Now')
  })

  it('shows loading skeletons when loading', () => {
    const wrapper = mount(TrendingCarousel, {
      props: { items: [], loading: true, error: null },
    })
    expect(wrapper.findAll('.skeleton-card').length).toBe(7)
  })

  it('shows error state with retry button', async () => {
    const wrapper = mount(TrendingCarousel, {
      props: { items: [], loading: false, error: 'Failed to load' },
    })
    expect(wrapper.text()).toContain('Failed to load')
    const btn = wrapper.find('button')
    await btn.trigger('click')
    expect(wrapper.emitted('retry')).toBeTruthy()
  })

  it('shows empty state when no items', () => {
    const wrapper = mount(TrendingCarousel, {
      props: { items: [], loading: false, error: null },
    })
    expect(wrapper.text()).toContain('No trending items available')
  })

  it('renders AnimeCard components for each item', () => {
    const wrapper = mount(TrendingCarousel, {
      props: { items: sampleItems, loading: false, error: null },
    })
    const cards = wrapper.findAllComponents(AnimeCard)
    expect(cards.length).toBe(3)
    expect(cards[0].props('title')).toBe('Naruto')
    expect(cards[1].props('title')).toBe('One Piece')
    expect(cards[2].props('title')).toBe('Bleach')
  })

  it('emits item-click when card is clicked', async () => {
    const wrapper = mount(TrendingCarousel, {
      props: { items: sampleItems, loading: false, error: null },
    })
    const card = wrapper.findComponent(AnimeCard)
    await card.trigger('click')
    expect(wrapper.emitted('item-click')).toBeTruthy()
    expect(wrapper.emitted('item-click')![0]).toEqual(['1'])
  })

  it('renders arrow navigation buttons', () => {
    const wrapper = mount(TrendingCarousel, {
      props: { items: sampleItems, loading: false, error: null },
    })
    const arrows = wrapper.findAll('.arrow-btn')
    expect(arrows.length).toBe(2)
  })

  it('hides arrows when loading', () => {
    const wrapper = mount(TrendingCarousel, {
      props: { items: [], loading: true, error: null },
    })
    expect(wrapper.find('.carousel-arrows').exists()).toBe(false)
  })

  it('hides arrows when empty', () => {
    const wrapper = mount(TrendingCarousel, {
      props: { items: [], loading: false, error: null },
    })
    expect(wrapper.find('.carousel-arrows').exists()).toBe(false)
  })

  it('renders gradient fade elements', () => {
    const wrapper = mount(TrendingCarousel, {
      props: { items: sampleItems, loading: false, error: null },
    })
    expect(wrapper.find('.carousel-fade-left').exists()).toBe(true)
    expect(wrapper.find('.carousel-fade-right').exists()).toBe(true)
  })

  it('applies custom itemWidth to cards', () => {
    const wrapper = mount(TrendingCarousel, {
      props: { items: sampleItems, loading: false, error: null, itemWidth: 200 },
    })
    const cards = wrapper.findAllComponents(AnimeCard)
    cards.forEach((card) => {
      expect(card.attributes('style')).toContain('200px')
    })
  })
})
