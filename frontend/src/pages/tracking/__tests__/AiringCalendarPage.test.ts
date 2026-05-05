import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import AiringCalendarPage from '../AiringCalendarPage.vue'

vi.mock('src/boot/axios', () => ({
  api: {
    get: vi.fn().mockResolvedValue({ data: { items: [] } }),
  },
}))

describe('AiringCalendarPage', () => {
  it('renders airing calendar title', () => {
    const wrapper = mount(AiringCalendarPage, {
      global: {
        stubs: {
          'q-page': { template: '<div><slot /></div>' },
          'q-btn': true,
          'q-banner': true,
          'q-list': true,
          'q-item': true,
          'q-item-section': true,
          'q-avatar': true,
          'q-icon': true,
          'q-item-label': true,
        },
      },
    })

    expect(wrapper.text()).toContain('Airing Calendar')
  })
})
