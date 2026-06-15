<template>
  <div class="flex h-14 items-center justify-around bg-[#111111] border-t border-[#1f2937] px-2">
    <button
      v-for="item in mobileNav"
      :key="item.name"
      class="flex flex-col items-center gap-0.5 px-3 py-1 text-xs transition-colors"
      :class="isActive(item.name) ? 'text-purple-400' : 'text-[#6b7280] hover:text-[#a1a1aa]'"
      @click="go(item)"
    >
      <component :is="item.icon" class="h-5 w-5" />
      <span>{{ item.label }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { Home, Search, List, Users, User } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const mobileNav = [
  { name: 'home', label: 'Home', icon: Home },
  { name: 'discover', label: 'Discover', icon: Search },
  { name: 'my-list-status', label: 'List', icon: List, params: { status: 'watching' } },
  { name: 'feed', label: 'Feed', icon: Users },
  { name: 'profile', label: 'Profile', icon: User },
]

function isActive(name: string): boolean {
  return route.name === name || String(route.name).startsWith(name)
}

function go(item: typeof mobileNav[number]): void {
  if (item.params) {
    router.push({ name: item.name, params: item.params })
  } else {
    router.push({ name: item.name })
  }
}
</script>
