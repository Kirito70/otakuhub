import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ServerSelector from '../ServerSelector.vue'

const sampleServers = [
  {
    id: 's1',
    source: 'MegaPlay',
    language: 'sub',
    episodeNumber: 1,
    embedUrl: 'https://example.com/1',
    isAvailable: true,
  },
  {
    id: 's2',
    source: 'MegaPlay',
    language: 'dub',
    episodeNumber: 1,
    embedUrl: 'https://example.com/2',
    isAvailable: true,
  },
  {
    id: 's3',
    source: 'Anikoto',
    language: 'sub',
    episodeNumber: 1,
    embedUrl: null,
    isAvailable: false,
  },
]

describe('ServerSelector', () => {
  it('renders server label', () => {
    const wrapper = mount(ServerSelector, {
      props: { servers: [], loading: false, error: null, selectedServerId: null },
    })
    expect(wrapper.text()).toContain('Select Server')
  })

  it('renders server pills', () => {
    const wrapper = mount(ServerSelector, {
      props: {
        servers: sampleServers,
        loading: false,
        error: null,
        selectedServerId: null,
      },
    })
    const pills = wrapper.findAll('.server-pill:not(.skeleton)')
    expect(pills.length).toBe(3)
  })

  it('emits select with server id on click', async () => {
    const wrapper = mount(ServerSelector, {
      props: {
        servers: sampleServers,
        loading: false,
        error: null,
        selectedServerId: null,
      },
    })
    const firstPill = wrapper.find('.server-pill')
    await firstPill.trigger('click')
    expect(wrapper.emitted('select')).toBeTruthy()
    expect(wrapper.emitted('select')![0]).toEqual(['s1'])
  })

  it('disables unavailable servers', () => {
    const wrapper = mount(ServerSelector, {
      props: {
        servers: sampleServers,
        loading: false,
        error: null,
        selectedServerId: null,
      },
    })
    const pills = wrapper.findAll('.server-pill')
    expect(pills[2].classes()).toContain('unavailable')
    expect(pills[2].attributes('disabled')).toBeDefined()
  })

  it('shows skeleton when loading', () => {
    const wrapper = mount(ServerSelector, {
      props: { servers: [], loading: true, error: null, selectedServerId: null },
    })
    expect(wrapper.findAll('.server-pill.skeleton').length).toBe(3)
  })

  it('shows error message', () => {
    const wrapper = mount(ServerSelector, {
      props: {
        servers: [],
        loading: false,
        error: 'Server error',
        selectedServerId: null,
      },
    })
    expect(wrapper.text()).toContain('Server error')
  })

  it('shows empty message when no servers', () => {
    const wrapper = mount(ServerSelector, {
      props: { servers: [], loading: false, error: null, selectedServerId: null },
    })
    expect(wrapper.text()).toContain('No servers available')
  })

  it('shows SUB and DUB labels', () => {
    const wrapper = mount(ServerSelector, {
      props: {
        servers: sampleServers,
        loading: false,
        error: null,
        selectedServerId: null,
      },
    })
    expect(wrapper.text()).toContain('SUB')
    expect(wrapper.text()).toContain('DUB')
  })

  it('marks selected server as active', () => {
    const wrapper = mount(ServerSelector, {
      props: {
        servers: sampleServers,
        loading: false,
        error: null,
        selectedServerId: 's1',
      },
    })
    const pills = wrapper.findAll('.server-pill')
    expect(pills[0].classes()).toContain('active')
    expect(pills[1].classes()).not.toContain('active')
  })
})
