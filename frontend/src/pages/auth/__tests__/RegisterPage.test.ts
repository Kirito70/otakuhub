import { defineComponent, ref } from 'vue'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import RegisterPage from '../RegisterPage.vue'

// Shared reactive refs for auth store mock
const isLoadingRef = ref(false)
const errorRef = ref<string | null>(null)
const mockRegister = vi.fn()

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
    register: mockRegister,
  }),
}))

describe('RegisterPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    formIsValid.value = true
    isLoadingRef.value = false
    errorRef.value = null
    mockRegister.mockReset()
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

  it('renders register form with heading', () => {
    const wrapper = mount(RegisterPage, { global: { stubs } })
    expect(wrapper.text()).toContain('Create account')
    expect(wrapper.text()).toContain('Join your OtakuHub group')
  })

  it('shows validation error on empty submit', async () => {
    formIsValid.value = false
    const wrapper = mount(RegisterPage, { global: { stubs } })
    const form = wrapper.find('form')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Please fix validation errors before submitting.')
  })

  it('does not call register when form validation fails', async () => {
    formIsValid.value = false
    const wrapper = mount(RegisterPage, { global: { stubs } })
    const form = wrapper.find('form')
    await form.trigger('submit')
    await flushPromises()
    expect(mockRegister).not.toHaveBeenCalled()
  })

  it('calls auth.register on valid submit', async () => {
    mockRegister.mockResolvedValue(undefined)
    const wrapper = mount(RegisterPage, { global: { stubs } })
    const form = wrapper.find('form')
    await form.trigger('submit')
    await flushPromises()
    expect(mockRegister).toHaveBeenCalled()
  })

  it('navigates to discover on successful registration', async () => {
    mockRegister.mockResolvedValue(undefined)
    const wrapper = mount(RegisterPage, { global: { stubs } })
    const form = wrapper.find('form')
    await form.trigger('submit')
    await flushPromises()
    expect(mockPush).toHaveBeenCalledWith({ name: 'discover' })
  })

  it('shows auth error banner when registration fails', () => {
    errorRef.value = 'Registration failed. Please check your inputs.'
    const wrapper = mount(RegisterPage, { global: { stubs } })
    expect(wrapper.text()).toContain('Registration failed')
  })

  it('navigates to login page on Back to login click', async () => {
    const wrapper = mount(RegisterPage, { global: { stubs } })
    const buttons = wrapper.findAll('button')
    const backBtn = buttons.find((b) => b.text().includes('Back to login'))
    expect(backBtn).toBeDefined()
    await backBtn!.trigger('click')
    expect(mockPush).toHaveBeenCalledWith({ name: 'login' })
  })

  it('renders username, email, and password inputs', () => {
    const wrapper = mount(RegisterPage, { global: { stubs } })
    const inputs = wrapper.findAll('input')
    expect(inputs.length).toBeGreaterThanOrEqual(3)
  })

  it('submit button is disabled while loading', () => {
    isLoadingRef.value = true
    const wrapper = mount(RegisterPage, { global: { stubs } })
    const buttons = wrapper.findAll('button')
    const registerBtn = buttons.find((b) => b.text().includes('Register'))
    expect(registerBtn).toBeDefined()
    expect((registerBtn!.element as HTMLButtonElement).disabled).toBe(true)
  })
})
