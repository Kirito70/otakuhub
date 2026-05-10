<template>
  <q-page class="row items-center justify-center q-pa-md">
    <q-card flat bordered style="max-width: 460px; width: 100%">
      <q-card-section>
        <div class="text-h6">Create account</div>
        <div class="text-caption text-grey-7">Join your OtakuHub group</div>
      </q-card-section>
      <q-form ref="registerFormRef" @submit="onRegister">
        <q-card-section class="q-gutter-md">
          <q-input v-model="username" label="Username" outlined lazy-rules :rules="usernameRules" />
          <q-input v-model="email" label="Email" type="email" outlined lazy-rules :rules="emailRules" />
          <q-input v-model="password" label="Password" type="password" outlined lazy-rules :rules="passwordRules" />
          <q-banner v-if="submitError || auth.error" dense rounded class="bg-red-1 text-red-9">{{ submitError || auth.error }}</q-banner>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Back to login" color="primary" @click="goLogin" />
          <q-btn :loading="auth.isLoading" label="Register" color="primary" type="submit" />
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
const registerFormRef = ref<QForm | null>(null)
const username = ref('')
const email = ref('')
const password = ref('')
const submitError = ref<string | null>(null)
const rules = useValidationRules()
const usernameRules = [rules.required('Username'), rules.minLength('Username', 3)]
const emailRules = [rules.required('Email'), rules.email('Email')]
const passwordRules = [rules.required('Password'), rules.minLength('Password', 8)]

async function onRegister(): Promise<void> {
  submitError.value = null
  const isValid = await registerFormRef.value?.validate()
  if (!isValid) {
    submitError.value = 'Please fix validation errors before submitting.'
    return
  }

  await auth.register({
    username: username.value,
    email: email.value,
    password: password.value,
  })

  await router.push({ name: 'discover' })
}

async function goLogin(): Promise<void> {
  await router.push({ name: 'login' })
}
</script>
