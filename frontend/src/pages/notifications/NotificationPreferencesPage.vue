<template>
  <div class="p-4 min-h-screen bg-[#0a0a0a] text-white">
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-bold">Notification Preferences</h1>
      <button class="text-sm text-blue-400 hover:text-blue-300 transition-colors" @click="goBack">
        Back to Bell
      </button>
    </div>

    <div v-if="formError" class="bg-red-700 text-white px-4 py-2 rounded mb-4 text-sm">{{ formError }}</div>
    <div v-if="saveSuccess" class="bg-green-700 text-white px-4 py-2 rounded mb-4 text-sm">Preferences saved.</div>
    <div v-if="notificationsStore.preferencesError" class="bg-red-700 text-white px-4 py-2 rounded mb-4 text-sm">
      {{ notificationsStore.preferencesError }}
    </div>

    <form class="space-y-4" @submit.prevent="onSubmit">
      <label class="flex items-center gap-3 cursor-pointer">
        <input type="checkbox" v-model="form.new_episode" class="w-4 h-4 rounded bg-[#111111] border-[#1f2937] accent-blue-500" />
        <span class="text-sm">New episode alerts</span>
      </label>
      <label class="flex items-center gap-3 cursor-pointer">
        <input type="checkbox" v-model="form.new_chapter" class="w-4 h-4 rounded bg-[#111111] border-[#1f2937] accent-blue-500" />
        <span class="text-sm">New chapter alerts</span>
      </label>
      <label class="flex items-center gap-3 cursor-pointer">
        <input type="checkbox" v-model="form.friend_activity" class="w-4 h-4 rounded bg-[#111111] border-[#1f2937] accent-blue-500" />
        <span class="text-sm">Friend activity</span>
      </label>
      <label class="flex items-center gap-3 cursor-pointer">
        <input type="checkbox" v-model="form.recommendations" class="w-4 h-4 rounded bg-[#111111] border-[#1f2937] accent-blue-500" />
        <span class="text-sm">Recommendations</span>
      </label>
      <label class="flex items-center gap-3 cursor-pointer">
        <input type="checkbox" v-model="form.watch_party_invite" class="w-4 h-4 rounded bg-[#111111] border-[#1f2937] accent-blue-500" />
        <span class="text-sm">Watch party invites</span>
      </label>
      <label class="flex items-center gap-3 cursor-pointer">
        <input type="checkbox" v-model="form.watch_party_reminder" class="w-4 h-4 rounded bg-[#111111] border-[#1f2937] accent-blue-500" />
        <span class="text-sm">Watch party reminders</span>
      </label>

      <div>
        <label class="block text-sm mb-1">Discord webhook (optional)</label>
        <input
          v-model="form.discord_webhook"
          type="text"
          placeholder="https://discord.com/api/webhooks/..."
          class="w-full px-3 py-2 rounded bg-[#111111] border border-[#1f2937] text-white text-sm placeholder-gray-500 focus:outline-none focus:border-blue-500 transition-colors"
        />
        <p v-if="discordValidationError" class="text-red-400 text-xs mt-1">{{ discordValidationError }}</p>
      </div>

      <div>
        <label class="block text-sm mb-1">Telegram chat ID (optional)</label>
        <input
          v-model="form.telegram_chat_id"
          type="text"
          placeholder="-1001234567890"
          class="w-full px-3 py-2 rounded bg-[#111111] border border-[#1f2937] text-white text-sm placeholder-gray-500 focus:outline-none focus:border-blue-500 transition-colors"
        />
        <p v-if="telegramValidationError" class="text-red-400 text-xs mt-1">{{ telegramValidationError }}</p>
      </div>

      <label class="flex items-center gap-3 cursor-pointer">
        <input type="checkbox" v-model="form.email_enabled" class="w-4 h-4 rounded bg-[#111111] border-[#1f2937] accent-blue-500" />
        <span class="text-sm">Enable email delivery</span>
      </label>
      <label class="flex items-center gap-3 cursor-pointer">
        <input type="checkbox" v-model="form.push_enabled" class="w-4 h-4 rounded bg-[#111111] border-[#1f2937] accent-blue-500" />
        <span class="text-sm">Enable push delivery</span>
      </label>

      <div class="flex gap-2 pt-2">
        <button
          type="submit"
          :disabled="notificationsStore.isSavingPreferences"
          class="px-4 py-2 rounded bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium transition-colors"
        >
          {{ notificationsStore.isSavingPreferences ? 'Saving...' : 'Save Preferences' }}
        </button>
        <button
          type="button"
          class="px-4 py-2 rounded bg-[#111111] border border-[#1f2937] hover:bg-[#1a1a1a] text-white text-sm transition-colors"
          @click="loadFromStore"
        >
          Reset
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useNotificationsStore } from 'src/stores/notifications'

const router = useRouter()
const notificationsStore = useNotificationsStore()
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

const discordValidationError = computed(() => {
  if (!form.value.discord_webhook) {
    return null
  }
  const isValid = /^(https?:\/\/|discord:\/\/).+/.test(form.value.discord_webhook)
  return isValid ? null : 'Discord webhook must start with https://, http://, or discord://'
})

const telegramValidationError = computed(() => {
  if (!form.value.telegram_chat_id) {
    return null
  }
  const isValid = /^-?\d+$/.test(form.value.telegram_chat_id)
  return isValid ? null : 'Telegram chat ID must be numeric'
})

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

  if (discordValidationError.value || telegramValidationError.value) {
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
