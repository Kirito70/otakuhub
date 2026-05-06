<template>
  <q-page class="row items-center justify-center q-pa-md">
    <q-card flat bordered style="max-width: 420px; width: 100%">
      <q-card-section>
        <div class="text-h6">Login</div>
        <div class="text-caption text-grey-7">Sign in to continue</div>
      </q-card-section>
      <q-card-section class="q-gutter-md">
        <q-input v-model="usernameOrEmail" label="Username or Email" outlined />
        <q-input v-model="password" label="Password" type="password" outlined />
        <q-banner v-if="auth.error" dense rounded class="bg-red-1 text-red-9">{{ auth.error }}</q-banner>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Register" color="primary" @click="goRegister" />
        <q-btn :loading="auth.isLoading" label="Login" color="primary" @click="onLogin" />
      </q-card-actions>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from 'src/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const usernameOrEmail = ref('')
const password = ref('')

async function onLogin(): Promise<void> {
  await auth.login({ username: usernameOrEmail.value, password: password.value })
  await router.push({ name: 'discover' })
}

async function goRegister(): Promise<void> {
  await router.push({ name: 'register' })
}
</script>
