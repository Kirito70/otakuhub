<template>
  <q-page class="row items-center justify-center q-pa-md">
    <q-card flat bordered style="max-width: 460px; width: 100%">
      <q-card-section>
        <div class="text-h6">Create account</div>
        <div class="text-caption text-grey-7">Join your OtakuHub group</div>
      </q-card-section>
      <q-card-section class="q-gutter-md">
        <q-input v-model="username" label="Username" outlined />
        <q-input v-model="email" label="Email" type="email" outlined />
        <q-input v-model="password" label="Password" type="password" outlined />
        <q-banner v-if="auth.error" dense rounded class="bg-red-1 text-red-9">{{ auth.error }}</q-banner>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Back to login" color="primary" @click="goLogin" />
        <q-btn :loading="auth.isLoading" label="Register" color="primary" @click="onRegister" />
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
const username = ref('')
const email = ref('')
const password = ref('')

async function onRegister(): Promise<void> {
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
