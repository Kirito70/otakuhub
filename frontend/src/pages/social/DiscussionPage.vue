<template>
  <q-page class="q-pa-md">
    <!-- Navigation breadcrumb when viewing thread detail -->
    <div v-if="view === 'detail'" class="q-mb-sm">
      <q-btn flat dense icon="arrow_back" label="Back to threads" @click="view = 'list'" />
    </div>

    <q-tabs v-model="activeTab" class="q-mb-md" dense :disable="view === 'detail'">
      <q-tab name="threads" label="Threads" />
      <q-tab name="create" label="Create" />
    </q-tabs>

    <q-tab-panels v-model="activeTab" animated>
      <!-- Threads List Tab -->
      <q-tab-panel name="threads" class="q-pa-none">
        <!-- Media selector for discussions -->
        <div v-if="view === 'list'" class="q-mb-md">
          <q-input
            v-model="mediaSearchId"
            outlined
            dense
            placeholder="Enter Media ID to view discussions (or paste from URL)"
            label="Media ID"
          >
            <template #append>
              <q-btn flat dense icon="search" :loading="store.discussionsIsLoading" @click="fetchForMedia" />
            </template>
          </q-input>
        </div>

        <app-page-state
          :is-loading="store.discussionsIsLoading"
          :error="store.discussionsError"
          :is-empty="store.discussions.length === 0 && !store.discussionsIsLoading"
          :empty-label="currentMediaId ? 'No discussions for this media yet.' : 'Enter a Media ID above to view discussions.'"
          loading-label="Loading discussions..."
          @retry="fetchForMedia()"
        >
          <template v-if="view === 'list'">
            <q-list separator>
              <q-item
                v-for="disc in store.discussions"
                :key="disc.id"
                clickable
                v-ripple
                @click="openThread(disc)"
              >
                <q-item-section>
                  <q-item-label class="text-weight-medium">
                    {{ disc.title || 'Untitled' }}
                    <q-badge v-if="disc.has_spoilers" color="warning" label="Spoiler" class="q-ml-xs" />
                  </q-item-label>
                  <q-item-label caption class="ellipsis-2-lines">
                    {{ disc.body }}
                  </q-item-label>
                  <q-item-label caption class="text-grey-7 text-caption q-mt-xs">
                    by #{{ disc.user_id.slice(0, 8) }} · {{ formatDate(disc.created_at) }}
                    <template v-if="disc.episode_number"> · Ep. {{ disc.episode_number }}</template>
                    <template v-if="disc.chapter_number"> · Ch. {{ disc.chapter_number }}</template>
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>

            <div v-if="store.discussionsHasMore" class="text-center q-mt-md">
              <q-btn
                flat
                color="primary"
                label="Load More"
                :loading="store.discussionsIsLoading"
                :disable="store.discussionsIsLoading"
                @click="store.fetchDiscussions(currentMediaId, 50, store.discussionsOffset)"
              />
            </div>
          </template>

          <!-- Thread Detail View -->
          <template v-if="view === 'detail' && currentDiscussion">
            <q-card bordered flat class="q-mb-md">
              <q-card-section>
                <div class="text-h6">
                  {{ currentDiscussion.title || 'Untitled' }}
                  <q-badge v-if="currentDiscussion.has_spoilers" color="warning" label="Spoiler" class="q-ml-xs" />
                </div>
                <div class="text-caption text-grey-7 q-mt-xs">
                  by #{{ currentDiscussion.user_id.slice(0, 8) }} · {{ formatDate(currentDiscussion.created_at) }}
                </div>
              </q-card-section>
              <q-card-section class="q-pt-none">
                <p class="text-body1" style="white-space: pre-wrap">{{ currentDiscussion.body }}</p>
              </q-card-section>
            </q-card>

            <!-- Replies Section -->
            <div class="text-subtitle2 q-mb-sm">Replies ({{ store.repliesTotal }})</div>

            <app-page-state
              :is-loading="store.repliesIsLoading"
              :error="store.repliesError"
              :is-empty="store.replies.length === 0 && !store.repliesIsLoading"
              empty-label="No replies yet. Be the first to reply!"
              loading-label="Loading replies..."
              @retry="store.fetchDiscussionReplies(currentDiscussion.id)"
            >
              <q-list separator>
                <q-item v-for="reply in store.replies" :key="reply.id">
                  <q-item-section>
                    <q-item-label caption class="text-grey-7">
                      #{{ reply.user_id.slice(0, 8) }} · {{ formatDate(reply.created_at) }}
                      <q-badge v-if="reply.has_spoilers" color="warning" label="Spoiler" class="q-ml-xs" />
                    </q-item-label>
                    <q-item-label class="q-mt-xs" style="white-space: pre-wrap">
                      <template v-if="reply.has_spoilers && !revealedReplies[reply.id]">
                        <q-btn flat dense color="warning" label="Show Spoiler" @click="revealReply(reply.id)" />
                      </template>
                      <template v-else>
                        {{ reply.body }}
                      </template>
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>

              <div v-if="store.repliesHasMore" class="text-center q-mt-md">
                <q-btn
                  flat
                  color="primary"
                  label="Load More Replies"
                  :loading="store.repliesIsLoading"
                  :disable="store.repliesIsLoading"
                  @click="store.fetchDiscussionReplies(currentDiscussion.id, 50, store.repliesOffset)"
                />
              </div>
            </app-page-state>

            <!-- Reply Form -->
            <q-form @submit.prevent="submitReply" class="q-mt-md">
              <q-input
                v-model="replyBody"
                outlined
                dense
                type="textarea"
                label="Write a reply..."
                :rules="[val => !!val || 'Reply cannot be empty']"
                lazy-rules
                class="q-mb-sm"
              />
              <div class="row items-center justify-between">
                <q-toggle v-model="replyHasSpoilers" label="Mark as spoiler" dense />
                <q-btn
                  type="submit"
                  color="primary"
                  label="Post Reply"
                  :loading="store.replyActionStatus === 'loading'"
                  :disable="store.replyActionStatus === 'loading' || !replyBody.trim()"
                />
              </div>
            </q-form>
          </template>
        </app-page-state>
      </q-tab-panel>

      <!-- Create Tab -->
      <q-tab-panel name="create" class="q-pa-none">
        <q-form @submit.prevent="submitDiscussion" class="q-gutter-md">
          <q-input
            v-model="createForm.media_id"
            outlined
            dense
            label="Media ID *"
            placeholder="UUID of the media entry"
            :rules="[val => !!val || 'Media ID is required']"
            lazy-rules
          />
          <q-input
            v-model="createForm.group_id"
            outlined
            dense
            label="Group ID *"
            placeholder="UUID of the group"
            :rules="[val => !!val || 'Group ID is required']"
            lazy-rules
          />
          <q-input
            v-model="createForm.title"
            outlined
            dense
            label="Title (optional)"
            placeholder="Discussion title"
          />
          <q-input
            v-model="createForm.body"
            outlined
            dense
            type="textarea"
            label="Body *"
            placeholder="Write your discussion content..."
            :rules="[val => !!val || 'Body is required']"
            lazy-rules
          />
          <div class="row items-center q-gutter-md">
            <q-toggle v-model="createForm.has_spoilers" label="Contains spoilers" dense />
            <q-input
              v-model="createForm.episode_number"
              outlined
              dense
              type="number"
              label="Episode (optional)"
              style="max-width: 150px"
              :rules="[val => val === null || val === undefined || val === '' || Number(val) > 0 || 'Must be positive']"
              lazy-rules
            />
          </div>

          <div class="row justify-end q-mt-md">
            <q-btn
              type="submit"
              color="primary"
              label="Create Discussion"
              :loading="store.createDiscussionStatus === 'loading'"
              :disable="store.createDiscussionStatus === 'loading'"
            />
          </div>
        </q-form>
      </q-tab-panel>
    </q-tab-panels>
  </q-page>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'

