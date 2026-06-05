import { defineComponent, ref } from 'vue'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import SetupPage from '../SetupPage.vue'

const formIsValid = ref(true)
const pushMock = vi.fn()
const axiosPostMock = vi.fn()

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: pushMock }),
}))

vi.mock('axios', () => ({
  default: { post: (...args: unknown[]) => axiosPostMock(...args) },
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
    axiosPostMock.mockReset()
  })

  const stubs = {
    'q-page': { template: '<div><slot /></div>' },
    'q-card': { template: '<div><slot /></div>' },
    'q-card-section': { template: '<div><slot /></div>' },
    'q-input': { template: '<div><label>{{ label }}</label><input /></div>', props: ['label'], inheritAttrs: false },
    'q-banner': { template: '<div><slot /></div>' },
    'q-btn': { template: '<button :disabled="loading"><slot />{{ label }}</button>', props: ['label', 'loading', 'type'] },
    'q-form': QFormStub,
  }

  it('shows validation error when form is invalid', async () => {
    formIsValid.value = false
    const wrapper = mount(SetupPage, { global: { stubs } })

    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Please fix validation errors before submitting.')
  })

  it('renders all form fields', () => {
    const wrapper = mount(SetupPage, { global: { stubs } })

    const html = wrapper.html()
    expect(html).toContain('Username')
    expect(html).toContain('Email')
    expect(html).toContain('Password')
    expect(html).toContain('Confirm Password')
  })

  it('renders submit button with correct label', () => {
    const wrapper = mount(SetupPage, { global: { stubs } })

    expect(wrapper.text()).toContain('Create Super Admin')
  })

  it('submits bootstrap and redirects to login on success', async () => {
    axiosPostMock.mockResolvedValue({ data: { id: 'u1' } })
    const wrapper = mount(SetupPage, { global: { stubs } })

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(axiosPostMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/setup/bootstrap-admin'),
      expect.objectContaining({ username: '', email: '', password: '' }),
    )
    expect(pushMock).toHaveBeenCalledWith({ name: 'login' })
  })

  it('disables submit button while loading', async () => {
    axiosPostMock.mockImplementation(() => new Promise(() => {})) // never resolves
    const wrapper = mount(SetupPage, { global: { stubs } })

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    const btn = wrapper.find('button')
    expect(btn.attributes('disabled')).toBeDefined()
  })

  it('shows success banner after completion', async () => {
    axiosPostMock.mockResolvedValue({ data: { id: 'u1' } })
    const wrapper = mount(SetupPage, { global: { stubs } })

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('Setup complete. You can now sign in.')
  })

  it('shows error banner on API failure (already initialized / 5xx)', async () => {
    axiosPostMock.mockRejectedValue(new Error('Conflict'))
    const wrapper = mount(SetupPage, { global: { stubs } })

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('Setup failed. It may already be completed.')
    expect(pushMock).not.toHaveBeenCalled()
  })
})
