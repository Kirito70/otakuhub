<template>
  <q-page class="row items-center justify-center q-pa-md">
    <q-card flat bordered style="max-width: 520px; width: 100%">
      <q-card-section>
        <div class="text-h6">Initial Setup</div>
        <div class="text-caption text-grey-7">Create the first super admin account</div>
      </q-card-section>

      <q-card-section>
        <q-form ref="setupFormRef" class="q-gutter-md" @submit="onSubmit">
          <q-input
            v-model="username"
            outlined
            label="Username"
            lazy-rules
            :rules="usernameRules"
          />
          <q-input
            v-model="email"
            outlined
            label="Email"
            type="email"
            lazy-rules
            :rules="emailRules"
          />
          <q-input
            v-model="password"
            outlined
            label="Password"
            type="password"
            lazy-rules
            :rules="passwordRules"
          />
          <q-input
            v-model="confirmPassword"
            outlined
            label="Confirm Password"
            type="password"
            lazy-rules
            :rules="confirmPasswordRules"
          />

          <q-banner v-if="error" class="bg-negative text-white" dense>{{ error }}</q-banner>
          <q-banner v-if="success" class="bg-positive text-white" dense>Setup complete. You can now sign in.</q-banner>

          <q-btn
            color="primary"
            type="submit"
            label="Create Super Admin"
            :loading="isLoading"
          />
        </q-form>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import axios from 'axios'
import type { QForm } from 'quasar'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useValidationRules } from 'src/composables/useValidationRules'

const router = useRouter()
const setupFormRef = ref<QForm | null>(null)

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')

const isLoading = ref(false)
const error = ref<string | null>(null)
const success = ref(false)
const rules = useValidationRules()

const usernameRules = [rules.required('Username'), rules.minLength('Username', 3)]
const emailRules = [rules.required('Email'), rules.email('Email')]
const passwordRules = [rules.required('Password'), rules.minLength('Password', 8)]
const confirmPasswordRules = [
  rules.required('Confirm Password'),
  rules.matches('Confirm Password', () => password.value, 'Passwords do not match'),
]

async function onSubmit(): Promise<void> {
  error.value = null
  success.value = false

  const isValid = await setupFormRef.value?.validate()
  if (!isValid) {
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
    await router.push({ name: 'login' })
  } catch {
    error.value = 'Setup failed. It may already be completed.'
  } finally {
    isLoading.value = false
  }
}
</script>
