import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import DiscoverPage from '../DiscoverPage.vue'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn().mockResolvedValue(undefined) }),
}))

vi.mock('src/composables/useMediaSearch', () => ({
  useMediaSearch: () => ({
    data: { value: [] },
    total: { value: 0 },
    isLoading: { value: false },
    error: { value: null },
    search: vi.fn(),
  }),
}))

describe('DiscoverPage', () => {
  it('renders search screen shell', () => {
    const wrapper = mount(DiscoverPage, {
      global: {
        stubs: {
          'q-page': { template: '<div><slot /></div>' },
          'q-input': true,
          'q-icon': true,
          'q-select': true,
          'q-btn': true,
          'q-banner': true,
          'q-card': true,
          'q-img': true,
          'q-card-section': true,
        },
      },
    })

    expect(wrapper.exists()).toBe(true)
  })
})
