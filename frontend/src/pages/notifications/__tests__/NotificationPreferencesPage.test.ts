import { defineComponent, ref } from 'vue'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import NotificationPreferencesPage from '../NotificationPreferencesPage.vue'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

const formIsValid = ref(true)

vi.mock('src/boot/axios', () => ({
  api: {
    get: vi.fn().mockResolvedValue({
      data: {
        user_id: 'u1',
        new_episode: true,
        new_chapter: true,
        friend_activity: true,
        recommendations: true,
        watch_party_invite: true,
        watch_party_reminder: true,
        discord_webhook: null,
        telegram_chat_id: null,
        email_enabled: false,
        push_enabled: false,
        updated_at: '2026-05-06T00:00:00Z',
      },
    }),
    patch: vi.fn().mockResolvedValue({
      data: {
        user_id: 'u1',
        new_episode: true,
        new_chapter: true,
        friend_activity: true,
        recommendations: true,
        watch_party_invite: true,
        watch_party_reminder: true,
        discord_webhook: null,
        telegram_chat_id: null,
        email_enabled: false,
        push_enabled: false,
        updated_at: '2026-05-06T00:00:00Z',
      },
    }),
  },
}))

const QFormStub = defineComponent({
  name: 'QForm',
  emits: ['submit'],
  methods: {
    validate(): boolean {
      return formIsValid.value
    },
  },
  template: '<form @submit.prevent="$emit(\'submit\')"><slot /></form>',
})

describe('NotificationPreferencesPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('shows validation message when form validation fails', async () => {
    formIsValid.value = false
    const wrapper = mount(NotificationPreferencesPage, {
      global: {
        stubs: {
          'q-page': { template: '<div><slot /></div>' },
          'q-btn': { template: '<button @click="$emit(\'click\')"><slot />{{ label }}</button>', props: ['label'] },
          'q-banner': { template: '<div><slot /></div>' },
          'q-toggle': true,
          'q-input': true,
          'q-form': QFormStub,
        },
      },
    })

    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Please fix the highlighted validation errors before saving.')
  })

  it('shows success message when save succeeds', async () => {
    formIsValid.value = true
    const wrapper = mount(NotificationPreferencesPage, {
      global: {
        stubs: {
          'q-page': { template: '<div><slot /></div>' },
          'q-btn': { template: '<button @click="$emit(\'click\')"><slot />{{ label }}</button>', props: ['label'] },
          'q-banner': { template: '<div><slot /></div>' },
          'q-toggle': true,
          'q-input': true,
          'q-form': QFormStub,
        },
      },
    })

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    const axiosModule = await import('src/boot/axios')
    expect(axiosModule.api.patch).toHaveBeenCalledWith('/api/v1/notifications/preferences', expect.any(Object))
  })
})
