import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import ImportListPage from '../ImportListPage.vue'

vi.mock('vue-router', () => ({
  useRoute: () => ({ query: {} }),
}))

vi.mock('src/boot/axios', () => ({
  api: {
    post: vi.fn().mockResolvedValue({ data: { job_id: 'job-123' } }),
  },
}))

describe('ImportListPage', () => {
  it('renders import list heading', () => {
    const wrapper = mount(ImportListPage, {
      global: {
        stubs: {
          'q-page': { template: '<div><slot /></div>' },
          'q-card': true,
          'q-card-section': true,
          'q-tabs': true,
          'q-tab': true,
          'q-route-tab': true,
          'q-separator': true,
          'q-input': true,
          'q-toggle': true,
          'q-banner': true,
          'q-card-actions': true,
          'q-btn': true,
        },
      },
    })

    expect(wrapper.text()).toContain('Import Lists')
  })
})
