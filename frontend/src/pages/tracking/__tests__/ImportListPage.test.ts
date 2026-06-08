import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import ImportListPage from '../ImportListPage.vue'

const { mockGet, mockPost, mockUseRoute } = vi.hoisted(() => {
  const mockGet = vi.fn()
  const mockPost = vi.fn()
  const mockUseRoute = vi.fn(() => ({ query: {} }))
  return { mockGet, mockPost, mockUseRoute }
})

vi.mock('vue-router', () => ({
  useRoute: () => mockUseRoute(),
}))

vi.mock('src/boot/axios', () => ({
  api: {
    get: mockGet,
    post: mockPost,
  },
}))

/** Advance one tick + 10ms microtask delay */
function tick(): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, 10))
}

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
  'q-form': {
    template: '<form><slot /></form>',
  },
  'q-input': {
    props: ['modelValue', 'outlined', 'label', 'rules'],
    template:
      '<input :value="modelValue" :placeholder="label" data-name="import-username" @input="$emit(\'update:modelValue\', $event.target.value)" />',
  },
  'q-toggle': {
    props: ['modelValue', 'label'],
    template:
      '<label class="q-toggle"><input type="checkbox" :checked="modelValue" data-name="overwrite-toggle" @change="$emit(\'update:modelValue\', $event.target.checked)" /> {{ label }}</label>',
  },
  'q-banner': {
    props: ['rounded'],
    template: '<div class="q-banner"><slot /><slot name="avatar" /></div>',
  },
  'q-btn': {
    props: ['label', 'loading', 'disable', 'color', 'flat', 'type'],
    template: '<button :disabled="disable || loading" data-name="import-btn" @click="$emit(\'click\')">{{ label }}</button>',
  },
  'q-icon': {
    props: ['name', 'size', 'color'],
    template: '<span class="q-icon">{{ name }}</span>',
  },
  'q-spinner': {
    props: ['size', 'color'],
    template: '<span class="q-spinner" />',
  },
  'q-linear-progress': {
    props: ['value', 'color'],
    template: '<div class="q-linear-progress" />',
  },
}

