<template>
  <q-page class="q-pa-md">
    <!-- Back button when viewing detail -->
    <div v-if="view === 'detail'" class="q-mb-sm">
      <q-btn flat dense icon="arrow_back" label="Back to parties" @click="closeDetail" />
    </div>

    <q-tabs v-model="activeTab" class="q-mb-md" dense :disable="view === 'detail'">
      <q-tab name="upcoming" label="Upcoming" />
      <q-tab name="past" label="Past" />
      <q-tab name="create" label="Create" />
    </q-tabs>

    <q-tab-panels v-model="activeTab" animated>
      <!-- Upcoming Tab -->
      <q-tab-panel name="upcoming" class="q-pa-none">
        <app-page-state
          :is-loading="store.isLoading"
          :error="store.error"
          :is-empty="store.parties.length === 0 && !store.isLoading"
          empty-label="No upcoming watch parties in your groups yet."
          loading-label="Loading upcoming parties..."
          @retry="store.fetchUpcoming()"
        >
          <q-list bordered separator>
            <q-item
              v-for="party in store.parties"
              :key="party.id"
              clickable
              v-ripple
              @click="openDetail(party.id)"
            >
              <q-item-section>
                <q-item-label class="text-weight-medium">
                  {{ party.title || 'Untitled Watch Party' }}
                </q-item-label>
                <q-item-label caption>
                  {{ formatDate(party.scheduled_at) }}
                  <span v-if="party.episode_number !== null"> · Ep. {{ party.episode_number }}</span>
                </q-item-label>
                <q-item-label caption class="text-grey-7">
                  Status: <q-badge :color="statusColor(party.status)" :label="party.status" />
                </q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-btn size="sm" color="positive" label="Attend" @click.stop="store.rsvpToParty(party.id, 'attending')" />
              </q-item-section>
            </q-item>
          </q-list>
        </app-page-state>
      </q-tab-panel>

      <!-- Past Tab -->
      <q-tab-panel name="past" class="q-pa-none">
        <app-page-state
          :is-loading="store.pastIsLoading"
          :error="store.pastError"
          :is-empty="store.pastParties.length === 0 && !store.pastIsLoading"
          empty-label="No past watch parties yet."
          loading-label="Loading past parties..."
          @retry="store.fetchPast()"
        >
          <q-list bordered separator>
            <q-item
              v-for="party in store.pastParties"
              :key="party.id"
              clickable
              v-ripple
              @click="openDetail(party.id)"
            >
              <q-item-section>
                <q-item-label :class="party.status === 'cancelled' ? 'text-grey-5' : ''">
                  {{ party.title || 'Untitled Watch Party' }}
                </q-item-label>
                <q-item-label caption>
                  {{ formatDate(party.scheduled_at) }}
                </q-item-label>
                <q-item-label caption class="text-grey-7">
                  <q-badge :color="statusColor(party.status)" :label="party.status" />
                </q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </app-page-state>
      </q-tab-panel>

      <!-- Create Tab -->
      <q-tab-panel name="create" class="q-pa-none">
        <q-card bordered flat>
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
              <q-banner v-if="createSuccess" class="bg-positive text-white" rounded>
                Watch party created successfully!
              </q-banner>
            </q-card-section>

            <q-card-actions align="right">
              <q-btn
                color="primary"
                :loading="store.isLoading"
                :disable="isCreateDisabled"
                label="Create"
                type="submit"
              />
            </q-card-actions>
          </q-form>
        </q-card>
      </q-tab-panel>
    </q-tab-panels>

    <!-- Detail Dialog -->
    <q-dialog v-model="detailOpen" maximized transition-show="slide-up" transition-hide="slide-down">
      <q-card v-if="store.currentDetail">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">{{ store.currentDetail.title || 'Watch Party' }}</div>
          <q-space />
          <q-btn flat dense icon="close" v-close-popup />
        </q-card-section>

        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-6">
              <q-list dense>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Status</q-item-label>
                    <q-item-label>
                      <q-badge :color="statusColor(store.currentDetail.status)" :label="store.currentDetail.status" />
                    </q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Scheduled</q-item-label>
                    <q-item-label>{{ formatDate(store.currentDetail.scheduled_at) }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="store.currentDetail.episode_number !== null">
                  <q-item-section>
                    <q-item-label caption>Episode</q-item-label>
                    <q-item-label>{{ store.currentDetail.episode_number }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Host</q-item-label>
                    <q-item-label>{{ store.currentDetail.host_username }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="store.currentDetail.media_title">
                  <q-item-section>
                    <q-item-label caption>Media</q-item-label>
                    <q-item-label>{{ store.currentDetail.media_title }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="store.currentDetail.stream_url">
                  <q-item-section>
                    <q-item-label caption>Stream URL</q-item-label>
                    <q-item-label>
                      <a :href="store.currentDetail.stream_url" target="_blank" rel="noopener">{{ store.currentDetail.stream_url }}</a>
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <div class="col-12 col-md-6">
              <div class="text-subtitle2 q-mb-sm">RSVPs</div>
              <app-page-state
                :is-loading="store.rsvpsIsLoading"
                :error="store.rsvpsError"
                :is-empty="store.rsvps.length === 0 && !store.rsvpsIsLoading"
                empty-label="No RSVPs yet."
                loading-label="Loading RSVPs..."
              >
                <q-list dense>
                  <q-item v-for="rsvp in store.rsvps" :key="rsvp.user_id">
                    <q-item-section>
                      <q-item-label caption>#{{ rsvp.user_id.slice(0, 8) }}</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-badge :color="rsvpColor(rsvp.status)" :label="rsvp.status" />
                    </q-item-section>
                  </q-item>
                </q-list>
              </app-page-state>
            </div>
          </div>

          <div v-if="store.currentDetail.notes" class="q-mt-md">
            <div class="text-caption text-grey-7">Notes</div>
            <p class="text-body2" style="white-space: pre-wrap">{{ store.currentDetail.notes }}</p>
          </div>

          <div class="row justify-end q-mt-md q-gutter-sm">
            <q-btn color="positive" label="Attending" @click="store.rsvpToParty(store.currentDetail.id, 'attending')" />
            <q-btn color="warning" label="Maybe" @click="store.rsvpToParty(store.currentDetail.id, 'pending')" />
            <q-btn color="negative" label="Decline" @click="store.rsvpToParty(store.currentDetail.id, 'declined')" />
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import type { QForm } from 'quasar'
import { computed, onMounted, ref, watch } from 'vue'

import AppPageState from 'src/components/AppPageState.vue'
import { useValidationRules } from 'src/composables/useValidationRules'
import { useWatchPartyStore } from 'src/stores/watchparty'

const store = useWatchPartyStore()
const rules = useValidationRules()

const activeTab = ref<'upcoming' | 'past' | 'create'>('upcoming')
const view = ref<'list' | 'detail'>('list')
const detailOpen = ref(false)

// Create form
const createFormRef = ref<QForm | null>(null)
const createSuccess = ref(false)
const createError = ref<string | null>(null)
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
  store.isLoading
  || !createForm.value.groupId.trim()
  || !createForm.value.mediaId.trim()
  || !createForm.value.scheduledAt.trim(),
)

// Fetch upcoming on mount
onMounted(async () => {
  await store.fetchUpcoming()
})

// Fetch past when switching to past tab
watch(activeTab, (tab) => {
  if (tab === 'past' && store.pastParties.length === 0) {
    store.fetchPast()
  }
})

async function onCreate(): Promise<void> {
  createSuccess.value = false
  createError.value = null

  const isValid = await createFormRef.value?.validate()
  if (!isValid) {
    createError.value = 'Please fix validation errors before submitting.'
    return
  }

  try {
    await store.createWatchParty({
      group_id: createForm.value.groupId,
      media_id: createForm.value.mediaId,
      scheduled_at: new Date(createForm.value.scheduledAt).toISOString(),
      title: createForm.value.title || undefined,
      episode_number: createForm.value.episodeNumber ?? undefined,
      stream_url: createForm.value.streamUrl || undefined,
      notes: createForm.value.notes || undefined,
    })
    createSuccess.value = true
    // Switch to upcoming tab after creation
    activeTab.value = 'upcoming'
  } catch {
    // Store handles error state
  }
}

async function openDetail(partyId: string): Promise<void> {
  view.value = 'detail'
  detailOpen.value = true
  await store.fetchPartyDetail(partyId)
  await store.fetchRsvps(partyId)
}

function closeDetail(): void {
  detailOpen.value = false
  view.value = 'list'
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString()
}

function statusColor(status: string): string {
  switch (status) {
    case 'scheduled': return 'primary'
    case 'live': return 'positive'
    case 'completed': return 'grey'
    case 'cancelled': return 'negative'
    default: return 'grey'
  }
}

function rsvpColor(status: string): string {
  switch (status) {
    case 'attending': return 'positive'
    case 'pending': return 'warning'
    case 'declined': return 'negative'
    default: return 'grey'
  }
}
</script>
