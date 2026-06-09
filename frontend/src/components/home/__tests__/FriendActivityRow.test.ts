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
  it('renders activity items', () => {
    const wrapper = mount(FriendActivityRow, { props: { items: sampleActivity, loading: false, error: null } })
    expect(wrapper.text()).toContain('Sakura')
    expect(wrapper.text()).toContain('Jujutsu Kaisen')
    expect(wrapper.text()).toContain('kirito')
  })

  it('shows skeleton when loading', () => {
    const wrapper = mount(FriendActivityRow, { props: { items: [], loading: true, error: null } })
    expect(wrapper.findAll('.skeleton-row').length).toBe(3)
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
    const wrapper = mount(FriendActivityRow, { props: { items: sampleActivity, loading: false, error: null } })
    const firstItem = wrapper.find('.activity-item')
    await firstItem.trigger('click')
    expect(wrapper.emitted('item-click')).toBeTruthy()
    expect(wrapper.emitted('item-click')![0]).toEqual(['m1'])
  })

  it('renders avatar fallback when avatarUrl is null', () => {
    const wrapper = mount(FriendActivityRow, { props: { items: sampleActivity, loading: false, error: null } })
    const fallbacks = wrapper.findAll('.avatar-fallback')
    expect(fallbacks.length).toBe(2)
    expect(fallbacks[0].text()).toBe('S')
    expect(fallbacks[1].text()).toBe('K')
  })
})
