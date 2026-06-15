<template>
  <header class="sticky top-0 z-40 flex h-14 items-center gap-4 border-b border-[#1f2937] bg-[#0a0a0a]/95 backdrop-blur supports-[backdrop-filter]:bg-[#0a0a0a]/80 px-4">
    <!-- Mobile menu button -->
    <button
      class="lg:hidden p-2 text-[#a1a1aa] hover:text-white"
      @click="$emit('toggle-mobile-nav')"
    >
      <Menu class="h-5 w-5" />
    </button>

    <!-- Search bar -->
    <div class="flex-1 max-w-md">
      <div class="relative">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#6b7280]" />
        <input
          v-model="query"
          type="text"
          placeholder="Search anime, manga..."
          class="w-full rounded-lg bg-[#111111] border border-[#1f2937] py-2 pl-9 pr-4 text-sm text-white placeholder:text-[#6b7280] focus:outline-none focus:border-purple-500 transition-colors"
          @keydown.enter="search"
        />
      </div>
    </div>

    <div class="flex items-center gap-2">
      <!-- Notifications bell -->
      <button
        class="relative p-2 text-[#a1a1aa] hover:text-white transition-colors"
        @click="go('notifications')"
      >
        <Bell class="h-5 w-5" />
      </button>

      <!-- User avatar (desktop) -->
      <button
        class="hidden sm:flex items-center gap-2 rounded-lg px-2 py-1 text-sm hover:bg-[#222222] transition-colors"
        @click="go('profile')"
      >
        <div class="h-7 w-7 rounded-full bg-purple-500 flex items-center justify-center text-xs font-bold text-white">
          {{ auth.avatarInitial }}
        </div>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Menu, Search, Bell } from 'lucide-vue-next'

defineEmits<{
  'toggle-mobile-nav': []
}>()

const router = useRouter()
const auth = useAuthStore()
const query = ref('')

function search() {
  const q = query.value.trim()
  if (q) {
    router.push({ name: 'search', query: { q } })
    query.value = ''
  }
}

function go(name: string) {
  router.push({ name })
}
</script>
