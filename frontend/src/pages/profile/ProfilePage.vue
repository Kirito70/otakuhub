<template>
  <q-page class="q-pa-md">
    <q-tabs v-model="activeTab" class="q-mb-md" dense>
      <q-tab name="overview" label="Overview" />
      <q-tab name="edit" label="Edit Profile" />
      <q-tab name="security" label="Account & Security" />
    </q-tabs>

    <q-tab-panels v-model="activeTab" animated>
      <!-- Overview Tab -->
      <q-tab-panel name="overview" class="q-pa-none">
        <app-page-state
          :is-loading="!user"
          :error="null"
          :is-empty="!user"
        >
          <div v-if="user" class="row q-col-gutter-md">
            <!-- Profile Card -->
            <div class="col-12 col-md-4">
              <q-card bordered flat>
                <q-card-section class="items-center column text-center">
                  <q-avatar size="96px" class="q-mb-md">
                    <img v-if="user.avatar_url" :src="user.avatar_url" alt="Avatar" />
                    <div v-else class="bg-primary text-white text-h4 flex flex-center" style="width:96px;height:96px;border-radius:50%">
                      {{ avatarInitial }}
                    </div>
                  </q-avatar>
                  <div class="text-h6">{{ user.display_name || user.username }}</div>
                  <div class="text-caption text-grey-7">@{{ user.username }}</div>
                </q-card-section>
                <q-separator />
                <q-card-section>
                  <div class="text-body2 q-mb-xs">
                    <strong>Email:</strong> {{ user.email }}
                  </div>
                  <div class="text-body2 q-mb-xs">
                    <strong>Timezone:</strong> {{ user.timezone }}
                  </div>
                  <div class="text-body2 q-mb-xs">
                    <strong>Member since:</strong> {{ formatDate(user.created_at) }}
                  </div>
                </q-card-section>
              </q-card>
            </div>

            <!-- Bio Card -->
            <div class="col-12 col-md-8">
              <q-card bordered flat>
                <q-card-section>
                  <div class="text-subtitle1">Bio</div>
                  <p v-if="user.bio" class="text-body2 q-mt-sm" style="white-space: pre-wrap">{{ user.bio }}</p>
                  <p v-else class="text-grey-7 text-caption q-mt-sm">No bio yet.</p>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </app-page-state>
      </q-tab-panel>

      <!-- Edit Profile Tab -->
      <q-tab-panel name="edit" class="q-pa-none">
        <q-card bordered flat>
          <q-card-section>
            <q-form @submit.prevent="saveProfile" class="q-gutter-md">
              <q-input
                v-model="editForm.display_name"
                outlined
                dense
                label="Display Name"
                placeholder="Your display name"
                maxlength="100"
              />
              <q-input
                v-model="editForm.avatar_url"
                outlined
                dense
                label="Avatar URL"
                placeholder="https://example.com/avatar.jpg"
                :rules="[val => !val || isValidUrl(val) || 'Must be a valid URL']"
                lazy-rules
              />
              <q-input
                v-model="editForm.bio"
                outlined
                dense
                type="textarea"
                label="Bio"
                placeholder="Tell us about yourself..."
                maxlength="1000"
              />
              <q-select
                v-model="editForm.timezone"
                outlined
                dense
                label="Timezone"
                :options="commonTimezones"
                emit-value
                map-options
              />

              <div class="row justify-end">
                <q-btn
                  type="submit"
                  color="primary"
                  label="Save Changes"
                  :loading="isSavingProfile"
                  :disable="isSavingProfile"
                />
              </div>

              <q-banner v-if="profileSaveStatus === 'success'" class="bg-positive text-white q-mt-sm" dense>
                Profile updated successfully!
              </q-banner>
              <q-banner v-if="profileSaveStatus === 'error'" class="bg-negative text-white q-mt-sm" dense>
                Failed to update profile. Please try again.
              </q-banner>
            </q-form>
          </q-card-section>
        </q-card>
      </q-tab-panel>

      <!-- Account & Security Tab -->
      <q-tab-panel name="security" class="q-pa-none">
        <q-card bordered flat>
          <q-card-section>
            <div class="text-subtitle1 q-mb-md">Change Password</div>
            <q-form @submit.prevent="changePassword" class="q-gutter-md">
              <q-input
                v-model="passwordForm.current_password"
                outlined
                dense
                type="password"
                label="Current Password *"
                :rules="[val => !!val || 'Current password is required']"
                lazy-rules
              />
              <q-input
                v-model="passwordForm.new_password"
                outlined
                dense
                type="password"
                label="New Password *"
                :rules="[
                  val => !!val || 'New password is required',
                  val => val.length >= 8 || 'Password must be at least 8 characters',
                ]"
                lazy-rules
              />
              <q-input
                v-model="passwordForm.new_password_confirm"
                outlined
                dense
                type="password"
                label="Confirm New Password *"
                :rules="[
                  val => !!val || 'Please confirm your new password',
                  val => val === passwordForm.new_password || 'Passwords do not match',
                ]"
                lazy-rules
              />

              <div class="row justify-end">
                <q-btn
                  type="submit"
                  color="primary"
                  label="Change Password"
                  :loading="isSavingPassword"
                  :disable="isSavingPassword"
                />
              </div>

              <q-banner v-if="passwordSaveStatus === 'success'" class="bg-positive text-white q-mt-sm" dense>
                Password changed successfully!
              </q-banner>
              <q-banner v-if="passwordSaveStatus === 'error'" class="bg-negative text-white q-mt-sm" dense>
                Failed to change password. Check your current password and try again.
              </q-banner>
            </q-form>
          </q-card-section>
        </q-card>
      </q-tab-panel>
    </q-tab-panels>
  </q-page>
