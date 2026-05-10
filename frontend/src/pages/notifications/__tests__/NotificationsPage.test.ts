import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import NotificationsPage from '../NotificationsPage.vue'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

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
    patch: vi.fn().mockResolvedValue({ data: { updated_count: 0 } }),
  },
}))

describe('NotificationsPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders notification bell heading', () => {
    const wrapper = mount(NotificationsPage, {
      global: {
        stubs: {
          'q-page': { template: '<div><slot /></div>' },
          'q-btn': { template: '<button><slot />{{ label }}</button>', props: ['label'] },
          'q-banner': { template: '<div><slot /></div>' },
          'q-list': { template: '<div><slot /></div>' },
          'q-item': { template: '<div><slot /></div>' },
          'q-item-section': { template: '<div><slot /></div>' },
          'q-item-label': { template: '<div><slot /></div>' },
          'q-checkbox': true,
          'q-badge': true,
          'app-page-state': { template: '<div><slot /></div>' },
        },
      },
    })

    expect(wrapper.text()).toContain('Notification Bell')
  })
})
