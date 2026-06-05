import { ref } from 'vue'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import RecommendationsPage from '../RecommendationsPage.vue'

const inboxItemsRef = ref<Array<Record<string, unknown>>>([])
const inboxIsLoadingRef = ref(false)
const inboxErrorRef = ref<string | null>(null)
const sentItemsRef = ref<Array<Record<string, unknown>>>([])
const sentIsLoadingRef = ref(false)
const sentErrorRef = ref<string | null>(null)
const acknowledgeStatusRef = ref<Record<string, string>>({})

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
  useSocialStore: () => ({
    inboxItems: inboxItemsRef,
    inboxIsLoading: inboxIsLoadingRef,
    inboxError: inboxErrorRef,
    inboxTotal: ref(0),
    inboxOffset: ref(0),
    inboxHasMore: ref(true),
    sentItems: sentItemsRef,
    sentIsLoading: sentIsLoadingRef,
    sentError: sentErrorRef,
    sentTotal: ref(0),
    sentOffset: ref(0),
    sentHasMore: ref(true),
    acknowledgeStatus: acknowledgeStatusRef,
    fetchInbox: vi.fn(),
    resetInbox: vi.fn(),
    fetchSent: vi.fn(),
    resetSent: vi.fn(),
    acknowledgeRecommendation: vi.fn().mockResolvedValue(true),
  }),
}))

const tabStubs = {
  'q-page': { template: '<div><slot /></div>' },
  'q-tabs': { template: '<div><slot /></div>' },
  'q-tab': { template: '<div><slot /></div>' },
  'q-tab-panels': { template: '<div><slot /></div>' },
  'q-tab-panel': { template: '<div><slot /></div>' },
  'q-btn': true,
  'q-separator': true,
  'recommend-card': { template: '<div><slot /></div>' },
}

describe('RecommendationsPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    inboxItemsRef.value = []
    inboxIsLoadingRef.value = false
    inboxErrorRef.value = null
    sentItemsRef.value = []
    sentIsLoadingRef.value = false
    sentErrorRef.value = null
    acknowledgeStatusRef.value = {}
  })

  it('renders tab labels', () => {
    const wrapper = mount(RecommendationsPage, {
      global: { stubs: tabStubs },
    })

    const html = wrapper.html()
    expect(html).toContain('Inbox')
    expect(html).toContain('Sent')
  })

  it('renders loading state', () => {
    inboxIsLoadingRef.value = true

    const wrapper = mount(RecommendationsPage, {
      global: {
        stubs: {
          ...tabStubs,
          'app-page-state': {
            props: ['isLoading', 'loadingLabel'],
            template: '<div><div v-if="isLoading">{{ loadingLabel }}</div><slot v-else /></div>',
          },
        },
      },
    })

    expect(wrapper.html()).toContain('Loading inbox')
  })

  it('renders error state', () => {
    inboxErrorRef.value = 'Failed to load inbox'

    const wrapper = mount(RecommendationsPage, {
      global: {
        stubs: {
          ...tabStubs,
          'app-page-state': {
            props: ['error'],
            template: '<div><div v-if="error">{{ error }}</div><slot v-else /></div>',
          },
        },
      },
    })

    expect(wrapper.html()).toContain('Failed to load inbox')
  })
})
