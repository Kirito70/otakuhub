import { defineComponent } from 'vue'
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

const QFormStub = defineComponent({
  name: 'QForm',
  emits: ['submit'],
  methods: {
    validate(): boolean {
      return false
    },
  },
  template: '<form @submit.prevent="$emit(\'submit\')"><slot /></form>',
})

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
          'q-form': QFormStub,
          'q-separator': true,
          'q-input': true,
          'q-btn': { template: '<button><slot />{{ label }}</button>', props: ['label'] },
          'q-banner': true,
          'app-page-state': { template: '<div><slot /></div>' },
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

  it('shows actionable validation message on invalid create submit', async () => {
    const wrapper = mount(WatchPartyPage, {
      global: {
        stubs: {
          'q-page': { template: '<div><slot /></div>' },
          'q-card': { template: '<div><slot /></div>' },
          'q-card-section': { template: '<div><slot /></div>' },
          'q-card-actions': { template: '<div><slot /></div>' },
          'q-form': QFormStub,
          'q-separator': true,
          'q-input': true,
          'q-btn': { template: '<button><slot />{{ label }}</button>', props: ['label'] },
          'q-banner': { template: '<div><slot /></div>' },
          'app-page-state': { template: '<div><slot /></div>' },
          'q-list': true,
          'q-item': true,
          'q-item-section': true,
          'q-item-label': true,
        },
      },
    })

    await wrapper.find('form').trigger('submit')
    expect(wrapper.text()).toContain('Please fix validation errors before submitting.')
  })
})
