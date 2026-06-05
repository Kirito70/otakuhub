import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import ProfilePage from '../ProfilePage.vue'

const mockUser = vi.hoisted(() => ({
  id: 'u1',
  username: 'testuser',
  display_name: 'Test User',
  email: 'test@example.com',
  avatar_url: null,
  bio: 'Hello, I am a test user.',
  timezone: 'UTC',
  is_active: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-06-01T00:00:00Z',
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

vi.mock('src/boot/axios', () => ({
  api: {
    get: vi.fn().mockResolvedValue({ data: {} }),
    patch: vi.fn().mockResolvedValue({ data: mockUser }),
    post: vi.fn().mockResolvedValue({ data: {} }),
  },
}))

vi.mock('src/stores/auth', () => ({
  useAuthStore: () => ({
    user: mockUser,
  }),
}))

const baseStubs = {
  'q-page': { template: '<div><slot /></div>' },
  'q-tabs': { template: '<div><slot /></div>' },
  'q-tab': { template: '<div><slot /></div>' },
  'q-tab-panels': { template: '<div><slot /></div>' },
  'q-tab-panel': { template: '<div><slot /></div>' },
  'q-btn': true,
  'q-input': true,
  'q-select': true,
  'q-toggle': true,
  'q-form': { template: '<form><slot /></form>' },
  'q-badge': true,
  'q-card': { template: '<div><slot /></div>' },
  'q-card-section': { template: '<div><slot /></div>' },
  'q-separator': true,
  'q-banner': true,
  'q-avatar': { template: '<div><slot /></div>' },
  'q-img': true,
  'app-page-state': {
    props: ['isEmpty', 'emptyLabel', 'isLoading', 'error'],
    template: '<div><div v-if="isEmpty">{{ emptyLabel }}</div><div v-if="error">{{ error }}</div><slot v-else /></div>',
  },
}

describe('ProfilePage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders tab labels', () => {
    const wrapper = mount(ProfilePage, {
      global: { stubs: baseStubs },
    })

    const html = wrapper.html()
    expect(html).toContain('Overview')
    expect(html).toContain('Edit Profile')
    expect(html).toContain('Account & Security')
  })

  it('renders user profile in overview tab', () => {
    const wrapper = mount(ProfilePage, {
      global: { stubs: baseStubs },
    })

    const html = wrapper.html()
    expect(html).toContain('testuser')
    expect(html).toContain('Test User')
    expect(html).toContain('test@example.com')
    expect(html).toContain('Hello, I am a test user.')
  })

  it('renders edit form in edit tab', () => {
    const wrapper = mount(ProfilePage, {
      global: { stubs: baseStubs },
    })

    const html = wrapper.html()
    expect(html).toContain('Save Changes')
  })

  it('renders password form in security tab', () => {
    const wrapper = mount(ProfilePage, {
      global: { stubs: baseStubs },
    })

    const html = wrapper.html()
    expect(html).toContain('Change Password')
  })
})
