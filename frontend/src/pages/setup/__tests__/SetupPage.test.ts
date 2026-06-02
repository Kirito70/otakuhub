import { defineComponent, ref } from 'vue'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import SetupPage from '../SetupPage.vue'

const formIsValid = ref(true)
const pushMock = vi.fn()

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: pushMock }),
}))

vi.mock('axios', () => ({
  default: {
    post: vi.fn().mockResolvedValue({ data: { id: 'u1' } }),
  },
}))

vi.mock('src/stores/bootstrap', () => ({
  useBootstrapStore: () => ({
    refresh: vi.fn().mockResolvedValue(undefined),
  }),
}))

const QFormStub = defineComponent({
  name: 'QForm',
  emits: ['submit'],
  methods: {
    validate(): boolean {
      return formIsValid.value
    },
  },
  template: '<form @submit="$emit(\'submit\', $event)"><slot /></form>',
})

describe('SetupPage', () => {
  beforeEach(() => {
    formIsValid.value = true
    pushMock.mockReset()
  })

  it('shows validation error when form is invalid', async () => {
    formIsValid.value = false
    const wrapper = mount(SetupPage, {
      global: {
        stubs: {
          'q-page': { template: '<div><slot /></div>' },
          'q-card': { template: '<div><slot /></div>' },
          'q-card-section': { template: '<div><slot /></div>' },
          'q-input': true,
          'q-banner': { template: '<div><slot /></div>' },
          'q-btn': { template: '<button><slot />{{ label }}</button>', props: ['label'] },
          'q-form': QFormStub,
        },
      },
    })

    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Please fix validation errors before submitting.')
  })

  it('submits bootstrap and redirects to login on success', async () => {
    const wrapper = mount(SetupPage, {
      global: {
        stubs: {
          'q-page': { template: '<div><slot /></div>' },
          'q-card': { template: '<div><slot /></div>' },
          'q-card-section': { template: '<div><slot /></div>' },
          'q-input': true,
          'q-banner': { template: '<div><slot /></div>' },
          'q-btn': { template: '<button><slot />{{ label }}</button>', props: ['label'] },
          'q-form': QFormStub,
        },
      },
    })

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(pushMock).toHaveBeenCalledWith({ name: 'login' })
  })
})
