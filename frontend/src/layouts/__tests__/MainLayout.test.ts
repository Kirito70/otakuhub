import { nextTick, reactive } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import { useAuthStore } from 'src/stores/auth'
import MainLayout from '../MainLayout.vue'

const pushMock = vi.fn().mockResolvedValue(undefined)
const useRouteMock = vi.fn(() => ({ name: 'discover' }))

const screenState = reactive({
  lt: { md: false },
  gt: { sm: true },
  md: true,
})

vi.mock('quasar', () => ({
  useQuasar: () => ({ screen: screenState }),
}))

vi.mock('vue-router', async () => {
  const actual = await vi.importActual<typeof import('vue-router')>('vue-router')
  return {
    ...actual,
    useRouter: () => ({ push: pushMock }),
    useRoute: () => useRouteMock(),
    RouterView: { template: '<div data-testid="router-view" />' },
  }
})

vi.mock('src/composables/useTheme', () => ({
  useTheme: () => ({
    isDark: false,
    toggleDarkMode: vi.fn(),
  }),
}))

const baseStubs = {
  'q-layout': { template: '<div><slot /></div>' },
  'q-header': { template: '<div><slot /></div>' },
  'q-toolbar': { template: '<div><slot /></div>' },
  'q-toolbar-title': { template: '<div><slot /></div>' },
  'q-btn': { template: '<button :aria-label="ariaLabel"><slot />{{ label }}</button>', props: ['ariaLabel', 'label', 'icon'] },
  'q-drawer': {
    template: '<aside :data-model-value="modelValue"><slot /></aside>',
    props: ['modelValue'],
  },
  'q-list': { template: '<div><slot /></div>' },
  'q-item': { template: '<div @click="$emit(\'click\')"><slot /></div>' },
  'q-item-section': { template: '<div><slot /></div>' },
  'q-item-label': { template: '<span><slot /></span>' },
  'q-icon': true,
  'q-separator': { template: '<hr />' },
  'q-avatar': { template: '<span><slot /></span>' },
  'q-menu': { template: '<div v-if="modelValue"><slot /></div>', props: ['modelValue'] },
  'q-page-container': { template: '<div><slot /></div>' },
  'q-footer': { template: '<div><slot /></div>' },
  'q-tabs': { template: '<div><slot /></div>' },
  'q-tab': { template: '<button @click="$emit(\'click\')"><slot /></button>' },
  'q-route-tab': { template: '<button><slot /></button>' },
  RouterView: { template: '<div data-testid="router-view" />' },
}

function mountLayout() {
  const pinia = createPinia()
  // Register the auth store on this pinia instance (already active from beforeEach)
  useAuthStore(pinia)
  return mount(MainLayout, {
    global: {
      plugins: [pinia],
      stubs: baseStubs,
    },
  })
}

describe('MainLayout', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    pushMock.mockClear()
    useRouteMock.mockClear()
    screenState.lt.md = false
    screenState.gt.sm = true
    screenState.md = true
  })

  it('shows a menu trigger on desktop so drawer can always be reopened', () => {
    const wrapper = mountLayout()

    const menuButton = wrapper.find('button[aria-label="Menu"]')
    expect(menuButton.exists()).toBe(true)
  })

  it('keeps desktop drawer open after sidebar navigation click', async () => {
    const wrapper = mountLayout()

    const drawer = wrapper.find('aside')
    expect(drawer.attributes('data-model-value')).toBe('true')

    const discoverNavItem = wrapper.find('[data-testid="nav-discover"]')
    expect(discoverNavItem.exists()).toBe(true)

    await discoverNavItem.trigger('click')
    await nextTick()

    expect(pushMock).toHaveBeenCalled()
    expect(drawer.attributes('data-model-value')).toBe('true')
  })

  it('syncs drawer open state when crossing mobile breakpoint', async () => {
    const wrapper = mountLayout()

    const drawer = wrapper.find('aside')
    expect(drawer.attributes('data-model-value')).toBe('true')

    screenState.lt.md = true
    await nextTick()

    expect(drawer.attributes('data-model-value')).toBe('false')
  })

  it('shows login nav item when user is not authenticated', () => {
    const wrapper = mountLayout()

    const loginNav = wrapper.find('[data-testid="nav-login"]')
    expect(loginNav.exists()).toBe(true)
  })
})
