import { nextTick, reactive } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

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

describe('MainLayout', () => {
  beforeEach(() => {
    pushMock.mockClear()
    useRouteMock.mockClear()
    screenState.lt.md = false
    screenState.gt.sm = true
    screenState.md = true
  })

  it('shows a menu trigger on desktop so drawer can always be reopened', () => {
    const wrapper = mount(MainLayout, {
      global: {
        mocks: {
          $q: {
            screen: screenState,
          },
        },
        stubs: {
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
          'q-icon': true,
          'q-page-container': { template: '<div><slot /></div>' },
          'q-footer': { template: '<div><slot /></div>' },
          'q-tabs': { template: '<div><slot /></div>' },
          'q-tab': { template: '<button @click="$emit(\'click\')"><slot /></button>' },
          'q-route-tab': { template: '<button><slot /></button>' },
          RouterView: { template: '<div data-testid="router-view" />' },
        },
      },
    })

    const menuButton = wrapper.find('button[aria-label="Menu"]')
    expect(menuButton.exists()).toBe(true)
  })

  it('keeps desktop drawer open after sidebar navigation click', async () => {
    const wrapper = mount(MainLayout, {
      global: {
        mocks: {
          $q: {
            screen: screenState,
          },
        },
        stubs: {
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
          'q-icon': true,
          'q-page-container': { template: '<div><slot /></div>' },
          'q-footer': { template: '<div><slot /></div>' },
          'q-tabs': { template: '<div><slot /></div>' },
          'q-tab': { template: '<button @click="$emit(\'click\')"><slot /></button>' },
          'q-route-tab': { template: '<button><slot /></button>' },
          RouterView: { template: '<div data-testid="router-view" />' },
        },
      },
    })

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
    const wrapper = mount(MainLayout, {
      global: {
        mocks: {
          $q: {
            screen: screenState,
          },
        },
        stubs: {
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
          'q-icon': true,
          'q-page-container': { template: '<div><slot /></div>' },
          'q-footer': { template: '<div><slot /></div>' },
          'q-tabs': { template: '<div><slot /></div>' },
          'q-tab': { template: '<button @click="$emit(\'click\')"><slot /></button>' },
          'q-route-tab': { template: '<button><slot /></button>' },
          RouterView: { template: '<div data-testid="router-view" />' },
        },
      },
    })

    const drawer = wrapper.find('aside')
    expect(drawer.attributes('data-model-value')).toBe('true')

    screenState.lt.md = true
    await nextTick()

    expect(drawer.attributes('data-model-value')).toBe('false')
  })
})