import AppPageState from 'src/components/AppPageState.vue'
import { useSocialStore } from 'src/stores/social'
import type { Discussion, DiscussionCreateRequest } from 'src/types/social'

const store = useSocialStore()

const activeTab = ref<'threads' | 'create'>('threads')
const view = ref<'list' | 'detail'>('list')
const currentDiscussion = ref<Discussion | null>(null)
const currentMediaId = ref<string>('')

// Media search for discussions
const mediaSearchId = ref('')

// Reply form
const replyBody = ref('')
const replyHasSpoilers = ref(false)
const revealedReplies = ref<Record<string, boolean>>({})

// Create form
const createForm = reactive<DiscussionCreateRequest>({
  media_id: '',
  group_id: '',
  title: '',
  body: '',
  has_spoilers: false,
  episode_number: null,
  chapter_number: null,
})

async function fetchForMedia(): Promise<void> {
  if (!mediaSearchId.value.trim()) return
  currentMediaId.value = mediaSearchId.value.trim()
    await store.fetchDiscussions(currentMediaId.value, 50, 0)
}

async function openThread(disc: Discussion): Promise<void> {
  currentDiscussion.value = disc
  view.value = 'detail'
  store.replies = []
  store.repliesOffset = 0
  await store.fetchDiscussionReplies(disc.id, 50, 0)
}

async function submitReply(): Promise<void> {
  if (!replyBody.value.trim() || !currentDiscussion.value) return
  const success = await store.createDiscussionReply(currentDiscussion.value.id, {
    body: replyBody.value,
    has_spoilers: replyHasSpoilers.value,
  })
  if (success) {
    replyBody.value = ''
    replyHasSpoilers.value = false
  }
}

async function submitDiscussion(): Promise<void> {
  const discussion = await store.createDiscussion({
    media_id: createForm.media_id,
    group_id: createForm.group_id,
    title: createForm.title || null,
    body: createForm.body,
    has_spoilers: createForm.has_spoilers,
    episode_number: createForm.episode_number ? Number(createForm.episode_number) : null,
    chapter_number: createForm.chapter_number ? Number(createForm.chapter_number) : null,
  })
  if (discussion) {
    // Reset form
    createForm.media_id = ''
    createForm.group_id = ''
    createForm.title = ''
    createForm.body = ''
    createForm.has_spoilers = false
    createForm.episode_number = null
    createForm.chapter_number = null
    // Switch to threads and load the new discussion
    activeTab.value = 'threads'
    mediaSearchId.value = discussion.media_id
    await fetchForMedia()
  }
}

function revealReply(replyId: string): void {
  revealedReplies.value[replyId] = true
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>
