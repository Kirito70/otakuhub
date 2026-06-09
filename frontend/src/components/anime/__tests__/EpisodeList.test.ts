import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import EpisodeList from '../EpisodeList.vue'
import EpisodeItem from '../EpisodeItem.vue'

const sampleItems = [
  {
    id: '1',
    episodeNumber: 1,
    title: 'Episode 1',
    airDate: '2024-01-01',
    thumbnailUrl: null,
    durationMinutes: 24,
  },
  {
    id: '2',
    episodeNumber: 2,
    title: 'Episode 2',
    airDate: '2024-01-08',
    thumbnailUrl: null,
    durationMinutes: 24,
  },
]

describe('EpisodeList', () => {
  it('renders header with total count', () => {
    const wrapper = mount(EpisodeList, {
      props: { items: sampleItems, loading: false, error: null, totalCount: 2 },
    })
    expect(wrapper.text()).toContain('Episodes')
    expect(wrapper.text()).toContain('2 episodes')
  })

  it('shows loading skeleton when loading', () => {
    const wrapper = mount(EpisodeList, {
      props: { items: [], loading: true, error: null, totalCount: 0 },
    })
    expect(wrapper.findAll('.skeleton-row').length).toBe(5)
  })

  it('shows error state with retry', async () => {
    const wrapper = mount(EpisodeList, {
      props: { items: [], loading: false, error: 'Failed', totalCount: 0 },
    })
    expect(wrapper.text()).toContain('Failed')
    await wrapper.find('.episode-list-state button').trigger('click')
    expect(wrapper.emitted('retry')).toBeTruthy()
  })

  it('shows empty state when no items', () => {
    const wrapper = mount(EpisodeList, {
      props: { items: [], loading: false, error: null, totalCount: 0 },
    })
    expect(wrapper.text()).toContain('No episodes available')
  })

  it('renders EpisodeItem components', () => {
    const wrapper = mount(EpisodeList, {
      props: { items: sampleItems, loading: false, error: null, totalCount: 2 },
    })
    const items = wrapper.findAllComponents(EpisodeItem)
    expect(items.length).toBe(2)
  })

  it('emits select when episode clicked', async () => {
    const wrapper = mount(EpisodeList, {
      props: { items: sampleItems, loading: false, error: null, totalCount: 2 },
    })
    const firstItem = wrapper.findComponent(EpisodeItem)
    await firstItem.trigger('click')
    expect(wrapper.emitted('select')).toBeTruthy()
    expect(wrapper.emitted('select')![0]).toEqual([1])
  })

  it('emits toggle-sort when sort button clicked', async () => {
    const wrapper = mount(EpisodeList, {
      props: { items: sampleItems, loading: false, error: null, totalCount: 2 },
    })
    await wrapper.find('.sort-toggle').trigger('click')
    expect(wrapper.emitted('toggle-sort')).toBeTruthy()
  })

  it('sorts items descending when sortOrder is desc', () => {
    const wrapper = mount(EpisodeList, {
      props: {
        items: sampleItems,
        loading: false,
        error: null,
        totalCount: 2,
        sortOrder: 'desc',
      },
    })
    const items = wrapper.findAllComponents(EpisodeItem)
    expect(items[0].props('episodeNumber')).toBe(2)
    expect(items[1].props('episodeNumber')).toBe(1)
  })

  it('applies watched state to watched episodes', () => {
    const wrapper = mount(EpisodeList, {
      props: {
        items: sampleItems,
        loading: false,
        error: null,
        totalCount: 2,
        watchedEpisodeNumbers: [1],
      },
    })
    const items = wrapper.findAllComponents(EpisodeItem)
    expect(items[0].props('isWatched')).toBe(true)
    expect(items[1].props('isWatched')).toBe(false)
  })
})
