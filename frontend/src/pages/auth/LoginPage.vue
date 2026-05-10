<template>
  <q-page class="row items-center justify-center q-pa-md">
    <q-card flat bordered style="max-width: 420px; width: 100%">
      <q-card-section>
        <div class="text-h6">Login</div>
        <div class="text-caption text-grey-7">Sign in to continue</div>
      </q-card-section>
      <q-form ref="loginFormRef" @submit="onLogin">
        <q-card-section class="q-gutter-md">
          <q-input v-model="usernameOrEmail" label="Username or Email" outlined lazy-rules :rules="usernameRules" />
          <q-input v-model="password" label="Password" type="password" outlined lazy-rules :rules="passwordRules" />
          <q-banner v-if="submitError || auth.error" dense rounded class="bg-red-1 text-red-9">{{ submitError || auth.error }}</q-banner>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Register" color="primary" @click="goRegister" />
          <q-btn :loading="auth.isLoading" label="Login" color="primary" type="submit" />
        </q-card-actions>
      </q-form>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import type { QForm } from 'quasar'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useValidationRules } from 'src/composables/useValidationRules'
import { useAuthStore } from 'src/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const loginFormRef = ref<QForm | null>(null)
const usernameOrEmail = ref('')
const password = ref('')
const submitError = ref<string | null>(null)
const rules = useValidationRules()
const usernameRules = [rules.required('Username or Email')]
const passwordRules = [rules.required('Password'), rules.minLength('Password', 8)]

async function onLogin(): Promise<void> {
  submitError.value = null
  const isValid = await loginFormRef.value?.validate()
  if (!isValid) {
    submitError.value = 'Please fix validation errors before submitting.'
    return
  }

  await auth.login({ username: usernameOrEmail.value, password: password.value })
  await router.push({ name: 'discover' })
}

async function goRegister(): Promise<void> {
  await router.push({ name: 'register' })
}
</script>
