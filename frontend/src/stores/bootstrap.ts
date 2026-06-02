import axios from 'axios'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export interface BootstrapContext {
  site_status: 'up' | 'degraded'
  setup_required?: boolean | null
  logged_in_user?: { id: string; username: string; is_admin: boolean } | null
}

export const useBootstrapStore = defineStore('bootstrap', () => {
  const context = ref<BootstrapContext | null>(null)
  const isHydrated = ref(false)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const setupRequired = computed(() => context.value?.setup_required === true)
  const siteUp = computed(() => context.value?.site_status === 'up')

  /**
   * Fetch bootstrap context from the backend.
   * Called once during app boot. Also called after setup-complete or login/logout
   * if the cached token changed the set of permissions needed.
   *
   * Never rejects — always sets `isHydrated = true`, even on failure,
   * so the route guard never hangs waiting.
   */
  async function hydrate(): Promise<void> {
    if (isLoading.value) return
    isLoading.value = true
    error.value = null
    try {
      const response = await axios.get<BootstrapContext>(
        `${process.env.API_BASE_URL}/api/v1/setup/bootstrap`,
        { timeout: 5000 },
      )
      context.value = response.data
    } catch (e) {
      error.value = 'Failed to fetch bootstrap context'
      // Degraded fallback — allows routing to still function.
      context.value = { site_status: 'degraded' }
    } finally {
      isHydrated.value = true
      isLoading.value = false
    }
  }

  /** Force a fresh fetch (e.g. after setup completes). */
  async function refresh(): Promise<void> {
    context.value = null
    isHydrated.value = false
    await hydrate()
  }

  return {
    context,
    isHydrated,
    isLoading,
    error,
    setupRequired,
    siteUp,
    hydrate,
    refresh,
  }
})
