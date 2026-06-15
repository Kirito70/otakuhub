import {
  createRouter,
  createWebHistory,
} from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { useBootstrapStore } from '@/stores/bootstrap'
import { resolveAccessGuard } from './guard'
import routes from './routes'

const router = createRouter({
  scrollBehavior: () => ({ left: 0, top: 0 }),
  routes,
  history: createWebHistory(),
})

/*
 * Unified route guard.
 *
 * Reads bootstrap + auth stores synchronously — no HTTP calls.
 * The bootstrap store is hydrated once during app boot (main.ts).
 * The auth store is hydrated from localStorage during boot.
 *
 * If for any reason bootstrap hasn't finished hydrating yet,
 * navigation is allowed through (a subsequent redirect will correct it).
 */
router.beforeEach((to) => {
  const auth = useAuthStore()
  const bootstrap = useBootstrapStore()

  if (!bootstrap.isHydrated) {
    // Bootstrap not ready yet — allow navigation.
    // The first protected-route request will naturally redirect
    // once the app is fully initialised.
    return true
  }

  return resolveAccessGuard({
    toName: typeof to.name === 'string' ? to.name : null,
    requiresAuth: to.meta.requiresAuth === true,
    setupRequired: bootstrap.setupRequired,
    loggedInUser: auth.isAuthenticated,
  })
})

export { router }
