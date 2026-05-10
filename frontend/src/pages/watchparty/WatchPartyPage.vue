<template>
  <q-page class="q-pa-md">
    <q-card bordered flat class="q-mb-md">
      <q-card-section>
        <div class="text-subtitle1">Create Watch Party</div>
      </q-card-section>

      <q-separator />

      <q-form ref="createFormRef" @submit="onCreate">
        <q-card-section class="q-gutter-md">
          <q-input v-model="createForm.groupId" outlined label="Group ID" lazy-rules :rules="groupIdRules" />
          <q-input v-model="createForm.mediaId" outlined label="Media ID" lazy-rules :rules="mediaIdRules" />
          <q-input v-model="createForm.scheduledAt" outlined type="datetime-local" label="Scheduled At" lazy-rules :rules="scheduledAtRules" />
          <q-input v-model="createForm.title" outlined label="Title (optional)" />
          <q-input v-model.number="createForm.episodeNumber" outlined type="number" label="Episode # (optional)" />
          <q-input v-model="createForm.streamUrl" outlined label="Stream URL (optional)" lazy-rules :rules="streamUrlRules" />
          <q-input v-model="createForm.notes" outlined type="textarea" label="Notes (optional)" autogrow />

          <q-banner v-if="createError" class="bg-negative text-white" rounded>
            {{ createError }}
          </q-banner>
          <q-banner v-if="createSuccess" class="bg-green-1 text-green-9" rounded>
            Watch party created successfully.
          </q-banner>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn color="primary" :loading="watchPartyStore.isLoading" :disable="isCreateDisabled" label="Create" type="submit" />
        </q-card-actions>
      </q-form>
    </q-card>

    <div class="row items-center justify-between q-mb-md">
      <div class="text-h5">Watch Parties</div>
      <q-btn
        label="Refresh"
        color="primary"
        flat
        :loading="watchPartyStore.isLoading"
        @click="watchPartyStore.fetchUpcoming()"
      />
    </div>

    <app-page-state
      :is-loading="watchPartyStore.isLoading"
      :error="watchPartyStore.error"
      :is-empty="watchPartyStore.parties.length === 0"
      empty-label="No upcoming watch parties in your groups yet."
      loading-label="Loading upcoming watch parties..."
      @retry="watchPartyStore.fetchUpcoming"
    >
      <q-list bordered separator>
      <q-item v-for="party in watchPartyStore.parties" :key="party.id">
        <q-item-section>
          <q-item-label>{{ party.title || 'Untitled watch party' }}</q-item-label>
          <q-item-label caption>
            Scheduled: {{ new Date(party.scheduled_at).toLocaleString() }}
          </q-item-label>
          <q-item-label caption v-if="party.episode_number !== null">
            Episode {{ party.episode_number }}
          </q-item-label>
          <q-item-label caption>Party ID: {{ party.id }}</q-item-label>
        </q-item-section>
        <q-item-section side>
          <div class="column q-gutter-sm">
            <q-btn size="sm" color="positive" label="Attending" @click="onRsvp(party.id, 'attending')" />
            <q-btn size="sm" color="warning" label="Maybe" @click="onRsvp(party.id, 'pending')" />
            <q-btn size="sm" color="negative" label="Decline" @click="onRsvp(party.id, 'declined')" />
          </div>
        </q-item-section>
      </q-item>
      </q-list>
    </app-page-state>
  </q-page>
</template>

<script setup lang="ts">
import type { QForm } from 'quasar'
import { computed, onMounted, ref } from 'vue'

import AppPageState from 'src/components/AppPageState.vue'
import { useValidationRules } from 'src/composables/useValidationRules'
import { useWatchPartyStore } from 'src/stores/watchparty'

const watchPartyStore = useWatchPartyStore()
const createFormRef = ref<QForm | null>(null)
const createSuccess = ref(false)
const createError = ref<string | null>(null)
const rules = useValidationRules()

const groupIdRules = [rules.required('Group ID')]
const mediaIdRules = [rules.required('Media ID')]
const scheduledAtRules = [rules.required('Scheduled At')]
const streamUrlRules = [rules.isHttpUrl('Stream URL')]

const createForm = ref({
  groupId: '',
  mediaId: '',
  scheduledAt: '',
  title: '',
  episodeNumber: null as number | null,
  streamUrl: '',
  notes: '',
})

const isCreateDisabled = computed(() =>
  watchPartyStore.isLoading
  || !createForm.value.groupId.trim()
  || !createForm.value.mediaId.trim()
  || !createForm.value.scheduledAt.trim(),
)

async function onCreate(): Promise<void> {
  createSuccess.value = false
  createError.value = null

  const isValid = await createFormRef.value?.validate()
  if (!isValid) {
    createError.value = 'Please fix validation errors before submitting.'
    return
  }

  try {
    await watchPartyStore.createWatchParty({
      group_id: createForm.value.groupId,
      media_id: createForm.value.mediaId,
      scheduled_at: new Date(createForm.value.scheduledAt).toISOString(),
      title: createForm.value.title || undefined,
      episode_number: createForm.value.episodeNumber ?? undefined,
      stream_url: createForm.value.streamUrl || undefined,
      notes: createForm.value.notes || undefined,
    })
    createSuccess.value = true
  } catch {
    // store handles error state
  }
}

async function onRsvp(partyId: string, status: 'pending' | 'attending' | 'declined'): Promise<void> {
  try {
    await watchPartyStore.rsvpToParty(partyId, status)
  } catch {
    // store handles error state
  }
}

onMounted(async () => {
  await watchPartyStore.fetchUpcoming()
})
</script>
