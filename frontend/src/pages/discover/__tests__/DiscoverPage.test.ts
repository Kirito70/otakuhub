import { ref } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import DiscoverPage from '../DiscoverPage.vue'

const itemsRef = ref<Array<{ id: string }>>([])
const totalRef = ref(0)
const isLoadingRef = ref(false)
const errorRef = ref<string | null>(null)

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn().mockResolvedValue(undefined) }),
}))

vi.mock('src/composables/useMediaSearch', () => ({
  useMediaSearch: () => ({
    data: itemsRef,
    total: totalRef,
    isLoading: isLoadingRef,
    error: errorRef,
    search: vi.fn(),
  }),
}))

describe('DiscoverPage', () => {
  beforeEach(() => {
    itemsRef.value = []
    totalRef.value = 0
    isLoadingRef.value = false
    errorRef.value = null
  })

  it('renders standardized empty state when no results exist', () => {
    const wrapper = mount(DiscoverPage, {
      global: {
        stubs: {
          'q-page': { template: '<div><slot /></div>' },
          'q-input': true,
          'q-icon': true,
          'q-select': true,
          'q-btn': true,
          'q-banner': true,
          'q-card': true,
          'q-img': true,
          'q-card-section': true,
          'app-page-state': {
            props: ['isEmpty', 'emptyLabel'],
            template: '<div><div v-if="isEmpty">{{ emptyLabel }}</div><slot /></div>',
          },
        },
      },
    })

    expect(wrapper.text()).toContain('No results to display yet.')
  })
})
