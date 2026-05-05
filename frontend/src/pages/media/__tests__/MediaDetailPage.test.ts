import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import MediaDetailPage from '../MediaDetailPage.vue'

vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { id: 'abc' } }),
}))

vi.mock('src/composables/useMediaDetail', () => ({
  useMediaDetail: () => ({
    data: { value: null },
    isLoading: { value: false },
    error: { value: null },
    fetchById: vi.fn(),
  }),
}))

describe('MediaDetailPage', () => {
  it('renders media detail page shell', () => {
    const wrapper = mount(MediaDetailPage, {
      global: {
        stubs: {
          'q-page': { template: '<div><slot /></div>' },
          'q-banner': true,
          'q-spinner': true,
          'q-card': true,
          'q-img': true,
          'q-card-section': true,
          'q-btn': true,
          'q-separator': true,
          AddToListSheet: true,
        },
      },
    })

    expect(wrapper.exists()).toBe(true)
  })
})
