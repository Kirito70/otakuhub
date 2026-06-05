import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import RecommendationsPage from '../RecommendationsPage.vue'

const { acknowledgeMock } = vi.hoisted(() => ({
  acknowledgeMock: vi.fn().mockResolvedValue(true),
}))

const inboxState: Record<string, unknown> = {
  inboxItems: [],
  inboxIsLoading: false,
  inboxError: null,
  inboxTotal: 0,
  inboxOffset: 0,
  inboxHasMore: true,
  sentItems: [],
  sentIsLoading: false,
  sentError: null,
  sentTotal: 0,
  sentOffset: 0,
  sentHasMore: true,
  acknowledgeStatus: {},
  fetchInbox: vi.fn(),
  resetInbox: vi.fn(),
  fetchSent: vi.fn(),
  resetSent: vi.fn(),
  acknowledgeRecommendation: acknowledgeMock,
}

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

vi.mock('src/boot/axios', () => ({
  api: {
    get: vi.fn().mockResolvedValue({ data: { items: [], total: 0, limit: 50, offset: 0 } }),
    patch: vi.fn().mockResolvedValue({ data: {} }),
  },
}))

vi.mock('src/stores/social', () => ({
  useSocialStore: () => inboxState,
}))

const tabStubs = {
  'q-page': { template: '<div><slot /></div>' },
  'q-tabs': { template: '<div><slot /></div>' },
  'q-tab': { template: '<div><slot /></div>' },
  'q-tab-panels': { template: '<div><slot /></div>' },
  'q-tab-panel': { template: '<div><slot /></div>' },
  'q-btn': { template: '<button><slot />{{ label }}</button>', props: ['label', 'loading'] },
  'q-separator': true,
  'recommend-card': { template: '<div class="rec-card"><slot /></div>' },
}

const appPageStateStub = {
  props: ['isLoading', 'error', 'isEmpty', 'loadingLabel', 'emptyLabel'],
  template: `<div>
    <div v-if="isLoading" class="loading-state">{{ loadingLabel }}</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>
    <div v-else-if="isEmpty" class="empty-state">{{ emptyLabel }}</div>
    <slot v-else />
  </div>`,
}

describe('RecommendationsPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    inboxState.inboxItems = []
    inboxState.inboxIsLoading = false
    inboxState.inboxError = null
    inboxState.inboxHasMore = true
    inboxState.sentItems = []
    inboxState.sentIsLoading = false
    inboxState.sentError = null
    inboxState.sentHasMore = true
    inboxState.acknowledgeStatus = {}
    acknowledgeMock.mockReset()
    acknowledgeMock.mockResolvedValue(true)
  })

  it('renders tab labels', () => {
    const wrapper = mount(RecommendationsPage, {
      global: { stubs: { ...tabStubs, 'app-page-state': appPageStateStub } },
    })
    const html = wrapper.html()
    expect(html).toContain('Inbox')
    expect(html).toContain('Sent')
  })

  it('renders inbox loading state', () => {
    inboxState.inboxIsLoading = true
    const wrapper = mount(RecommendationsPage, {
      global: { stubs: { ...tabStubs, 'app-page-state': appPageStateStub } },
    })
    expect(wrapper.html()).toContain('Loading inbox')
  })

  it('renders inbox error state', () => {
    inboxState.inboxError = 'Failed to load inbox'
    const wrapper = mount(RecommendationsPage, {
      global: { stubs: { ...tabStubs, 'app-page-state': appPageStateStub } },
    })
    expect(wrapper.html()).toContain('Failed to load inbox')
  })

  it('renders inbox empty state', () => {
    inboxState.inboxIsLoading = false
    inboxState.inboxError = null
    inboxState.inboxItems = []
    const wrapper = mount(RecommendationsPage, {
      global: { stubs: { ...tabStubs, 'app-page-state': appPageStateStub } },
    })
    expect(wrapper.html()).toContain('No recommendations in your inbox yet')
  })

  it('renders sent empty state', () => {
    inboxState.inboxItems = [{ id: 'r1', media_id: 'm1' }] // populate inbox to avoid empty state there
    inboxState.sentIsLoading = false
    inboxState.sentError = null
    inboxState.sentItems = []
    const wrapper = mount(RecommendationsPage, {
      global: { stubs: { ...tabStubs, 'app-page-state': appPageStateStub } },
    })
    expect(wrapper.html()).toContain("You haven't sent any recommendations yet")
  })

  it('renders inbox items with acknowledge', () => {
    inboxState.inboxIsLoading = false
    inboxState.inboxError = null
    inboxState.inboxItems = [
      { id: 'r1', media_id: 'm1', from_user_id: 'u1', is_acknowledged: false, created_at: '2026-06-05T00:00:00Z' },
    ]
    const wrapper = mount(RecommendationsPage, {
      global: { stubs: { ...tabStubs, 'app-page-state': appPageStateStub } },
    })
    expect(wrapper.html()).toContain('rec-card')
  })

  it('renders sent items', () => {
    inboxState.inboxItems = [{ id: 'r1', media_id: 'm1', from_user_id: 'u1', is_acknowledged: false, created_at: '2026-06-05T00:00:00Z' }]
    inboxState.sentIsLoading = false
    inboxState.sentError = null
    inboxState.sentItems = [
      { id: 'r2', media_id: 'm2', to_user_id: 'u2', is_acknowledged: false, created_at: '2026-06-04T00:00:00Z' },
    ]
    const wrapper = mount(RecommendationsPage, {
      global: { stubs: { ...tabStubs, 'app-page-state': appPageStateStub } },
    })
    // Sent tab renders recommend-card with direction="sent"
    expect(wrapper.html()).toContain('direction="sent"')
  })
})
