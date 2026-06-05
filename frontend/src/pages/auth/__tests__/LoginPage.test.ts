import { defineComponent, ref } from 'vue'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import LoginPage from '../LoginPage.vue'

// Shared reactive refs for auth store mock
const isLoadingRef = ref(false)
const errorRef = ref<string | null>(null)
const mockLogin = vi.fn()

const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
}))

// QForm stub with configurable validate()
const formIsValid = ref(true)
const QFormStub = defineComponent({
  name: 'QForm',
  emits: ['submit'],
  methods: {
    validate(): Promise<boolean> {
      return Promise.resolve(formIsValid.value)
    },
  },
  template: '<form @submit.prevent="$emit(\'submit\')"><slot /></form>',
})

vi.mock('src/stores/auth', () => ({
  useAuthStore: () => ({
    isLoading: isLoadingRef,
    error: errorRef,
    login: mockLogin,
  }),
}))

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    formIsValid.value = true
    isLoadingRef.value = false
    errorRef.value = null
    mockLogin.mockReset()
  })

  const stubs = {
    'q-page': { template: '<div><slot /></div>' },
    'q-card': { template: '<div><slot /></div>' },
    'q-card-section': { template: '<div><slot /></div>' },
    'q-card-actions': { template: '<div><slot /></div>' },
    'q-input': { props: ['modelValue', 'rules', 'lazyRules', 'type', 'label'], template: '<input :type="type" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />' },
    'q-btn': { props: ['label', 'loading', 'type', 'color', 'flat'], template: '<button :disabled="loading" :type="type" @click="$emit(\'click\')">{{ label }}</button>' },
    'q-banner': { template: '<div class="q-banner"><slot /></div>' },
    'q-form': QFormStub,
    'q-icon': true,
    'q-spinner': true,
  }

  it('renders login form with heading', () => {
    const wrapper = mount(LoginPage, { global: { stubs } })
    expect(wrapper.text()).toContain('Login')
    expect(wrapper.text()).toContain('Sign in to continue')
  })

  it('shows validation error on empty submit', async () => {
    formIsValid.value = false
    const wrapper = mount(LoginPage, { global: { stubs } })
    const form = wrapper.find('form')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Please fix validation errors before submitting.')
  })

  it('does not call login when form validation fails', async () => {
    formIsValid.value = false
    const wrapper = mount(LoginPage, { global: { stubs } })
    const form = wrapper.find('form')
    await form.trigger('submit')
    await flushPromises()
    expect(mockLogin).not.toHaveBeenCalled()
  })

  it('calls auth.login on valid submit', async () => {
    mockLogin.mockResolvedValue(undefined)
    const wrapper = mount(LoginPage, { global: { stubs } })
    const form = wrapper.find('form')
    await form.trigger('submit')
    await flushPromises()
    expect(mockLogin).toHaveBeenCalled()
  })

  it('navigates to discover on successful login', async () => {
    mockLogin.mockResolvedValue(undefined)
    const wrapper = mount(LoginPage, { global: { stubs } })
    const form = wrapper.find('form')
    await form.trigger('submit')
    await flushPromises()
    expect(mockPush).toHaveBeenCalledWith({ name: 'discover' })
  })

  it('shows auth.error banner text', () => {
    errorRef.value = 'Invalid credentials. Please try again.'
    const wrapper = mount(LoginPage, { global: { stubs } })
    expect(wrapper.text()).toContain('Invalid credentials')
  })

  it('navigates to register page on Register button click', async () => {
    const wrapper = mount(LoginPage, { global: { stubs } })
    const buttons = wrapper.findAll('button')
    const registerBtn = buttons.find((b) => b.text().includes('Register'))
    expect(registerBtn).toBeDefined()
    await registerBtn!.trigger('click')
    expect(mockPush).toHaveBeenCalledWith({ name: 'register' })
  })

  it('renders username and password inputs', () => {
    const wrapper = mount(LoginPage, { global: { stubs } })
    const inputs = wrapper.findAll('input')
    expect(inputs.length).toBeGreaterThanOrEqual(2)
  })

  it('submit button is disabled while loading', () => {
    isLoadingRef.value = true
    const wrapper = mount(LoginPage, { global: { stubs } })
    const buttons = wrapper.findAll('button')
    const loginBtn = buttons.find((b) => b.text().includes('Login'))
    expect(loginBtn).toBeDefined()
    expect((loginBtn!.element as HTMLButtonElement).disabled).toBe(true)
  })
})
