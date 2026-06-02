import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import MyListPage from '../MyListPage.vue'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn().mockResolvedValue(undefined) }),
  useRoute: () => ({ params: { status: 'watching' } }),
}))

vi.mock('src/stores/tracking', () => ({
  useTrackingStore: () => ({
    byStatus: { watching: [] },
    isLoading: false,
    error: null,
    customLists: [],
    fetchMyList: vi.fn(),
    updateEntry: vi.fn(),
    createCustomList: vi.fn(),
    replaceCustomListEntries: vi.fn(),
  }),
}))

describe('MyListPage', () => {
  it('renders my list heading', () => {
    const wrapper = mount(MyListPage, {
      global: {
        stubs: {
          'q-page': { template: '<div><slot /></div>' },
          'q-banner': true,
          'q-tabs': true,
          'q-tab': true,
          'q-route-tab': true,
          'q-separator': true,
          'q-spinner': true,
          'q-list': true,
          'q-item': true,
          'q-item-section': true,
          'q-avatar': true,
          'q-icon': true,
          'q-item-label': true,
          'q-card': true,
          'q-card-section': true,
          'q-input': true,
          'q-btn': true,
          'q-dialog': true,
          'q-card-actions': true,
          ProgressWidget: true,
          ScoreWidget: true,
        },
      },
    })

    expect(wrapper.text()).toContain('My List')
  })
})