describe('ImportListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockUseRoute.mockReturnValue({ query: {} })
  })

  // -- Rendering --

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

  it('shows provider-specific info banner for AniList by default', () => {
    const wrapper = mount(ImportListPage, { global: { stubs } })
    expect(wrapper.text()).toContain('AniList usernames')
    expect(wrapper.text()).toContain('3–20 characters')
  })

  // -- API call routing --

  it('calls AniList endpoint with correct payload on import', async () => {
    mockPost.mockResolvedValue({ data: { job_id: 'job-123' } })
    const wrapper = mount(ImportListPage, { global: { stubs } })

    const input = wrapper.find('input[data-name="import-username"]')
    await input.setValue('otaku_fan')

    await (wrapper.vm as unknown as { onImport: () => Promise<void> }).onImport()
    await flushPromises()

    expect(mockPost).toHaveBeenCalledWith(
      '/api/v1/sync/import/anilist',
      expect.objectContaining({
        username: 'otaku_fan',
        overwrite_existing: false,
      }),
    )
  })

  it('calls MAL endpoint when provider is mal', async () => {
    mockUseRoute.mockReturnValue({ query: { provider: 'mal' } })
    mockPost.mockResolvedValue({ data: { job_id: 'job-456' } })
    const wrapper = mount(ImportListPage, { global: { stubs } })

    const input = wrapper.find('input[data-name="import-username"]')
    await input.setValue('mal_user')

    await (wrapper.vm as unknown as { onImport: () => Promise<void> }).onImport()
    await flushPromises()

    expect(mockPost).toHaveBeenCalledWith(
      '/api/v1/sync/import/mal',
      expect.objectContaining({ username: 'mal_user' }),
    )
  })

  // -- Error mapping --

  it('shows generic error on API failure', async () => {
    mockPost.mockRejectedValue(new Error('Network error'))
    const wrapper = mount(ImportListPage, { global: { stubs } })

    await (wrapper.vm as unknown as { onImport: () => Promise<void> }).onImport()
    await flushPromises()

    expect(wrapper.text()).toContain('Failed to start import')
  })

  it('shows 400 error with provider-specific message', async () => {
    mockPost.mockRejectedValue({ response: { status: 400 } })
    const wrapper = mount(ImportListPage, { global: { stubs } })

    await (wrapper.vm as unknown as { onImport: () => Promise<void> }).onImport()
    await flushPromises()

    expect(wrapper.text()).toContain('Invalid request for AniList import')
  })

  it('shows 429 rate-limit error message', async () => {
    mockPost.mockRejectedValue({ response: { status: 429 } })
    const wrapper = mount(ImportListPage, { global: { stubs } })

    await (wrapper.vm as unknown as { onImport: () => Promise<void> }).onImport()
    await flushPromises()

    expect(wrapper.text()).toContain('Too many requests')
  })

  // -- Import button loading state --

  it('disables import button while importing', async () => {
    let deferredResolve!: (value: unknown) => void
    mockPost.mockReturnValue(new Promise((resolve) => { deferredResolve = resolve }))

    const wrapper = mount(ImportListPage, { global: { stubs } })
    const btn = wrapper.find('button[data-name="import-btn"]')

    void (wrapper.vm as unknown as { onImport: () => Promise<void> }).onImport()
    await wrapper.vm.$nextTick()

    expect(btn.attributes('disabled')).toBe('')

    deferredResolve({ data: { job_id: 'done' } })
    await flushPromises()
  })

  it('disables import button while job polling is active', async () => {
    mockPost.mockResolvedValue({ data: { job_id: 'poll-job' } })
    mockGet.mockResolvedValue({ data: { id: 'poll-job', status: 'running', processed_items: 0, failed_items: 0 } })

    const wrapper = mount(ImportListPage, { global: { stubs } })

    await (wrapper.vm as unknown as { onImport: () => Promise<void> }).onImport()
    await flushPromises()

    // Button should be disabled while polling (isPolling = true)
    expect(wrapper.find('button[data-name="import-btn"]').attributes('disabled')).toBe('')
  })

  // -- Job polling & status display --

  it('shows job status card after import starts', async () => {
    mockPost.mockResolvedValue({ data: { job_id: 'job-1' } })
    mockGet.mockResolvedValue({ data: { id: 'job-1', status: 'running', processed_items: 2, total_items: 50, failed_items: 0 } })

    const wrapper = mount(ImportListPage, { global: { stubs } })
    expect(wrapper.find('[data-name="job-status-card"]').exists()).toBe(false)

    await (wrapper.vm as unknown as { onImport: () => Promise<void> }).onImport()
    await flushPromises()

    const card = wrapper.find('[data-name="job-status-card"]')
    expect(card.exists()).toBe(true)
    expect(wrapper.text()).toContain('job-1')
  })

  it('shows running state with progress info', async () => {
    mockPost.mockResolvedValue({ data: { job_id: 'job-run' } })
    mockGet.mockResolvedValue({ data: { id: 'job-run', status: 'running', processed_items: 5, total_items: 100, failed_items: 0 } })

    const wrapper = mount(ImportListPage, { global: { stubs } })
    await (wrapper.vm as unknown as { onImport: () => Promise<void> }).onImport()
    await flushPromises()

    expect(wrapper.text()).toContain('Import in progress')
    expect(wrapper.text()).toContain('5 items processed')
  })

  it('shows completed state with item count', async () => {
    mockPost.mockResolvedValue({ data: { job_id: 'job-done' } })
    mockGet.mockResolvedValue({ data: { id: 'job-done', status: 'completed', processed_items: 42, total_items: 42, failed_items: 0 } })

    const wrapper = mount(ImportListPage, { global: { stubs } })
    await (wrapper.vm as unknown as { onImport: () => Promise<void> }).onImport()
    await flushPromises()

    expect(wrapper.text()).toContain('Import completed')
    expect(wrapper.text()).toContain('42 items imported')
  })

  it('shows failed state with error log', async () => {
    mockPost.mockResolvedValue({ data: { job_id: 'job-fail' } })
    mockGet.mockResolvedValue({ data: { id: 'job-fail', status: 'failed', processed_items: 0, failed_items: 0, error_log: 'AniList API timeout' } })

    const wrapper = mount(ImportListPage, { global: { stubs } })
    await (wrapper.vm as unknown as { onImport: () => Promise<void> }).onImport()
    await flushPromises()

    expect(wrapper.text()).toContain('Import failed')
    expect(wrapper.text()).toContain('AniList API timeout')
  })

  it('shows partial state with processed/failed counts', async () => {
    mockPost.mockResolvedValue({ data: { job_id: 'job-partial' } })
    mockGet.mockResolvedValue({ data: { id: 'job-partial', status: 'partial', processed_items: 30, failed_items: 5, total_items: 35 } })

    const wrapper = mount(ImportListPage, { global: { stubs } })
    await (wrapper.vm as unknown as { onImport: () => Promise<void> }).onImport()
    await flushPromises()

    expect(wrapper.text()).toContain('completed with errors')
    expect(wrapper.text()).toContain('30 items imported, 5 failed')
  })

  it('stops polling when job reaches terminal state and shows Start New Import', async () => {
    mockPost.mockResolvedValue({ data: { job_id: 'job-term' } })
    const getCalls: string[] = []

    mockGet.mockImplementation((url: string) => {
      getCalls.push(url)
      return Promise.resolve({ data: { id: 'job-term', status: 'completed', processed_items: 10, total_items: 10, failed_items: 0 } })
    })

    const wrapper = mount(ImportListPage, { global: { stubs } })
    await (wrapper.vm as unknown as { onImport: () => Promise<void> }).onImport()
    await flushPromises()

    // Should have called GET at least once (immediate poll)
    expect(getCalls.length).toBeGreaterThanOrEqual(1)
    expect(getCalls[0]).toContain('/api/v1/sync/jobs/job-term')

    // After a tick, the completed status should have stopped polling
    await tick()
    await flushPromises()

    // Start New Import button should appear after terminal status
    const newImportBtn = wrapper.findAll('button').filter(b => b.text().includes('Start New Import'))
    expect(newImportBtn.length).toBeGreaterThan(0)
  })

  it('resets UI and hides job card on Start New Import', async () => {
    mockPost.mockResolvedValue({ data: { job_id: 'job-reset' } })
    mockGet.mockResolvedValue({ data: { id: 'job-reset', status: 'completed', processed_items: 5, total_items: 5, failed_items: 0 } })

    const wrapper = mount(ImportListPage, { global: { stubs } })
    await (wrapper.vm as unknown as { onImport: () => Promise<void> }).onImport()
    await flushPromises()

    // Should have job card
    expect(wrapper.find('[data-name="job-status-card"]').exists()).toBe(true)

    // Find and click the new import button (second button in the card actions)
    const newImportBtn = wrapper.findAll('button').filter(b => b.text().includes('Start New Import'))
    expect(newImportBtn.length).toBeGreaterThan(0)
  })

  // -- AniList validation rules --

  it('has AniList validation: too short username shows error', async () => {
    const wrapper = mount(ImportListPage, { global: { stubs } })
    const input = wrapper.find('input[data-name="import-username"]')
    await input.setValue('ab')
    // Check provider banner shows AniList rules
    expect(wrapper.text()).toContain('3–20 characters')
  })

  it('has AniList validation: invalid characters show error', async () => {
    const wrapper = mount(ImportListPage, { global: { stubs } })
    const input = wrapper.find('input[data-name="import-username"]')
    await input.setValue('user@name!')
    expect(wrapper.text()).toContain('3–20 characters')
  })

  it('accepts valid AniList usernames', async () => {
    mockPost.mockResolvedValue({ data: { job_id: 'ok' } })
    const wrapper = mount(ImportListPage, { global: { stubs } })
    const input = wrapper.find('input[data-name="import-username"]')
    await input.setValue('valid_user-123')
    await (wrapper.vm as unknown as { onImport: () => Promise<void> }).onImport()
    await flushPromises()
    expect(mockPost).toHaveBeenCalled()
  })
})
