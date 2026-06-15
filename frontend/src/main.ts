import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import App from './App.vue'
import { router } from './router'
import { api } from './plugins/axios'
import './css/globals.css'

const app = createApp(App)

// Pinia
const pinia = createPinia()
app.use(pinia)

// Router
app.use(router)

// Provide axios instance globally
app.config.globalProperties.$axios = axios
app.config.globalProperties.$api = api

// Bootstrap: hydrate auth + bootstrap stores
async function bootstrap() {
  const { useAuthStore } = await import('./stores/auth')
  const { useBootstrapStore } = await import('./stores/bootstrap')
  const auth = useAuthStore()
  const bootstrap = useBootstrapStore()

  await auth.hydrateFromStorage()
  await auth.fetchProfile()
  await bootstrap.hydrate()

  // Mount after hydration
  app.mount('#app')
}

bootstrap()
