import { defineComponent, ref } from 'vue'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import NotificationPreferencesPage from '../NotificationPreferencesPage.vue'

const mockPush = vi.fn().mockResolvedValue(undefined)
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
}))

// Shared reactive refs for notifications store mock
const preferencesRef = ref<Record<string, unknown> | null>(null)
const preferencesErrorRef = ref<string | null>(null)
const isSavingRef = ref(false)
const mockFetchPreferences = vi.fn()
const mockSavePreferences = vi.fn()

vi.mock('src/stores/notifications', () => ({
  useNotificationsStore: () => ({
    preferences: preferencesRef,
    preferencesError: preferencesErrorRef,
    isSavingPreferences: isSavingRef,
    fetchPreferences: mockFetchPreferences,
    savePreferences: mockSavePreferences,
  }),
}))

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

const stubs = {
  'q-page': { template: '<div><slot /></div>' },
  'q-btn': {
    props: ['label', 'flat', 'color', 'type', 'loading'],
    template: '<button :disabled="loading" :data-name="label" @click="$emit(\'click\')">{{ label }}</button>',
  },
  'q-banner': {
    props: ['dense'],
    template: '<div class="q-banner"><slot /></div>',
  },
  'q-toggle': {
    props: ['modelValue', 'label'],
    template:
      '<label class="q-toggle"><input type="checkbox" :checked="modelValue" @change="$emit(\'update:modelValue\', $event.target.checked)" /> {{ label }}</label>',
  },
  'q-input': {
    props: ['modelValue', 'outlined', 'label', 'lazyRules', 'rules'],
    template:
      '<input :value="modelValue" :placeholder="label" data-name="pref-input" @input="$emit(\'update:modelValue\', $event.target.value)" />',
  },
  'q-form': QFormStub,
  'q-icon': true,
  'q-spinner': true,
}

describe('NotificationPreferencesPage', () => {
  beforeEach(() => {
    preferencesRef.value = null
    preferencesErrorRef.value = null
    isSavingRef.value = false
    formIsValid.value = true
    mockFetchPreferences.mockReset()
    mockSavePreferences.mockReset()
    mockPush.mockClear()
  })

  it('calls fetchPreferences on mount', () => {
    mockFetchPreferences.mockResolvedValue(undefined)
    mount(NotificationPreferencesPage, { global: { stubs } })
    expect(mockFetchPreferences).toHaveBeenCalled()
  })

  it('populates form from preferences on mount', async () => {
    preferencesRef.value = {
      new_episode: true,
      new_chapter: false,
      friend_activity: true,
      recommendations: false,
      watch_party_invite: true,
      watch_party_reminder: false,
      discord_webhook: 'https://discord.com/api/webhooks/xxx',
      telegram_chat_id: '123456789',
      email_enabled: true,
      push_enabled: false,
    }
    mockFetchPreferences.mockResolvedValue(undefined)
    const wrapper = mount(NotificationPreferencesPage, { global: { stubs } })
    // Wait for async onMounted to complete
    await flushPromises()
    // Form populated - discord webhook value should be in an input
    const inputs = wrapper.findAll('input[data-name="pref-input"]')
    // There should be 2 inputs (discord_webhook + telegram_chat_id)
    expect(inputs.length).toBeGreaterThanOrEqual(2)
  })

  it('shows store error banner when preferencesError is set', () => {
    preferencesErrorRef.value = 'Failed to load notification preferences.'
    const wrapper = mount(NotificationPreferencesPage, { global: { stubs } })
    expect(wrapper.text()).toContain('Failed to load notification preferences.')
  })

  it('shows validation error when form validation fails', async () => {
    formIsValid.value = false
    mockSavePreferences.mockResolvedValue(undefined)
    const wrapper = mount(NotificationPreferencesPage, { global: { stubs } })

    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Please fix the highlighted validation errors before saving.')
    expect(mockSavePreferences).not.toHaveBeenCalled()
  })

  it('calls savePreferences and shows success message on valid submit', async () => {
    mockSavePreferences.mockResolvedValue(undefined)
    const wrapper = mount(NotificationPreferencesPage, { global: { stubs } })

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(mockSavePreferences).toHaveBeenCalled()
    expect(wrapper.text()).toContain('Preferences saved.')
  })

  it('shows form error when savePreferences fails', async () => {
    mockSavePreferences.mockRejectedValue(new Error('Save failed'))
    const wrapper = mount(NotificationPreferencesPage, { global: { stubs } })

    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Could not save preferences right now. Please try again.')
  })

  it('navigates back on Back to Bell click', async () => {
    const wrapper = mount(NotificationPreferencesPage, { global: { stubs } })
    const backBtn = wrapper.findAll('button').find((b) => b.text().includes('Back to Bell'))
    expect(backBtn).toBeDefined()
    await backBtn!.trigger('click')
    expect(mockPush).toHaveBeenCalledWith({ name: 'notifications' })
  })

  it('renders Save Preferences and Reset buttons', () => {
    const wrapper = mount(NotificationPreferencesPage, { global: { stubs } })
    expect(wrapper.text()).toContain('Save Preferences')
    expect(wrapper.text()).toContain('Reset')
  })

  it('renders toggles for notification types', () => {
    const wrapper = mount(NotificationPreferencesPage, { global: { stubs } })
    expect(wrapper.text()).toContain('New episode alerts')
    expect(wrapper.text()).toContain('New chapter alerts')
    expect(wrapper.text()).toContain('Friend activity')
    expect(wrapper.text()).toContain('Recommendations')
    expect(wrapper.text()).toContain('Watch party invites')
    expect(wrapper.text()).toContain('Watch party reminders')
    expect(wrapper.text()).toContain('Enable email delivery')
    expect(wrapper.text()).toContain('Enable push delivery')
  })
})
