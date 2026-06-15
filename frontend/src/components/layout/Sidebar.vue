<template>
  <div class="flex h-full flex-col bg-[#111111] border-r border-[#1f2937]">
    <!-- Brand -->
    <div class="flex h-14 items-center px-4 border-b border-[#1f2937]">
      <h1 class="text-lg font-bold text-white">
        <span class="text-purple-400">Otaku</span>Hub
      </h1>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 overflow-y-auto p-2 space-y-1">
      <button
        v-for="item in navItems"
        :key="item.name"
        :data-testid="`nav-${item.name}`"
        class="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-[#a1a1aa] hover:bg-[#222222] hover:text-white transition-colors"
        :class="{ 'bg-[#222222] text-white': isActive(item.name) }"
        @click="go(item.name)"
      >
        <component :is="item.icon" class="h-5 w-5 shrink-0" />
        <span>{{ item.label }}</span>
      </button>
    </nav>

    <!-- User section -->
    <div class="border-t border-[#1f2937] p-2">
      <button
        class="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-[#a1a1aa] hover:bg-[#222222] hover:text-white transition-colors"
        @click="go('profile')"
      >
        <div class="h-8 w-8 rounded-full bg-purple-500 flex items-center justify-center text-xs font-bold text-white shrink-0">
          {{ auth.avatarInitial }}
        </div>
        <div class="flex-1 text-left truncate">
          <p class="text-white truncate">{{ auth.displayName }}</p>
          <p class="text-[#6b7280] text-xs truncate">{{ auth.user?.username }}</p>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Home,
  Search,
  List,
  Calendar,
  Download,
  Users,
  MessageSquare,
  Video,
  Bell,
  User,
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const navItems = [
  { name: 'home', label: 'Home', icon: Home },
  { name: 'discover', label: 'Discover', icon: Search },
  { name: 'my-list-status', label: 'My List', icon: List, params: { status: 'watching' } },
  { name: 'airing-calendar', label: 'Calendar', icon: Calendar },
  { name: 'import-list', label: 'Import', icon: Download },
  { name: 'feed', label: 'Feed', icon: Users },
  { name: 'recommendations', label: 'Recs', icon: MessageSquare },
  { name: 'discussions', label: 'Discussions', icon: MessageSquare },
  { name: 'watchparty', label: 'Watch Party', icon: Video },
  { name: 'notifications', label: 'Notifications', icon: Bell },
]

function isActive(name: string): boolean {
  return route.name === name || String(route.name).startsWith(name)
}

function go(name: string): void {
  const item = navItems.find(n => n.name === name)
  if (item?.params) {
    router.push({ name, params: item.params })
  } else {
    router.push({ name })
  }
}
</script>
