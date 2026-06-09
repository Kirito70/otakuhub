import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import GenrePills from '../GenrePills.vue'

const sampleGenres = [
  { id: '1', name: 'Action', slug: 'action' },
  { id: '2', name: 'Romance', slug: 'romance' },
  { id: '3', name: 'Fantasy', slug: 'fantasy' },
]

describe('GenrePills', () => {
  it('renders genre pills', () => {
    const wrapper = mount(GenrePills, { props: { items: sampleGenres, loading: false, error: null } })
    expect(wrapper.text()).toContain('Action')
    expect(wrapper.text()).toContain('Romance')
    expect(wrapper.text()).toContain('Fantasy')
  })

  it('shows skeleton when loading', () => {
    const wrapper = mount(GenrePills, { props: { items: [], loading: true, error: null } })
    expect(wrapper.findAll('.pill.skeleton').length).toBe(6)
  })

  it('shows error message', () => {
    const wrapper = mount(GenrePills, { props: { items: [], loading: false, error: 'Failed' } })
    expect(wrapper.text()).toContain('Failed')
  })

  it('shows empty message when no genres', () => {
    const wrapper = mount(GenrePills, { props: { items: [], loading: false, error: null } })
    expect(wrapper.text()).toContain('No genres available')
  })

  it('emits select with slug on click', async () => {
    const wrapper = mount(GenrePills, { props: { items: sampleGenres, loading: false, error: null } })
    const buttons = wrapper.findAll('button')
    await buttons[0].trigger('click')
    expect(wrapper.emitted('select')).toBeTruthy()
    expect(wrapper.emitted('select')![0]).toEqual(['action'])
  })
})
