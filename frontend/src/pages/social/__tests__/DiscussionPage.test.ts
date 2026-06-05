import { ref } from 'vue'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import DiscussionPage from '../DiscussionPage.vue'

const discussionsRef = ref<Array<Record<string, unknown>>>([])
const discussionsIsLoadingRef = ref(false)
const discussionsErrorRef = ref<string | null>(null)
const repliesRef = ref<Array<Record<string, unknown>>>([])
const repliesIsLoadingRef = ref(false)
const repliesErrorRef = ref<string | null>(null)
const repliesTotalRef = ref(0)
const replyActionStatusRef = ref<'idle' | 'loading' | 'error' | 'success'>('idle')
const createDiscussionStatusRef = ref<'idle' | 'loading' | 'error' | 'success'>('idle')

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

vi.mock('src/boot/axios', () => ({
  api: {
    get: vi.fn().mockResolvedValue({ data: { items: [], total: 0, limit: 50, offset: 0 } }),
    post: vi.fn().mockResolvedValue({ data: { id: 'new-1' } }),
  },
}))

vi.mock('src/stores/social', () => ({
  useSocialStore: () => ({
    discussions: discussionsRef,
    discussionsIsLoading: discussionsIsLoadingRef,
    discussionsError: discussionsErrorRef,
    discussionsTotal: ref(0),
    discussionsOffset: ref(0),
    discussionsHasMore: ref(true),
    replies: repliesRef,
    repliesIsLoading: repliesIsLoadingRef,
    repliesError: repliesErrorRef,
    repliesTotal: repliesTotalRef,
    repliesOffset: ref(0),
    repliesHasMore: ref(true),
    replyActionStatus: replyActionStatusRef,
    createDiscussionStatus: createDiscussionStatusRef,
    fetchDiscussions: vi.fn(),
    resetDiscussions: vi.fn(),
    fetchDiscussionReplies: vi.fn(),
    resetReplies: vi.fn(),
    createDiscussionReply: vi.fn().mockResolvedValue(true),
    createDiscussion: vi.fn().mockResolvedValue({ id: 'new-1' }),
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
  'q-toggle': true,
  'q-form': { template: '<form><slot /></form>' },
  'q-badge': true,
  'q-card': { template: '<div><slot /></div>' },
  'q-card-section': { template: '<div><slot /></div>' },
  'q-list': { template: '<div><slot /></div>' },
  'q-item': true,
  'q-item-section': true,
  'q-item-label': true,
  'q-separator': true,
}

describe('DiscussionPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    discussionsRef.value = []
    discussionsIsLoadingRef.value = false
    discussionsErrorRef.value = null
    repliesRef.value = []
    repliesIsLoadingRef.value = false
    repliesErrorRef.value = null
    repliesTotalRef.value = 0
    replyActionStatusRef.value = 'idle'
    createDiscussionStatusRef.value = 'idle'
  })

  it('renders tab labels', () => {
    const wrapper = mount(DiscussionPage, {
      global: { stubs: baseStubs },
    })

    const html = wrapper.html()
    expect(html).toContain('Threads')
    expect(html).toContain('Create')
  })

  it('renders loading state for discussions', () => {
    discussionsIsLoadingRef.value = true

    const wrapper = mount(DiscussionPage, {
      global: {
        stubs: {
          ...baseStubs,
          'app-page-state': {
            props: ['isLoading', 'loadingLabel'],
            template: '<div><div v-if="isLoading">{{ loadingLabel }}</div><slot v-else /></div>',
          },
        },
      },
    })

    expect(wrapper.html()).toContain('Loading discussions')
  })

  it('renders error state', () => {
    discussionsErrorRef.value = 'Failed to load discussions'

    const wrapper = mount(DiscussionPage, {
      global: {
        stubs: {
          ...baseStubs,
          'app-page-state': {
            props: ['error'],
            template: '<div><div v-if="error">{{ error }}</div><slot v-else /></div>',
          },
        },
      },
    })

    expect(wrapper.html()).toContain('Failed to load discussions')
  })

  it('renders create form', () => {
    const wrapper = mount(DiscussionPage, {
      global: { stubs: baseStubs },
    })

    const html = wrapper.html()
    // Create tab has a form with q-btn "Create Discussion"
    expect(html).toContain('Create Discussion')
  })
})
