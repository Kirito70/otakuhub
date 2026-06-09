import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AnimeGrid from '../AnimeGrid.vue'
import AnimeCard from '../AnimeCard.vue'

const sampleItems = [
  {
    id: '1',
    title: 'Naruto',
    titleEnglish: 'Naruto',
    coverImage: null,
    coverImageLarge: null,
    mediaType: 'anime',
    format: 'TV',
    score: 7.5,
    year: 2002,
    episodeCount: 220,
    season: null,
    status: 'finished',
    synopsis: null,
  },
]

describe('AnimeGrid', () => {
  it('renders title when provided', () => {
    const wrapper = mount(AnimeGrid, {
      props: { items: [], loading: false, error: null, title: 'Trending' },
    })
    expect(wrapper.text()).toContain('Trending')
  })

  it('does not render title section when title is not provided', () => {
    const wrapper = mount(AnimeGrid, {
      props: { items: [], loading: false, error: null },
    })
    expect(wrapper.find('.section-header').exists()).toBe(false)
  })

  it('shows loading skeletons when loading', () => {
    const wrapper = mount(AnimeGrid, {
      props: { items: [], loading: true, error: null },
    })
    const cards = wrapper.findAllComponents(AnimeCard)
    expect(cards.length).toBeGreaterThan(0)
    expect(cards.length).toBe(8)
  })

  it('shows error state with retry button', async () => {
    const wrapper = mount(AnimeGrid, {
      props: { items: [], loading: false, error: 'Failed to load' },
    })
    expect(wrapper.text()).toContain('Failed to load')
    const btn = wrapper.find('button')
    expect(btn.exists()).toBe(true)
    await btn.trigger('click')
    expect(wrapper.emitted('retry')).toBeTruthy()
  })

  it('shows empty state when no items', () => {
    const wrapper = mount(AnimeGrid, {
      props: { items: [], loading: false, error: null },
    })
    expect(wrapper.text()).toContain('No items to display')
  })

  it('shows custom empty message when provided', () => {
    const wrapper = mount(AnimeGrid, {
      props: {
        items: [],
        loading: false,
        error: null,
        emptyMessage: 'Nothing here yet',
      },
    })
    expect(wrapper.text()).toContain('Nothing here yet')
  })

  it('renders items as AnimeCards', () => {
    const wrapper = mount(AnimeGrid, {
      props: { items: sampleItems, loading: false, error: null },
    })
    const cards = wrapper.findAllComponents(AnimeCard)
    expect(cards.length).toBe(1)
    expect(cards[0].props('title')).toBe('Naruto')
  })

  it('emits item-click when card is clicked', async () => {
    const wrapper = mount(AnimeGrid, {
      props: { items: sampleItems, loading: false, error: null },
    })
    const card = wrapper.findComponent(AnimeCard)
    await card.trigger('click')
    expect(wrapper.emitted('item-click')).toBeTruthy()
    expect(wrapper.emitted('item-click')![0]).toEqual(['1'])
  })

  it('does not render card grid when loading', () => {
    const wrapper = mount(AnimeGrid, {
      props: { items: sampleItems, loading: true, error: null },
    })
    // Should show skeletons, not the actual items
    expect(wrapper.text()).not.toContain('Naruto')
  })

  it('does not render card grid when error', () => {
    const wrapper = mount(AnimeGrid, {
      props: { items: sampleItems, loading: false, error: 'Oops' },
    })
    expect(wrapper.text()).not.toContain('Naruto')
  })
})
