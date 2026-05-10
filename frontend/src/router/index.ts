import { route } from 'quasar/wrappers'
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router'
import axios from 'axios'

import { useAuthStore } from 'src/stores/auth'
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

  Router.beforeEach((to) => {
    const auth = useAuthStore(store)

    // Unified app bootstrap flow via backend routing context endpoint.
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    return (async () => {
      try {
        const bootstrapResponse = await axios.get<{
          site_status: 'up' | 'degraded'
          setup_required?: boolean
          logged_in_user?: { id: string; username: string; is_admin: boolean }
        }>(
          `${process.env.API_BASE_URL}/api/v1/setup/bootstrap`,
          {
            timeout: 5000,
            headers: auth.accessToken
              ? {
                  Authorization: `Bearer ${auth.accessToken}`,
                }
              : undefined,
          },
        )
        const setupRequired = bootstrapResponse.data.setup_required === true
        const loggedInUser = bootstrapResponse.data.logged_in_user

        const guardDecision = resolveAccessGuard({
          toName: typeof to.name === 'string' ? to.name : null,
          requiresAuth: to.meta.requiresAuth === true,
          setupRequired,
          loggedInUser: Boolean(loggedInUser),
        })
        if (guardDecision !== true) {
          return guardDecision
        }
      } catch {
        // If setup status cannot be fetched, continue with regular auth guard.
      }

      return resolveAccessGuard({
        toName: typeof to.name === 'string' ? to.name : null,
        requiresAuth: to.meta.requiresAuth === true,
        setupRequired: false,
        loggedInUser: auth.isAuthenticated,
      })
    })()
  })

  return Router
})
