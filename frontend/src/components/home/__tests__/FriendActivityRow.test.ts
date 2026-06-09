import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FriendActivityRow from '../FriendActivityRow.vue'

const sampleActivity = [
  {
    id: 'a1',
    userId: 'u1',
    username: 'sakura',
    displayName: 'Sakura',
    avatarUrl: null,
    mediaId: 'm1',
    mediaTitle: 'Jujutsu Kaisen',
    mediaCoverImage: null,
    eventType: 'status_changed',
    newStatus: 'watching',
    newProgress: null,
    createdAt: new Date().toISOString(),
  },
  {
    id: 'a2',
    userId: 'u2',
    username: 'kirito',
    displayName: null,
    avatarUrl: null,
    mediaId: 'm2',
    mediaTitle: 'Attack on Titan',
    mediaCoverImage: null,
    eventType: 'progress_updated',
    newStatus: null,
    newProgress: 12,
    createdAt: new Date(Date.now() - 3600000).toISOString(),
  },
]

describe('FriendActivityRow', () => {
  const defaultProps = { items: sampleActivity, loading: false, error: null }

  it('renders activity items', () => {
    const wrapper = mount(FriendActivityRow, { props: defaultProps })
    expect(wrapper.text()).toContain('Sakura')
    expect(wrapper.text()).toContain('Jujutsu Kaisen')
    expect(wrapper.text()).toContain('kirito')
  })

  it('shows skeleton when loading and items empty', () => {
    const wrapper = mount(FriendActivityRow, { props: { items: [], loading: true, error: null } })
    expect(wrapper.findAll('.skeleton-row').length).toBe(3)
  })

  it('does not show skeleton when loading with items already present', () => {
    const wrapper = mount(FriendActivityRow, { props: { ...defaultProps, loading: true } })
    expect(wrapper.findAll('.skeleton-row').length).toBe(0)
    expect(wrapper.find('.activity-list').exists()).toBe(true)
  })

  it('shows error message', () => {
    const wrapper = mount(FriendActivityRow, { props: { items: [], loading: false, error: 'Failed' } })
    expect(wrapper.text()).toContain('Failed')
  })

  it('shows empty message', () => {
    const wrapper = mount(FriendActivityRow, { props: { items: [], loading: false, error: null } })
    expect(wrapper.text()).toContain('No friend activity yet')
  })

  it('emits item-click with mediaId on click', async () => {
    const wrapper = mount(FriendActivityRow, { props: defaultProps })
    const firstItem = wrapper.find('.activity-item')
    await firstItem.trigger('click')
    expect(wrapper.emitted('item-click')).toBeTruthy()
    expect(wrapper.emitted('item-click')![0]).toEqual(['m1'])
  })

  it('renders avatar fallback when avatarUrl is null', () => {
    const wrapper = mount(FriendActivityRow, { props: defaultProps })
    const fallbacks = wrapper.findAll('.avatar-fallback')
    expect(fallbacks.length).toBe(2)
    expect(fallbacks[0].text()).toBe('S')
    expect(fallbacks[1].text()).toBe('K')
  })

  // ── Filter pills ────────────────────────────────────────────────────────

  it('renders filter pills', () => {
    const wrapper = mount(FriendActivityRow, { props: defaultProps })
    const pills = wrapper.findAll('.filter-pill')
    expect(pills.length).toBe(4)
    expect(pills[0].text()).toBe('All')
    expect(pills[1].text()).toBe('Anime')
    expect(pills[2].text()).toBe('Manga')
    expect(pills[3].text()).toBe('Manhwa')
  })

  it('marks the active filter pill', () => {
    const wrapper = mount(FriendActivityRow, { props: { ...defaultProps, activeFilter: 'anime' } })
    const pills = wrapper.findAll('.filter-pill')
    expect(pills[0].classes()).not.toContain('active')
    expect(pills[1].classes()).toContain('active')
  })

  it('emits filter-change when filter pill clicked', async () => {
    const wrapper = mount(FriendActivityRow, { props: defaultProps })
    const pills = wrapper.findAll('.filter-pill')
    await pills[1].trigger('click')
    expect(wrapper.emitted('filter-change')).toBeTruthy()
    expect(wrapper.emitted('filter-change')![0]).toEqual(['anime'])
  })

  // ── Load More ───────────────────────────────────────────────────────────

  it('shows Load More button when hasMore is true', () => {
    const wrapper = mount(FriendActivityRow, { props: { ...defaultProps, hasMore: true } })
    expect(wrapper.text()).toContain('Load More')
  })

  it('hides Load More button when hasMore is false or undefined', () => {
    const wrapper = mount(FriendActivityRow, { props: { ...defaultProps, hasMore: false } })
    expect(wrapper.text()).not.toContain('Load More')
  })

  it('emits load-more when Load More clicked', async () => {
    const wrapper = mount(FriendActivityRow, { props: { ...defaultProps, hasMore: true } })
    const btn = wrapper.find('.load-more-btn')
    await btn.trigger('click')
    expect(wrapper.emitted('load-more')).toBeTruthy()
  })

  it('Load More button is disabled when loading', () => {
    const wrapper = mount(FriendActivityRow, { props: { ...defaultProps, hasMore: true, loading: true } })
    const btn = wrapper.find('.load-more-btn')
    expect(btn.attributes('disabled')).toBeDefined()
  })

  it('filter pills are disabled when filterLoading is true', () => {
    const wrapper = mount(FriendActivityRow, { props: { ...defaultProps, filterLoading: true } })
    const pills = wrapper.findAll('.filter-pill')
    pills.forEach((pill) => {
      expect(pill.attributes('disabled')).toBeDefined()
    })
  })
})
