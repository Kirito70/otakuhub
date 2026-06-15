<template>
  <div class="p-4">
    <!-- Tabs -->
    <div class="flex gap-1 mb-4 border-b border-[#1f2937]">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        :class="[
          'px-4 py-2 text-sm font-medium transition-colors rounded-t-lg',
          activeTab === tab.key
            ? 'text-white border-b-2 border-purple-500'
            : 'text-[#6b7280] hover:text-[#a1a1aa]'
        ]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Overview Tab -->
    <div v-if="activeTab === 'overview'">
      <app-page-state
        :is-loading="!user"
        :error="null"
        :is-empty="!user"
      >
        <div v-if="user" class="flex gap-4 flex-col md:flex-row">
          <!-- Profile Card -->
          <div class="w-full md:w-1/3">
            <div class="rounded-lg bg-[#111111] border border-[#1f2937] overflow-hidden">
              <div class="p-4 flex flex-col items-center text-center">
                <div class="w-24 h-24 mb-4">
                  <img
                    v-if="user.avatar_url"
                    :src="user.avatar_url"
                    alt="Avatar"
                    class="w-24 h-24 rounded-full object-cover"
                  />
                  <div
                    v-else
                    class="w-24 h-24 rounded-full bg-purple-600 text-white text-2xl font-bold flex items-center justify-center"
                  >
                    {{ avatarInitial }}
                  </div>
                </div>
                <div class="text-lg font-semibold">{{ user.display_name || user.username }}</div>
                <div class="text-xs text-[#6b7280]">@{{ user.username }}</div>
              </div>
              <hr class="border-[#1f2937]" />
              <div class="p-4 space-y-1">
                <div class="text-sm mb-1">
                  <strong>Email:</strong> {{ user.email }}
                </div>
                <div class="text-sm mb-1">
                  <strong>Timezone:</strong> {{ user.timezone }}
                </div>
                <div class="text-sm mb-1">
                  <strong>Member since:</strong> {{ formatDate(user.created_at) }}
                </div>
              </div>
            </div>
          </div>

          <!-- Bio Card -->
          <div class="w-full md:w-2/3">
            <div class="rounded-lg bg-[#111111] border border-[#1f2937] overflow-hidden">
              <div class="p-4">
                <div class="text-base font-medium mb-2">Bio</div>
                <p v-if="user.bio" class="text-sm mt-2" style="white-space: pre-wrap">{{ user.bio }}</p>
                <p v-else class="text-[#6b7280] text-xs mt-2">No bio yet.</p>
              </div>
            </div>
          </div>
        </div>
      </app-page-state>
    </div>

    <!-- Edit Profile Tab -->
    <div v-if="activeTab === 'edit'">
      <div class="rounded-lg bg-[#111111] border border-[#1f2937] overflow-hidden">
        <div class="p-4">
          <form @submit.prevent="handleSaveProfile" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-[#a1a1aa] mb-1">Display Name</label>
              <input
                v-model="editForm.display_name"
                type="text"
                placeholder="Your display name"
                maxlength="100"
                class="w-full rounded-lg bg-[#0a0a0a] border border-[#1f2937] px-3 py-2 text-sm text-white placeholder:text-[#6b7280] focus:outline-none focus:border-purple-500 transition-colors"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-[#a1a1aa] mb-1">Avatar URL</label>
              <input
                v-model="editForm.avatar_url"
                type="url"
                placeholder="https://example.com/avatar.jpg"
                class="w-full rounded-lg bg-[#0a0a0a] border border-[#1f2937] px-3 py-2 text-sm text-white placeholder:text-[#6b7280] focus:outline-none focus:border-purple-500 transition-colors"
              />
              <p v-if="editErrors.avatar_url" class="text-xs text-red-400 mt-1">{{ editErrors.avatar_url }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#a1a1aa] mb-1">Bio</label>
              <textarea
                v-model="editForm.bio"
                placeholder="Tell us about yourself..."
                maxlength="1000"
                rows="3"
                class="w-full rounded-lg bg-[#0a0a0a] border border-[#1f2937] px-3 py-2 text-sm text-white placeholder:text-[#6b7280] focus:outline-none focus:border-purple-500 transition-colors resize-vertical"
              ></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#a1a1aa] mb-1">Timezone</label>
              <select
                v-model="editForm.timezone"
                class="w-full rounded-lg bg-[#0a0a0a] border border-[#1f2937] px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500 transition-colors"
              >
                <option v-for="tz in commonTimezones" :key="tz" :value="tz">{{ tz }}</option>
              </select>
            </div>

            <div class="flex justify-end">
              <button
                type="submit"
                :disabled="isSavingProfile"
                class="rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span v-if="isSavingProfile" class="inline-block animate-spin mr-2">⟳</span>
                Save Changes
              </button>
            </div>

            <div v-if="profileSaveStatus === 'success'" class="rounded bg-emerald-600 text-white px-3 py-2 text-sm mt-2">
              Profile updated successfully!
            </div>
            <div v-if="profileSaveStatus === 'error'" class="rounded bg-red-600 text-white px-3 py-2 text-sm mt-2">
              {{ editErrors._form || 'Failed to update profile. Please try again.' }}
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Account & Security Tab -->
    <div v-if="activeTab === 'security'">
      <div class="rounded-lg bg-[#111111] border border-[#1f2937] overflow-hidden">
        <div class="p-4">
          <div class="text-base font-medium mb-4">Change Password</div>
          <form @submit.prevent="handleChangePassword" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-[#a1a1aa] mb-1">Current Password *</label>
              <input
                v-model="passwordForm.current_password"
                type="password"
                placeholder="Current password"
                class="w-full rounded-lg bg-[#0a0a0a] border border-[#1f2937] px-3 py-2 text-sm text-white placeholder:text-[#6b7280] focus:outline-none focus:border-purple-500 transition-colors"
              />
              <p v-if="passwordErrors.current_password" class="text-xs text-red-400 mt-1">{{ passwordErrors.current_password }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#a1a1aa] mb-1">New Password *</label>
              <input
                v-model="passwordForm.new_password"
                type="password"
                placeholder="New password"
                class="w-full rounded-lg bg-[#0a0a0a] border border-[#1f2937] px-3 py-2 text-sm text-white placeholder:text-[#6b7280] focus:outline-none focus:border-purple-500 transition-colors"
              />
              <p v-if="passwordErrors.new_password" class="text-xs text-red-400 mt-1">{{ passwordErrors.new_password }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#a1a1aa] mb-1">Confirm New Password *</label>
              <input
                v-model="passwordForm.new_password_confirm"
                type="password"
                placeholder="Confirm new password"
                class="w-full rounded-lg bg-[#0a0a0a] border border-[#1f2937] px-3 py-2 text-sm text-white placeholder:text-[#6b7280] focus:outline-none focus:border-purple-500 transition-colors"
              />
              <p v-if="passwordErrors.new_password_confirm" class="text-xs text-red-400 mt-1">{{ passwordErrors.new_password_confirm }}</p>
            </div>

            <div class="flex justify-end">
              <button
                type="submit"
                :disabled="isSavingPassword"
                class="rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span v-if="isSavingPassword" class="inline-block animate-spin mr-2">⟳</span>
                Change Password
              </button>
            </div>

            <div v-if="passwordSaveStatus === 'success'" class="rounded bg-emerald-600 text-white px-3 py-2 text-sm mt-2">
              Password changed successfully!
            </div>
            <div v-if="passwordSaveStatus === 'error'" class="rounded bg-red-600 text-white px-3 py-2 text-sm mt-2">
              {{ passwordErrors._form || 'Failed to change password. Check your current password and try again.' }}
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { z } from 'zod'

import { api } from 'src/boot/axios'
import AppPageState from 'src/components/AppPageState.vue'
import { useAuthStore } from 'src/stores/auth'

const auth = useAuthStore()

const tabs = [
  { key: 'overview', label: 'Overview' },
  { key: 'edit', label: 'Edit Profile' },
  { key: 'security', label: 'Account & Security' },
] as const

const activeTab = ref<'overview' | 'edit' | 'security'>('overview')

const user = computed(() => auth.user)

const avatarInitial = computed(() => {
  const name = user.value?.display_name || user.value?.username || 'U'
  return name.charAt(0).toUpperCase()
})

const editForm = reactive({
  display_name: '',
  avatar_url: '',
  bio: '',
  timezone: 'UTC',
})
const editErrors = reactive<Record<string, string>>({})
const isSavingProfile = ref(false)
const profileSaveStatus = ref<'idle' | 'success' | 'error'>('idle')

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  new_password_confirm: '',
})
const passwordErrors = reactive<Record<string, string>>({})
const isSavingPassword = ref(false)
const passwordSaveStatus = ref<'idle' | 'success' | 'error'>('idle')

const commonTimezones = [
  'UTC', 'America/New_York', 'America/Chicago', 'America/Denver',
  'America/Los_Angeles', 'Europe/London', 'Europe/Berlin', 'Europe/Paris',
  'Asia/Tokyo', 'Asia/Seoul', 'Asia/Shanghai', 'Asia/Kolkata',
  'Australia/Sydney', 'Pacific/Auckland',
]

const profileSchema = z.object({
  display_name: z.string().max(100).optional().or(z.literal('')),
  avatar_url: z.string().url('Must be a valid URL').optional().or(z.literal('')),
  bio: z.string().max(1000).optional().or(z.literal('')),
  timezone: z.string().min(1),
})

const passwordSchema = z.object({
  current_password: z.string().min(1, 'Current password is required'),
  new_password: z.string().min(8, 'Password must be at least 8 characters'),
  new_password_confirm: z.string().min(1, 'Please confirm your new password'),
}).refine(data => data.new_password === data.new_password_confirm, {
  message: 'Passwords do not match',
  path: ['new_password_confirm'],
})

// Hydrate edit form when switching to edit tab
import { watch } from 'vue'

watch(activeTab, (tab) => {
  if (tab === 'edit' && auth.user) {
    editForm.display_name = auth.user.display_name || ''
    editForm.avatar_url = auth.user.avatar_url || ''
    editForm.bio = auth.user.bio || ''
    editForm.timezone = auth.user.timezone || 'UTC'
    Object.keys(editErrors).forEach(k => delete editErrors[k])
  }
  if (tab === 'security') {
    Object.keys(passwordErrors).forEach(k => delete passwordErrors[k])
  }
})

function clearErrors(errors: Record<string, string>) {
  Object.keys(errors).forEach(k => delete errors[k])
}

async function handleSaveProfile(): Promise<void> {
  clearErrors(editErrors)
  const result = profileSchema.safeParse(editForm)
  if (!result.success) {
    for (const issue of result.error.issues) {
      const field = issue.path[0] as string
      editErrors[field] = issue.message
    }
    return
  }

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

async function handleChangePassword(): Promise<void> {
  clearErrors(passwordErrors)
  const result = passwordSchema.safeParse(passwordForm)
  if (!result.success) {
    for (const issue of result.error.issues) {
      const field = issue.path[0] as string
      passwordErrors[field] = issue.message
    }
    return
  }

  isSavingPassword.value = true
  passwordSaveStatus.value = 'idle'
  try {
    await api.post('/api/v1/auth/change-password', {
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
      new_password_confirm: passwordForm.new_password_confirm,
    })
    passwordSaveStatus.value = 'success'
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
