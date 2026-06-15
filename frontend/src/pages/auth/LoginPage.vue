<template>
  <div class="min-h-screen bg-[#0a0a0a] flex items-center justify-center px-4">
    <div class="w-full max-w-[420px] bg-[#121212] border border-[#1f1f1f] rounded-lg p-6">
      <div class="mb-6">
        <h1 class="text-xl font-semibold text-white m-0">Login</h1>
        <p class="text-sm text-gray-400 mt-1 m-0">Sign in to continue</p>
      </div>

      <form @submit.prevent="onLogin" novalidate>
        <div class="space-y-4">
          <div>
            <label for="usernameOrEmail" class="block text-sm font-medium text-gray-300 mb-1">Username or Email</label>
            <input
              id="usernameOrEmail"
              v-model="usernameOrEmail"
              type="text"
              autocomplete="username"
              class="w-full px-3 py-2.5 bg-[#1a1a1a] border border-[#2a2a2a] rounded-md text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent transition-colors"
              :class="{ 'border-red-500 focus:ring-red-500': fieldErrors.usernameOrEmail }"
              placeholder="Username or Email"
              @input="clearFieldError('usernameOrEmail')"
            />
            <p v-if="fieldErrors.usernameOrEmail" class="text-xs text-red-400 mt-1">{{ fieldErrors.usernameOrEmail }}</p>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-300 mb-1">Password</label>
            <input
              id="password"
              v-model="password"
              type="password"
              autocomplete="current-password"
              class="w-full px-3 py-2.5 bg-[#1a1a1a] border border-[#2a2a2a] rounded-md text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent transition-colors"
              :class="{ 'border-red-500 focus:ring-red-500': fieldErrors.password }"
              placeholder="Password"
              @input="clearFieldError('password')"
            />
            <p v-if="fieldErrors.password" class="text-xs text-red-400 mt-1">{{ fieldErrors.password }}</p>
          </div>

          <div v-if="formError" class="bg-red-900/30 border border-red-800 rounded-md px-3 py-2">
            <p class="text-sm text-red-400 m-0">{{ formError }}</p>
          </div>
        </div>

        <div class="flex items-center justify-between mt-6 gap-3">
          <button
            type="button"
            class="text-sm text-blue-400 hover:text-blue-300 bg-transparent border-none cursor-pointer px-0 py-1 transition-colors"
            @click="goRegister"
          >
            Register
          </button>
          <button
            type="submit"
            :disabled="auth.isLoading"
            class="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 disabled:cursor-not-allowed text-white text-sm font-medium rounded-md border-none cursor-pointer transition-colors flex items-center gap-2"
          >
            <svg v-if="auth.isLoading" class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span>{{ auth.isLoading ? 'Signing in...' : 'Login' }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { z } from 'zod'

import { useAuthStore } from 'src/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const usernameOrEmail = ref('')
const password = ref('')
const formError = ref<string | null>(null)
const fieldErrors = reactive<Record<string, string>>({})

const loginSchema = z.object({
  usernameOrEmail: z.string().min(1, 'Username or Email is required'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

function clearFieldError(field: string): void {
  delete fieldErrors[field]
}

async function onLogin(): Promise<void> {
  formError.value = null
  Object.keys(fieldErrors).forEach((k) => delete fieldErrors[k])

  const result = loginSchema.safeParse({
    usernameOrEmail: usernameOrEmail.value,
    password: password.value,
  })

  if (!result.success) {
    for (const issue of result.error.issues) {
      const path = issue.path[0] as string
      if (!fieldErrors[path]) {
        fieldErrors[path] = issue.message
      }
    }
    formError.value = 'Please fix validation errors before submitting.'
    return
  }

  try {
    await auth.login({ username: usernameOrEmail.value, password: password.value })
    await router.push({ name: 'discover' })
  } catch {
    formError.value = auth.error ?? 'Invalid credentials. Please try again.'
  }
}

async function goRegister(): Promise<void> {
  await router.push({ name: 'register' })
}
</script>
