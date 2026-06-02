import { boot } from 'quasar/wrappers'

import { useAuthStore } from 'src/stores/auth'
import { useBootstrapStore } from 'src/stores/bootstrap'

/**
 * App-init boot file.
 *
 * 1. Hydrate auth store from secure storage (reads persisted tokens).
 * 2. Fetch bootstrap context once (setup_required, site_status).
 *
 * The route guard reads the bootstrap store synchronously — no API calls
 * on every navigation.
 */
export default boot(async ({ store }) => {
  const auth = useAuthStore(store)
  const bootstrap = useBootstrapStore(store)

  await auth.hydrateFromStorage()
  await bootstrap.hydrate()
})
