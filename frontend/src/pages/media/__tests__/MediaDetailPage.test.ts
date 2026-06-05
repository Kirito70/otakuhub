import { ref } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import MediaDetailPage from '../MediaDetailPage.vue'

const mediaRef = ref<Record<string, unknown> | null>(null)
const isLoadingRef = ref(false)
const errorRef = ref<string | null>(null)
const mockFetchById = vi.fn()

vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { id: 'abc' } }),
}))

vi.mock('src/composables/useMediaDetail', () => ({
  useMediaDetail: () => ({
    data: mediaRef,
    isLoading: isLoadingRef,
    error: errorRef,
    fetchById: mockFetchById,
  }),
}))

const stubs = {
  'q-page': { template: '<div><slot /></div>' },
  'q-banner': {
    props: ['rounded'],
    template: '<div class="q-banner" data-name="error-banner"><slot /></div>',
  },
  'q-spinner': { template: '<div class="q-spinner" />' },
  'q-card': { template: '<div class="q-card"><slot /></div>' },
  'q-img': {
    props: ['src', 'ratio'],
    template: '<div class="q-img" data-name="media-image"><slot name="error"><div class="no-cover">No Cover</div></slot></div>',
  },
  'q-card-section': { template: '<div class="q-card-section"><slot /></div>' },
  'q-btn': {
    props: ['label', 'color'],
    template: '<button :data-name="label" @click="$emit(\'click\')">{{ label }}</button>',
  },
  'q-separator': true,
  'add-to-list-sheet': {
    props: ['modelValue', 'mediaId', 'title'],
    template: '<div class="add-to-list-sheet" v-if="modelValue">AddToListSheet for {{ title }}</div>',
  },
}

describe('MediaDetailPage', () => {
  beforeEach(() => {
    mediaRef.value = null
    isLoadingRef.value = false
    errorRef.value = null
    mockFetchById.mockReset()
  })

  it('renders loading spinner while fetching', () => {
    isLoadingRef.value = true
    const wrapper = mount(MediaDetailPage, { global: { stubs } })
    expect(wrapper.find('.q-spinner').exists()).toBe(true)
  })

  it('renders error banner when fetch fails', () => {
    errorRef.value = 'Failed to load media detail.'
    const wrapper = mount(MediaDetailPage, { global: { stubs } })
    const banner = wrapper.find('[data-name="error-banner"]')
    expect(banner.exists()).toBe(true)
    expect(banner.text()).toContain('Failed to load media detail.')
  })

  it('renders media detail card with metadata', () => {
    mediaRef.value = {
      id: '1',
      title_romaji: 'Attack on Titan',
      title_english: 'Attack on Titan',
      title_native: '進撃の巨人',
      media_type: 'anime',
      format: 'TV',
      status: 'finished',
      average_score: 9.0,
      synopsis: 'A story about giants.',
      cover_image_large: 'http://example.com/cover.jpg',
      banner_image: 'http://example.com/banner.jpg',
    }
    const wrapper = mount(MediaDetailPage, { global: { stubs } })
    expect(wrapper.text()).toContain('Attack on Titan')
    expect(wrapper.text()).toContain('進撃の巨人')
    expect(wrapper.text()).toContain('anime')
    expect(wrapper.text()).toContain('TV')
    expect(wrapper.text()).toContain('finished')
    expect(wrapper.text()).toContain('9')
    expect(wrapper.text()).toContain('A story about giants.')
    // Banner image should be present (stub renders q-img)
    expect(wrapper.findAll('[data-name="media-image"]').length).toBeGreaterThanOrEqual(2)
  })

  it('shows title_romaji as fallback when title_english is null', () => {
    mediaRef.value = {
      id: '2',
      title_romaji: 'One Piece',
      title_english: null,
      synopsis: null,
      cover_image_large: null,
    }
    const wrapper = mount(MediaDetailPage, { global: { stubs } })
    expect(wrapper.text()).toContain('One Piece')
    // Should show fallback text for synopsis
    expect(wrapper.text()).toContain('No synopsis available.')
  })

  it('shows No Cover fallback when cover image is missing', () => {
    mediaRef.value = {
      id: '3',
      title_romaji: 'Bleach',
      cover_image_large: null,
    }
    const wrapper = mount(MediaDetailPage, { global: { stubs } })
    expect(wrapper.text()).toContain('No Cover')
    // No banner image since banner_image is not set
    const images = wrapper.findAll('[data-name="media-image"]')
    expect(images.length).toBe(1)
  })

  it('shows Add to List sheet on button click', async () => {
    mediaRef.value = {
      id: '42',
      title_romaji: 'Naruto',
      cover_image_large: 'http://example.com/cover.jpg',
    }
    const wrapper = mount(MediaDetailPage, { global: { stubs } })
    // Add to List not visible initially
    expect(wrapper.find('.add-to-list-sheet').exists()).toBe(false)

    // Click the "Add to List" button
    const addBtn = wrapper.find('button[data-name="Add to List"]')
    expect(addBtn.exists()).toBe(true)
    await addBtn.trigger('click')

    // Sheet should now be visible
    expect(wrapper.find('.add-to-list-sheet').exists()).toBe(true)
    expect(wrapper.text()).toContain('Naruto')
  })

  it('renders N/A for missing fields', () => {
    mediaRef.value = {
      id: '4',
      title_romaji: 'Test',
      media_type: null,
      format: null,
      status: null,
      average_score: null,
    }
    const wrapper = mount(MediaDetailPage, { global: { stubs } })
    expect(wrapper.text()).toContain('Unknown')
    expect(wrapper.text()).toContain('N/A')
  })
})
