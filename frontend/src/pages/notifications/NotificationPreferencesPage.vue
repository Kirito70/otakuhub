<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h5">Notification Preferences</div>
      <q-btn flat color="primary" label="Back to Bell" @click="goBack" />
    </div>

    <q-banner v-if="formError" class="bg-negative text-white q-mb-md" dense>{{ formError }}</q-banner>
    <q-banner v-if="saveSuccess" class="bg-positive text-white q-mb-md" dense>Preferences saved.</q-banner>
    <q-banner v-if="notificationsStore.preferencesError" class="bg-negative text-white q-mb-md" dense>
      {{ notificationsStore.preferencesError }}
    </q-banner>

    <q-form ref="preferencesFormRef" class="q-gutter-md" @submit="onSubmit">
      <q-toggle v-model="form.new_episode" label="New episode alerts" />
      <q-toggle v-model="form.new_chapter" label="New chapter alerts" />
      <q-toggle v-model="form.friend_activity" label="Friend activity" />
      <q-toggle v-model="form.recommendations" label="Recommendations" />
      <q-toggle v-model="form.watch_party_invite" label="Watch party invites" />
      <q-toggle v-model="form.watch_party_reminder" label="Watch party reminders" />

      <q-input
        v-model="form.discord_webhook"
        outlined
        label="Discord webhook (optional)"
        lazy-rules
        :rules="[validateDiscordWebhook]"
      />

      <q-input
        v-model="form.telegram_chat_id"
        outlined
        label="Telegram chat ID (optional)"
        lazy-rules
        :rules="[validateTelegramChatId]"
      />

      <q-toggle v-model="form.email_enabled" label="Enable email delivery" />
      <q-toggle v-model="form.push_enabled" label="Enable push delivery" />

      <div class="row q-gutter-sm">
        <q-btn color="primary" label="Save Preferences" type="submit" :loading="notificationsStore.isSavingPreferences" />
        <q-btn flat color="primary" label="Reset" @click="loadFromStore" />
      </div>
    </q-form>
  </q-page>
</template>

<script setup lang="ts">
import type { QForm } from 'quasar'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useNotificationsStore } from 'src/stores/notifications'

const router = useRouter()
const notificationsStore = useNotificationsStore()
const preferencesFormRef = ref<QForm | null>(null)
const saveSuccess = ref(false)
const formError = ref<string | null>(null)

const form = ref({
  new_episode: true,
  new_chapter: true,
  friend_activity: true,
  recommendations: true,
  watch_party_invite: true,
  watch_party_reminder: true,
  discord_webhook: '',
  telegram_chat_id: '',
  email_enabled: false,
  push_enabled: false,
})

function validateDiscordWebhook(value: string): true | string {
  if (!value) {
    return true
  }
  const isValid = /^(https?:\/\/|discord:\/\/).+/.test(value)
  return isValid || 'Discord webhook must start with https://, http://, or discord://'
}

function validateTelegramChatId(value: string): true | string {
  if (!value) {
    return true
  }
  const isValid = /^-?\d+$/.test(value)
  return isValid || 'Telegram chat ID must be numeric'
}

function loadFromStore(): void {
  if (!notificationsStore.preferences) {
    return
  }
  const prefs = notificationsStore.preferences
  form.value = {
    new_episode: prefs.new_episode,
    new_chapter: prefs.new_chapter,
    friend_activity: prefs.friend_activity,
    recommendations: prefs.recommendations,
    watch_party_invite: prefs.watch_party_invite,
    watch_party_reminder: prefs.watch_party_reminder,
    discord_webhook: prefs.discord_webhook ?? '',
    telegram_chat_id: prefs.telegram_chat_id ?? '',
    email_enabled: prefs.email_enabled,
    push_enabled: prefs.push_enabled,
  }
}

async function onSubmit(): Promise<void> {
  formError.value = null
  saveSuccess.value = false

  const isValid = await preferencesFormRef.value?.validate()
  if (!isValid) {
    formError.value = 'Please fix the highlighted validation errors before saving.'
    return
  }

  try {
    await notificationsStore.savePreferences({
      ...form.value,
      discord_webhook: form.value.discord_webhook || null,
      telegram_chat_id: form.value.telegram_chat_id || null,
    })
    saveSuccess.value = true
  } catch {
    formError.value = 'Could not save preferences right now. Please try again.'
  }
}

async function goBack(): Promise<void> {
  await router.push({ name: 'notifications' })
}

onMounted(async () => {
  try {
    await notificationsStore.fetchPreferences()
    loadFromStore()
  } catch {
    // error is exposed by store banner
  }
})
</script>
