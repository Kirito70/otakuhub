<template>
  <div class="min-h-screen bg-[#0a0a0a] flex items-center justify-center px-4">
    <div class="w-full max-w-md bg-[#111111] border border-[#1f2937] rounded-lg p-6">
      <h1 class="text-xl font-semibold text-white">Initial Setup</h1>
      <p class="text-sm text-gray-400 mt-1">Create the first super admin account</p>

      <form class="mt-6 space-y-4" @submit.prevent="onSubmit">
        <div>
          <label for="username" class="block text-sm font-medium text-gray-300 mb-1">Username</label>
          <input
            id="username"
            v-model="username"
            type="text"
            class="w-full rounded-md bg-[#0a0a0a] border border-[#1f2937] px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Username"
            :class="{ 'border-red-500': fieldErrors.username }"
          />
          <p v-if="fieldErrors.username" class="mt-1 text-xs text-red-400">{{ fieldErrors.username }}</p>
        </div>

        <div>
          <label for="email" class="block text-sm font-medium text-gray-300 mb-1">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            class="w-full rounded-md bg-[#0a0a0a] border border-[#1f2937] px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Email"
            :class="{ 'border-red-500': fieldErrors.email }"
          />
          <p v-if="fieldErrors.email" class="mt-1 text-xs text-red-400">{{ fieldErrors.email }}</p>
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-gray-300 mb-1">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="w-full rounded-md bg-[#0a0a0a] border border-[#1f2937] px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Password"
            :class="{ 'border-red-500': fieldErrors.password }"
          />
          <p v-if="fieldErrors.password" class="mt-1 text-xs text-red-400">{{ fieldErrors.password }}</p>
        </div>

        <div>
          <label for="confirmPassword" class="block text-sm font-medium text-gray-300 mb-1">Confirm Password</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            class="w-full rounded-md bg-[#0a0a0a] border border-[#1f2937] px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Confirm Password"
            :class="{ 'border-red-500': fieldErrors.confirmPassword }"
          />
          <p v-if="fieldErrors.confirmPassword" class="mt-1 text-xs text-red-400">{{ fieldErrors.confirmPassword }}</p>
        </div>

        <div v-if="error" class="rounded-md bg-red-900/50 border border-red-800 px-3 py-2 text-sm text-red-300">{{ error }}</div>
        <div v-if="success" class="rounded-md bg-green-900/50 border border-green-800 px-3 py-2 text-sm text-green-300">Setup complete. You can now sign in.</div>

        <button
          type="submit"
          :disabled="isLoading"
          class="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-[#111111] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          :class="{ 'opacity-50 cursor-not-allowed': isLoading }"
        >
          <span v-if="isLoading" class="inline-flex items-center gap-2">
            <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Creating...
          </span>
          <span v-else>Create Super Admin</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import axios from 'axios'
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { z } from 'zod'

import { useBootstrapStore } from 'src/stores/bootstrap'

const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')

const isLoading = ref(false)
const error = ref<string | null>(null)
const success = ref(false)
const fieldErrors = reactive<Record<string, string>>({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const formSchema = computed(() =>
  z
    .object({
      username: z.string().min(1, 'Username is required').min(3, 'Username must be at least 3 characters'),
      email: z.string().min(1, 'Email is required').email('Enter a valid email address'),
      password: z.string().min(1, 'Password is required').min(8, 'Password must be at least 8 characters'),
      confirmPassword: z.string().min(1, 'Confirm Password is required'),
    })
    .refine((data) => data.password === data.confirmPassword, {
      message: 'Passwords do not match',
      path: ['confirmPassword'],
    }),
)

function validate(): boolean {
  fieldErrors.username = ''
  fieldErrors.email = ''
  fieldErrors.password = ''
  fieldErrors.confirmPassword = ''

  const result = formSchema.value.safeParse({
    username: username.value,
    email: email.value,
    password: password.value,
    confirmPassword: confirmPassword.value,
  })

  if (!result.success) {
    for (const issue of result.error.issues) {
      const field = issue.path[0] as keyof typeof fieldErrors
      if (fieldErrors[field] === '') {
        fieldErrors[field] = issue.message
      }
    }
    return false
  }

  return true
}

async function onSubmit(): Promise<void> {
  error.value = null
  success.value = false

  if (!validate()) {
    error.value = 'Please fix validation errors before submitting.'
    return
  }

  isLoading.value = true
  try {
    await axios.post(`${process.env.API_BASE_URL}/api/v1/setup/bootstrap-admin`, {
      username: username.value,
      email: email.value,
      password: password.value,
    })
    success.value = true
    const bootstrap = useBootstrapStore()
    await bootstrap.refresh()
    await router.push({ name: 'login' })
  } catch {
    error.value = 'Setup failed. It may already be completed.'
  } finally {
    isLoading.value = false
  }
}
</script>
