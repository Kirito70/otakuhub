import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import WatchPartyPage from '../WatchPartyPage.vue'

vi.mock('src/boot/axios', () => ({
  api: {
    get: vi.fn().mockResolvedValue({
      data: {
        items: [],
        total: 0,
        limit: 50,
        offset: 0,
      },
    }),
  },
}))

describe('WatchPartyPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders watch parties title', () => {
    const wrapper = mount(WatchPartyPage, {
      global: {
        stubs: {
          'q-page': { template: '<div><slot /></div>' },
          'q-card': { template: '<div><slot /></div>' },
          'q-card-section': { template: '<div><slot /></div>' },
          'q-card-actions': { template: '<div><slot /></div>' },
          'q-separator': true,
          'q-input': true,
          'q-btn': { template: '<button><slot />{{ label }}</button>', props: ['label'] },
          'q-banner': true,
          'q-list': true,
          'q-item': true,
          'q-item-section': true,
          'q-item-label': true,
        },
      },
    })

    expect(wrapper.text()).toContain('Watch Parties')
    expect(wrapper.text()).toContain('Create Watch Party')
  })
})
