import { describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'

import RelatedMediaCarousel from '../RelatedMediaCarousel.vue'

const sampleItems = [
  { id: '1', title: 'Attack on Titan S2', coverImage: 'https://example.com/aot.jpg', relationType: 'sequel' },
  { id: '2', title: 'Attack on Titan: Junior High', coverImage: null, relationType: 'spin_off' },
  { id: '3', title: 'Attack on Titan S0', coverImage: 'https://example.com/prequel.jpg', relationType: 'prequel' },
]

describe('RelatedMediaCarousel', () => {
  it('renders title heading', () => {
    const wrapper = mount(RelatedMediaCarousel, {
      props: { items: [], isLoading: false, error: null },
    })
    expect(wrapper.text()).toContain('Related Media')
  })

  it('shows loading skeleton when isLoading is true', () => {
    const wrapper = mount(RelatedMediaCarousel, {
      props: { items: [], isLoading: true, error: null },
    })
    expect(wrapper.findAll('.skeleton-card').length).toBe(5)
    expect(wrapper.find('.carousel-track').exists()).toBe(false)
  })

  it('shows error state with retry button', () => {
    const wrapper = mount(RelatedMediaCarousel, {
      props: { items: [], isLoading: false, error: 'Something went wrong.' },
    })
    expect(wrapper.text()).toContain('Something went wrong.')
    const retryBtn = wrapper.find('button')
    expect(retryBtn.exists()).toBe(true)
  })

  it('emits retry when retry button clicked', async () => {
    const wrapper = mount(RelatedMediaCarousel, {
      props: { items: [], isLoading: false, error: 'Error!' },
    })
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('retry')).toBeTruthy()
  })

  it('shows empty state when items array is empty', () => {
    const wrapper = mount(RelatedMediaCarousel, {
      props: { items: [], isLoading: false, error: null },
    })
    expect(wrapper.text()).toContain('No related media.')
  })

  it('renders carousel cards when items are provided', () => {
    const wrapper = mount(RelatedMediaCarousel, {
      props: { items: sampleItems, isLoading: false, error: null },
    })
    const cards = wrapper.findAll('.carousel-card')
    expect(cards.length).toBe(3)
    expect(wrapper.text()).toContain('Attack on Titan S2')
    expect(wrapper.text()).toContain('Attack on Titan: Junior High')
  })

  it('shows cover image when coverImage is present', () => {
    const wrapper = mount(RelatedMediaCarousel, {
      props: { items: [sampleItems[0]], isLoading: false, error: null },
    })
    const img = wrapper.find('img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe('https://example.com/aot.jpg')
  })

  it('shows placeholder text when coverImage is null', () => {
    const wrapper = mount(RelatedMediaCarousel, {
      props: { items: [sampleItems[1]], isLoading: false, error: null },
    })
    expect(wrapper.text()).toContain('No Cover')
    expect(wrapper.find('img').exists()).toBe(false)
  })

  it('displays relation badge for each card', () => {
    const wrapper = mount(RelatedMediaCarousel, {
      props: { items: sampleItems, isLoading: false, error: null },
    })
    const badges = wrapper.findAll('.relation-badge')
    expect(badges.length).toBe(3)
    expect(badges[0].text()).toBe('Sequel')
    expect(badges[1].text()).toBe('Spin-off')
    expect(badges[2].text()).toBe('Prequel')
  })

  it('uses "Other" label for "other" relation type', () => {
    const wrapper = mount(RelatedMediaCarousel, {
      props: {
        items: [{ id: 'x', title: 'Other Relation', coverImage: null, relationType: 'other' }],
        isLoading: false,
        error: null,
      },
    })
    expect(wrapper.find('.relation-badge').text()).toBe('Other')
  })

  it('emits navigate with item id when card is clicked', async () => {
    const wrapper = mount(RelatedMediaCarousel, {
      props: { items: sampleItems, isLoading: false, error: null },
    })
    const cards = wrapper.findAll('.carousel-card')
    await cards[0].trigger('click')
    expect(wrapper.emitted('navigate')).toBeTruthy()
    expect(wrapper.emitted('navigate')![0]).toEqual(['1'])
  })

  it('falls back to raw type when relationLabel has no mapping', () => {
    const wrapper = mount(RelatedMediaCarousel, {
      props: {
        items: [{ id: 'y', title: 'Custom', coverImage: null, relationType: 'custom_rel' }],
        isLoading: false,
        error: null,
      },
    })
    expect(wrapper.find('.relation-badge').text()).toBe('custom_rel')
  })
})
