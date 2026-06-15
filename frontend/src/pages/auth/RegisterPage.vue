<template>
  <div class="flex items-center justify-center min-h-screen bg-[#0a0a0a] px-4">
    <div class="w-full max-w-[460px] bg-[#111] border border-[#222] rounded-xl p-6">
      <div class="mb-6">
        <h1 class="text-xl font-semibold text-white">Create account</h1>
        <p class="text-sm text-gray-400 mt-1">Join your OtakuHub group</p>
      </div>

      <form @submit.prevent="onRegister" novalidate>
        <div class="space-y-4">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-300 mb-1">Username</label>
            <input
              id="username"
              v-model="username"
              type="text"
              autocomplete="username"
              class="w-full px-3 py-2.5 bg-[#1a1a1a] border border-[#333] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
              :class="{ 'border-red-500 focus:ring-red-500': fieldErrors.username }"
              placeholder="Your username"
              @input="clearFieldError('username')"
              @blur="validateField('username')"
            />
            <p v-if="fieldErrors.username" class="text-red-400 text-xs mt-1">{{ fieldErrors.username }}</p>
          </div>

          <div>
            <label for="email" class="block text-sm font-medium text-gray-300 mb-1">Email</label>
            <input
              id="email"
              v-model="email"
              type="email"
              autocomplete="email"
              class="w-full px-3 py-2.5 bg-[#1a1a1a] border border-[#333] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
              :class="{ 'border-red-500 focus:ring-red-500': fieldErrors.email }"
              placeholder="you@example.com"
              @input="clearFieldError('email')"
              @blur="validateField('email')"
            />
            <p v-if="fieldErrors.email" class="text-red-400 text-xs mt-1">{{ fieldErrors.email }}</p>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-300 mb-1">Password</label>
            <input
              id="password"
              v-model="password"
              type="password"
              autocomplete="new-password"
              class="w-full px-3 py-2.5 bg-[#1a1a1a] border border-[#333] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
              :class="{ 'border-red-500 focus:ring-red-500': fieldErrors.password }"
              placeholder="At least 8 characters"
              @input="clearFieldError('password')"
              @blur="validateField('password')"
            />
            <p v-if="fieldErrors.password" class="text-red-400 text-xs mt-1">{{ fieldErrors.password }}</p>
          </div>

          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-300 mb-1">Confirm password</label>
            <input
              id="confirmPassword"
              v-model="confirmPassword"
              type="password"
              autocomplete="new-password"
              class="w-full px-3 py-2.5 bg-[#1a1a1a] border border-[#333] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
              :class="{ 'border-red-500 focus:ring-red-500': fieldErrors.confirmPassword }"
              placeholder="Repeat your password"
              @input="clearFieldError('confirmPassword')"
              @blur="validateField('confirmPassword')"
            />
            <p v-if="fieldErrors.confirmPassword" class="text-red-400 text-xs mt-1">{{ fieldErrors.confirmPassword }}</p>
          </div>

          <div v-if="submitError || auth.error" class="bg-red-900/30 border border-red-800 rounded-lg px-4 py-3 text-sm text-red-400">
            {{ submitError || auth.error }}
          </div>
        </div>

        <div class="flex items-center justify-between mt-6 gap-3">
          <button
            type="button"
            class="text-sm text-gray-400 hover:text-gray-300 transition"
            @click="goLogin"
          >
            Back to login
          </button>
          <button
            type="submit"
            :disabled="auth.isLoading"
            class="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition"
          >
            <span v-if="auth.isLoading" class="inline-flex items-center gap-2">
              <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Registering...
            </span>
            <span v-else>Register</span>
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

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const submitError = ref<string | null>(null)

const fieldErrors = reactive<Record<string, string | null>>({
  username: null,
  email: null,
  password: null,
  confirmPassword: null,
})

const registerSchema = z
  .object({
    username: z
      .string()
      .min(1, 'Username is required')
      .min(3, 'Username must be at least 3 characters'),
    email: z
      .string()
      .min(1, 'Email is required')
      .regex(/.+@.+\..+/, 'Enter a valid email address'),
    password: z
      .string()
      .min(1, 'Password is required')
      .min(8, 'Password must be at least 8 characters'),
    confirmPassword: z.string().min(1, 'Please confirm your password'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  })

function validateField(field: string): void {
  const payload: Record<string, string> = {
    username: username.value,
    email: email.value,
    password: password.value,
    confirmPassword: confirmPassword.value,
  }

  const result = registerSchema.safeParse(payload)
  if (!result.success) {
    const fieldIssue = result.error.issues.find((i) => i.path[0] === field)
    fieldErrors[field] = fieldIssue?.message ?? null
  } else {
    fieldErrors[field] = null
  }
}

function clearFieldError(field: string): void {
  fieldErrors[field] = null
}

function validateAll(): boolean {
  const payload = {
    username: username.value,
    email: email.value,
    password: password.value,
    confirmPassword: confirmPassword.value,
  }

  const result = registerSchema.safeParse(payload)
  if (!result.success) {
    for (const issue of result.error.issues) {
      const field = issue.path[0] as string
      if (!fieldErrors[field]) {
        fieldErrors[field] = issue.message
      }
    }
    return false
  }

  for (const key of Object.keys(fieldErrors)) {
    fieldErrors[key] = null
  }
  return true
}

async function onRegister(): Promise<void> {
  submitError.value = null

  if (!validateAll()) {
    submitError.value = 'Please fix validation errors before submitting.'
    return
  }

  try {
    await auth.register({
      username: username.value,
      email: email.value,
      password: password.value,
    })
    await router.push({ name: 'discover' })
  } catch {
    submitError.value = auth.error ?? 'Registration failed. Please try again.'
  }
}

async function goLogin(): Promise<void> {
  await router.push({ name: 'login' })
}
</script>
