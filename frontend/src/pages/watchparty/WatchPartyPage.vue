<template>
  <div class="bg-[#0a0a0a] text-white min-h-screen p-4">
    <!-- Back button when viewing detail -->
    <div v-if="view === 'detail'" class="mb-2">
      <button @click="closeDetail" class="flex items-center text-sm text-gray-400 hover:text-white">
        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Back to parties
      </button>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-[#1f2937] mb-4" :class="{ 'pointer-events-none opacity-50': view === 'detail' }">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        class="px-4 py-2 text-sm font-medium transition-colors"
        :class="activeTab === tab.key ? 'text-white border-b-2 border-blue-500' : 'text-gray-400 hover:text-gray-300'"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Upcoming Tab -->
    <div v-if="activeTab === 'upcoming'">
      <div v-if="store.isLoading" class="flex items-center justify-center py-6">
        <svg class="animate-spin h-5 w-5 text-blue-500 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <span class="text-gray-400 text-sm">Loading upcoming parties...</span>
      </div>
      <div v-else-if="store.error" class="bg-red-600/10 border border-red-600/30 text-red-400 p-4 rounded-lg mb-4">
        <span>{{ store.error }}</span>
        <button @click="store.fetchUpcoming()" class="ml-2 underline text-sm hover:text-red-300">Retry</button>
      </div>
      <div v-else-if="store.parties.length === 0" class="text-gray-400 text-sm py-4">
        No upcoming watch parties in your groups yet.
      </div>
      <div v-else class="divide-y divide-[#1f2937] border border-[#1f2937] rounded-lg overflow-hidden">
        <div
          v-for="party in store.parties"
          :key="party.id"
          class="flex items-center justify-between p-4 hover:bg-[#111111] cursor-pointer transition-colors"
          @click="openDetail(party.id)"
        >
          <div class="flex-1 min-w-0">
            <div class="font-medium truncate">{{ party.title || 'Untitled Watch Party' }}</div>
            <div class="text-sm text-gray-400 mt-0.5">
              {{ formatDate(party.scheduled_at) }}
              <span v-if="party.episode_number !== null"> &middot; Ep. {{ party.episode_number }}</span>
            </div>
            <div class="text-xs text-gray-500 mt-0.5">
              Status: <span :class="statusBadgeClass(party.status)">{{ party.status }}</span>
            </div>
          </div>
          <button
            @click.stop="store.rsvpToParty(party.id, 'attending')"
            class="px-3 py-1.5 text-xs font-medium rounded bg-green-600 hover:bg-green-700 text-white shrink-0 ml-4"
          >
            Attend
          </button>
        </div>
      </div>
    </div>

    <!-- Past Tab -->
    <div v-if="activeTab === 'past'">
      <div v-if="store.pastIsLoading" class="flex items-center justify-center py-6">
        <svg class="animate-spin h-5 w-5 text-blue-500 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <span class="text-gray-400 text-sm">Loading past parties...</span>
      </div>
      <div v-else-if="store.pastError" class="bg-red-600/10 border border-red-600/30 text-red-400 p-4 rounded-lg mb-4">
        <span>{{ store.pastError }}</span>
        <button @click="store.fetchPast()" class="ml-2 underline text-sm hover:text-red-300">Retry</button>
      </div>
      <div v-else-if="store.pastParties.length === 0" class="text-gray-400 text-sm py-4">
        No past watch parties yet.
      </div>
      <div v-else class="divide-y divide-[#1f2937] border border-[#1f2937] rounded-lg overflow-hidden">
        <div
          v-for="party in store.pastParties"
          :key="party.id"
          class="flex items-center justify-between p-4 hover:bg-[#111111] cursor-pointer transition-colors"
          @click="openDetail(party.id)"
        >
          <div class="flex-1 min-w-0">
            <div :class="['font-medium truncate', party.status === 'cancelled' ? 'text-gray-500' : '']">
              {{ party.title || 'Untitled Watch Party' }}
            </div>
            <div class="text-sm text-gray-400 mt-0.5">{{ formatDate(party.scheduled_at) }}</div>
            <div class="text-xs text-gray-500 mt-0.5">
              <span :class="statusBadgeClass(party.status)">{{ party.status }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Tab -->
    <div v-if="activeTab === 'create'">
      <div class="bg-[#111111] border border-[#1f2937] rounded-lg">
        <div class="px-4 py-3 text-base font-medium border-b border-[#1f2937]">Create Watch Party</div>
        <form @submit.prevent="onCreate" class="p-4 space-y-4">
          <div>
            <label class="block text-sm text-gray-400 mb-1">Group ID</label>
            <input
              v-model="createForm.groupId"
              type="text"
              class="w-full bg-[#1a1a1a] border border-[#1f2937] rounded px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              placeholder="Group ID"
            />
            <p v-if="formErrors.groupId" class="text-red-400 text-xs mt-1">{{ formErrors.groupId }}</p>
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">Media ID</label>
            <input
              v-model="createForm.mediaId"
              type="text"
              class="w-full bg-[#1a1a1a] border border-[#1f2937] rounded px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              placeholder="Media ID"
            />
            <p v-if="formErrors.mediaId" class="text-red-400 text-xs mt-1">{{ formErrors.mediaId }}</p>
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">Scheduled At</label>
            <input
              v-model="createForm.scheduledAt"
              type="datetime-local"
              class="w-full bg-[#1a1a1a] border border-[#1f2937] rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
            />
            <p v-if="formErrors.scheduledAt" class="text-red-400 text-xs mt-1">{{ formErrors.scheduledAt }}</p>
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">Title (optional)</label>
            <input
              v-model="createForm.title"
              type="text"
              class="w-full bg-[#1a1a1a] border border-[#1f2937] rounded px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              placeholder="Title (optional)"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">Episode # (optional)</label>
            <input
              type="number"
              :value="createForm.episodeNumber ?? ''"
              @input="createForm.episodeNumber = ($event.target as HTMLInputElement).value ? Number(($event.target as HTMLInputElement).value) : null"
              class="w-full bg-[#1a1a1a] border border-[#1f2937] rounded px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              placeholder="Episode # (optional)"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">Stream URL (optional)</label>
            <input
              v-model="createForm.streamUrl"
              type="text"
              class="w-full bg-[#1a1a1a] border border-[#1f2937] rounded px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              placeholder="Stream URL (optional)"
            />
            <p v-if="formErrors.streamUrl" class="text-red-400 text-xs mt-1">{{ formErrors.streamUrl }}</p>
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">Notes (optional)</label>
            <textarea
              v-model="createForm.notes"
              class="w-full bg-[#1a1a1a] border border-[#1f2937] rounded px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-y min-h-[80px]"
              placeholder="Notes (optional)"
            ></textarea>
          </div>

          <div v-if="createError" class="bg-red-600/10 border border-red-600/30 text-red-400 p-3 rounded-lg text-sm">{{ createError }}</div>
          <div v-if="createSuccess" class="bg-green-600/10 border border-green-600/30 text-green-400 p-3 rounded-lg text-sm">Watch party created successfully!</div>

          <div class="flex justify-end">
            <button
              type="submit"
              :disabled="isCreateDisabled"
              class="px-4 py-2 text-sm font-medium rounded bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="store.isLoading" class="flex items-center">
                <svg class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Creating...
              </span>
              <span v-else>Create</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Detail Dialog -->
    <div v-if="detailOpen" class="fixed inset-0 z-50 bg-black/60" @click.self="closeDetail">
      <div class="absolute inset-0 overflow-y-auto">
        <div class="min-h-full flex items-start justify-center pt-8 pb-12">
          <div v-if="store.currentDetail" class="w-full max-w-2xl bg-[#111111] border border-[#1f2937] rounded-lg mx-4">
            <!-- Header -->
            <div class="flex items-center justify-between px-4 py-3 border-b border-[#1f2937]">
              <h2 class="text-lg font-semibold">{{ store.currentDetail.title || 'Watch Party' }}</h2>
              <button @click="closeDetail" class="text-gray-400 hover:text-white">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div class="p-4">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Left column -->
                <div class="space-y-3">
                  <div>
                    <div class="text-xs text-gray-500">Status</div>
                    <div class="mt-0.5">
                      <span :class="statusBadgeClass(store.currentDetail.status)">{{ store.currentDetail.status }}</span>
                    </div>
                  </div>
                  <div>
                    <div class="text-xs text-gray-500">Scheduled</div>
                    <div class="mt-0.5 text-sm">{{ formatDate(store.currentDetail.scheduled_at) }}</div>
                  </div>
                  <div v-if="store.currentDetail.episode_number !== null">
                    <div class="text-xs text-gray-500">Episode</div>
                    <div class="mt-0.5 text-sm">{{ store.currentDetail.episode_number }}</div>
                  </div>
                  <div>
                    <div class="text-xs text-gray-500">Host</div>
                    <div class="mt-0.5 text-sm">{{ store.currentDetail.host_username }}</div>
                  </div>
                  <div v-if="store.currentDetail.media_title">
                    <div class="text-xs text-gray-500">Media</div>
                    <div class="mt-0.5 text-sm">{{ store.currentDetail.media_title }}</div>
                  </div>
                  <div v-if="store.currentDetail.stream_url">
                    <div class="text-xs text-gray-500">Stream URL</div>
                    <div class="mt-0.5 text-sm">
                      <a
                        :href="store.currentDetail.stream_url"
                        target="_blank"
                        rel="noopener"
                        class="text-blue-400 hover:underline break-all"
                      >{{ store.currentDetail.stream_url }}</a>
                    </div>
                  </div>
                </div>

                <!-- Right column -->
                <div>
                  <div class="text-sm font-medium mb-2">RSVPs</div>
                  <div v-if="store.rsvpsIsLoading" class="flex items-center text-sm text-gray-400">
                    <svg class="animate-spin h-4 w-4 text-blue-500 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Loading RSVPs...
                  </div>
                  <div v-else-if="store.rsvpsError" class="text-red-400 text-sm">{{ store.rsvpsError }}</div>
                  <div v-else-if="store.rsvps.length === 0" class="text-gray-400 text-sm">No RSVPs yet.</div>
                  <div v-else class="divide-y divide-[#1f2937]">
                    <div v-for="rsvp in store.rsvps" :key="rsvp.user_id" class="flex items-center justify-between py-2">
                      <span class="text-xs text-gray-400">#{{ rsvp.user_id.slice(0, 8) }}</span>
                      <span :class="rsvpBadgeClass(rsvp.status)">{{ rsvp.status }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="store.currentDetail.notes" class="mt-4">
                <div class="text-xs text-gray-500 mb-1">Notes</div>
                <p class="text-sm whitespace-pre-wrap">{{ store.currentDetail.notes }}</p>
              </div>

              <div class="flex justify-end gap-2 mt-4">
                <button @click="store.rsvpToParty(store.currentDetail.id, 'attending')" class="px-3 py-1.5 text-xs font-medium rounded bg-green-600 hover:bg-green-700 text-white">Attending</button>
                <button @click="store.rsvpToParty(store.currentDetail.id, 'pending')" class="px-3 py-1.5 text-xs font-medium rounded bg-yellow-600 hover:bg-yellow-700 text-white">Maybe</button>
                <button @click="store.rsvpToParty(store.currentDetail.id, 'declined')" class="px-3 py-1.5 text-xs font-medium rounded bg-red-600 hover:bg-red-700 text-white">Decline</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { z } from 'zod'
import { computed, onMounted, ref, watch } from 'vue'

import { useWatchPartyStore } from 'src/stores/watchparty'

const store = useWatchPartyStore()

const activeTab = ref<'upcoming' | 'past' | 'create'>('upcoming')
const view = ref<'list' | 'detail'>('list')
const detailOpen = ref(false)

const tabs = [
  { key: 'upcoming' as const, label: 'Upcoming' },
  { key: 'past' as const, label: 'Past' },
  { key: 'create' as const, label: 'Create' },
]

// Create form
const createForm = ref({
  groupId: '',
  mediaId: '',
  scheduledAt: '',
  title: '',
  episodeNumber: null as number | null,
  streamUrl: '',
  notes: '',
})

const createSchema = z.object({
  groupId: z.string().min(1, 'Group ID is required'),
  mediaId: z.string().min(1, 'Media ID is required'),
  scheduledAt: z.string().min(1, 'Scheduled At is required'),
  streamUrl: z.string().url('Stream URL must be a valid URL starting with http:// or https://').or(z.literal('')).optional(),
})

const formErrors = ref<Record<string, string>>({})
const createSuccess = ref(false)
const createError = ref<string | null>(null)

const isCreateDisabled = computed(() =>
  store.isLoading
  || !createForm.value.groupId.trim()
  || !createForm.value.mediaId.trim()
  || !createForm.value.scheduledAt.trim(),
)

function validateForm(): boolean {
  const result = createSchema.safeParse(createForm.value)
  if (!result.success) {
    const errors: Record<string, string> = {}
    for (const issue of result.error.issues) {
      const path = issue.path[0] as string
      if (!errors[path]) {
        errors[path] = issue.message
      }
    }
    formErrors.value = errors
    return false
  }
  formErrors.value = {}
  return true
}

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

  if (!validateForm()) {
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

function statusBadgeClass(status: string): string {
  switch (status) {
    case 'scheduled': return 'inline-block px-2 py-0.5 text-xs font-medium rounded bg-blue-600 text-white'
    case 'live': return 'inline-block px-2 py-0.5 text-xs font-medium rounded bg-green-600 text-white'
    case 'completed': return 'inline-block px-2 py-0.5 text-xs font-medium rounded bg-gray-600 text-white'
    case 'cancelled': return 'inline-block px-2 py-0.5 text-xs font-medium rounded bg-red-600 text-white'
    default: return 'inline-block px-2 py-0.5 text-xs font-medium rounded bg-gray-600 text-white'
  }
}

function rsvpBadgeClass(status: string): string {
  switch (status) {
    case 'attending': return 'inline-block px-2 py-0.5 text-xs font-medium rounded bg-green-600 text-white'
    case 'pending': return 'inline-block px-2 py-0.5 text-xs font-medium rounded bg-yellow-600 text-white'
    case 'declined': return 'inline-block px-2 py-0.5 text-xs font-medium rounded bg-red-600 text-white'
    default: return 'inline-block px-2 py-0.5 text-xs font-medium rounded bg-gray-600 text-white'
  }
}
</script>