</template>

<script setup lang="ts">
import { reactive, ref, watch, computed } from 'vue'
import { useQuasar } from 'quasar'

import { api } from 'src/boot/axios'
import AppPageState from 'src/components/AppPageState.vue'
import { useAuthStore } from 'src/stores/auth'
import type { UserSettings, UserSettingsUpdateRequest } from 'src/types/social'

const $q = useQuasar()
const auth = useAuthStore()

const activeTab = ref<'overview' | 'edit' | 'security'>('overview')

// User data from auth store
const user = computed(() => auth.user)

const avatarInitial = computed(() => {
  const name = user.value?.display_name || user.value?.username || 'U'
  return name.charAt(0).toUpperCase()
})

// Edit form
const editForm = reactive({
  display_name: '',
  avatar_url: '',
  bio: '',
  timezone: 'UTC',
})
const isSavingProfile = ref(false)
const profileSaveStatus = ref<'idle' | 'success' | 'error'>('idle')

// Password form
const passwordForm = reactive({
  current_password: '',
  new_password: '',
  new_password_confirm: '',
})
const isSavingPassword = ref(false)
const passwordSaveStatus = ref<'idle' | 'success' | 'error'>('idle')

const commonTimezones = [
  'UTC', 'America/New_York', 'America/Chicago', 'America/Denver',
  'America/Los_Angeles', 'Europe/London', 'Europe/Berlin', 'Europe/Paris',
  'Asia/Tokyo', 'Asia/Seoul', 'Asia/Shanghai', 'Asia/Kolkata',
  'Australia/Sydney', 'Pacific/Auckland',
]

// Hydrate edit form when switching to edit tab
watch(activeTab, (tab) => {
  if (tab === 'edit' && auth.user) {
    editForm.display_name = auth.user.display_name || ''
    editForm.avatar_url = auth.user.avatar_url || ''
    editForm.bio = auth.user.bio || ''
    editForm.timezone = auth.user.timezone || 'UTC'
  }
})

function isValidUrl(val: string): boolean {
  try {
    new URL(val)
    return true
  } catch {
    return false
  }
}

async function saveProfile(): Promise<void> {
  isSavingProfile.value = true
  profileSaveStatus.value = 'idle'
  try {
    const { data } = await api.patch('/api/v1/users/me', {
      display_name: editForm.display_name || null,
      avatar_url: editForm.avatar_url || null,
      bio: editForm.bio || null,
      timezone: editForm.timezone,
    })
    auth.user = data
    profileSaveStatus.value = 'success'
  } catch {
    profileSaveStatus.value = 'error'
  } finally {
    isSavingProfile.value = false
    setTimeout(() => { profileSaveStatus.value = 'idle' }, 3000)
  }
}

async function changePassword(): Promise<void> {
  isSavingPassword.value = true
  passwordSaveStatus.value = 'idle'
  try {
    await api.post('/api/v1/auth/change-password', {
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
      new_password_confirm: passwordForm.new_password_confirm,
    })
    passwordSaveStatus.value = 'success'
    // Clear form
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.new_password_confirm = ''
  } catch {
    passwordSaveStatus.value = 'error'
  } finally {
    isSavingPassword.value = false
    setTimeout(() => { passwordSaveStatus.value = 'idle' }, 3000)
  }
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>
