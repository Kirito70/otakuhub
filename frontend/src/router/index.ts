import { route } from 'quasar/wrappers'
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router'

import { useAuthStore } from 'src/stores/auth'
import { useBootstrapStore } from 'src/stores/bootstrap'
import { resolveAccessGuard } from './guard'
import routes from './routes'

export default route(function ({ store }) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === 'history'
      ? createWebHistory
      : createWebHashHistory

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,
    history: createHistory(process.env.VUE_ROUTER_BASE),
  })

  /*
   * Unified route guard.
   *
   * Reads bootstrap + auth stores synchronously — no HTTP calls.
   * The bootstrap store is hydrated once during app boot (boot/bootstrap.ts).
   * The auth store is hydrated from localStorage during boot.
   *
   * If for any reason bootstrap hasn't finished hydrating yet,
   * navigation is allowed through (a subsequent redirect will correct it).
   */
  Router.beforeEach((to) => {
    const auth = useAuthStore(store)
    const bootstrap = useBootstrapStore(store)

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

  return Router
})
