import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import ImportListPage from '../ImportListPage.vue'
import { api } from 'src/boot/axios'

vi.mock('vue-router', () => ({
  useRoute: () => ({ query: {} }),
}))

vi.mock('src/boot/axios', () => ({
  api: {
    post: vi.fn(),
  },
}))

const stubs = {
  'q-page': { template: '<div><slot /></div>' },
  'q-card': { template: '<div class="q-card"><slot /></div>' },
  'q-card-section': { template: '<div class="q-card-section"><slot /></div>' },
  'q-card-actions': { template: '<div class="q-card-actions"><slot /></div>' },
  'q-tabs': { template: '<div class="q-tabs"><slot /></div>' },
  'q-tab': true,
  'q-route-tab': {
    props: ['name', 'label', 'to', 'exact'],
    template: '<div class="q-route-tab" data-name="route-tab">{{ label }}</div>',
  },
  'q-separator': true,
  'q-input': {
    props: ['modelValue', 'outlined', 'label'],
    template:
      '<input :value="modelValue" :placeholder="label" data-name="import-username" @input="$emit(\'update:modelValue\', $event.target.value)" />',
  },
  'q-toggle': {
    props: ['modelValue', 'label'],
    template:
      '<label class="q-toggle"><input type="checkbox" :checked="modelValue" @change="$emit(\'update:modelValue\', $event.target.checked)" /> {{ label }}</label>',
  },
  'q-banner': {
    props: ['rounded'],
    template: '<div class="q-banner"><slot /></div>',
  },
  'q-btn': {
    props: ['label', 'loading', 'color'],
    template: '<button :disabled="loading" data-name="import-btn" @click="$emit(\'click\')">{{ label }}</button>',
  },
}

describe('ImportListPage', () => {
  beforeEach(() => {
    vi.mocked(api.post).mockReset()
  })

  it('renders heading and description', () => {
    const wrapper = mount(ImportListPage, { global: { stubs } })
    expect(wrapper.text()).toContain('Import Lists')
    expect(wrapper.text()).toContain('Import your AniList or MyAnimeList list')
  })

  it('renders provider tabs (AniList, MyAnimeList)', () => {
    const wrapper = mount(ImportListPage, { global: { stubs } })
    const tabs = wrapper.findAll('[data-name="route-tab"]')
    expect(tabs.length).toBe(2)
    expect(tabs[0].text()).toContain('AniList')
    expect(tabs[1].text()).toContain('MyAnimeList')
  })

  it('renders username input and overwrite toggle', () => {
    const wrapper = mount(ImportListPage, { global: { stubs } })
    expect(wrapper.find('input[data-name="import-username"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Overwrite existing entries')
  })

  it('calls API with correct endpoint and payload on import', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: { job_id: 'job-123' } })
    const wrapper = mount(ImportListPage, { global: { stubs } })

    const input = wrapper.find('input[data-name="import-username"]')
    await input.setValue('otaku_fan')

    const importBtn = wrapper.find('button[data-name="import-btn"]')
    await importBtn.trigger('click')
    await flushPromises()

    expect(vi.mocked(api.post)).toHaveBeenCalledWith(
      '/api/v1/sync/import/anilist',
      expect.objectContaining({
        username: 'otaku_fan',
        overwrite_existing: false,
      }),
    )
  })

  it('shows success message after import starts', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: { job_id: 'job-123' } })
    const wrapper = mount(ImportListPage, { global: { stubs } })

    const importBtn = wrapper.find('button[data-name="import-btn"]')
    await importBtn.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Import started successfully')
    expect(wrapper.text()).toContain('job-123')
  })

  it('shows error banner when import fails', async () => {
    vi.mocked(api.post).mockRejectedValue(new Error('API error'))
    const wrapper = mount(ImportListPage, { global: { stubs } })

    const importBtn = wrapper.find('button[data-name="import-btn"]')
    await importBtn.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Failed to start import.')
  })

  it('disables import button while loading', async () => {
    let deferredResolve!: (value: unknown) => void
    vi.mocked(api.post).mockReturnValue(new Promise((resolve) => { deferredResolve = resolve }))

    const wrapper = mount(ImportListPage, { global: { stubs } })
    const importBtn = wrapper.find('button[data-name="import-btn"]')
    await importBtn.trigger('click')
    await wrapper.vm.$nextTick()

    expect(importBtn.attributes('disabled')).toBe('')

    deferredResolve({ data: { job_id: 'done' } })
    await flushPromises()
  })

  it('uses default anilist endpoint', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: { job_id: 'test' } })
    const wrapper = mount(ImportListPage, { global: { stubs } })

    const importBtn = wrapper.find('button[data-name="import-btn"]')
    await importBtn.trigger('click')
    await flushPromises()

    expect(vi.mocked(api.post)).toHaveBeenCalledWith(
      '/api/v1/sync/import/anilist',
      expect.any(Object),
    )
  })
})
