import { ref } from 'vue'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import FeedPage from '../FeedPage.vue'

const feedItemsRef = ref<Array<Record<string, unknown>>>([])
const feedIsLoadingRef = ref(false)
const feedErrorRef = ref<string | null>(null)

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

vi.mock('src/boot/axios', () => ({
  api: {
    get: vi.fn().mockResolvedValue({ data: { items: [], total: 0, limit: 50, offset: 0 } }),
  },
}))

vi.mock('src/stores/social', () => ({
  useSocialStore: () => ({
    feedItems: feedItemsRef,
    feedIsLoading: feedIsLoadingRef,
    feedError: feedErrorRef,
    feedTotal: ref(0),
    feedOffset: ref(0),
    feedHasMore: ref(true),
    fetchFeed: vi.fn(),
    resetFeed: vi.fn(),
  }),
}))

// Shared stubs that render all panel content regardless of active state
const tabStubs = {
  'q-page': { template: '<div><slot /></div>' },
  'q-tabs': { template: '<div><slot /></div>' },
  'q-tab': { template: '<div><slot /></div>' },
  'q-tab-panels': { template: '<div><slot /></div>' },
  'q-tab-panel': { template: '<div><slot /></div>' },
  'q-list': { template: '<div><slot /></div>' },
  'q-item': true,
  'q-btn': true,
  'q-separator': true,
  'q-banner': true,
  'activity-feed-item': { template: '<div><slot /></div>' },
}

describe('FeedPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    feedItemsRef.value = []
    feedIsLoadingRef.value = false
    feedErrorRef.value = null
  })

  it('renders tab labels', () => {
    const wrapper = mount(FeedPage, {
      global: {
        stubs: tabStubs,
      },
    })

    const html = wrapper.html()
    expect(html).toContain('Group Activity')
    expect(html).toContain('My Activity')
  })

  it('renders loading state', () => {
    feedIsLoadingRef.value = true

    const wrapper = mount(FeedPage, {
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

    expect(wrapper.html()).toContain('Loading feed')
  })

  it('renders error state', () => {
    feedErrorRef.value = 'Failed to load feed'

    const wrapper = mount(FeedPage, {
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

    expect(wrapper.html()).toContain('Failed to load feed')
  })
})
