<template>
  <q-layout view="lHh Lpr lFf">
    <q-header bordered>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="leftDrawerOpen = !leftDrawerOpen"
        />
        <q-toolbar-title>OtakuHub</q-toolbar-title>
        <q-btn flat dense round :icon="isDark ? 'dark_mode' : 'light_mode'" aria-label="Toggle theme" @click="toggleDarkMode" />
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      :show-if-above="$q.screen.gt.sm"
      :mini="$q.screen.md"
      bordered
      :width="240"
    >
      <q-list padding>
        <q-item v-for="item in navItems" :key="item.name" clickable v-ripple @click="go(item.name)">
          <q-item-section avatar>
            <q-icon :name="item.icon" />
          </q-item-section>
          <q-item-section>{{ item.label }}</q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>

    <q-footer v-if="$q.screen.lt.md" bordered>
      <q-tabs :model-value="activeTab" align="justify" indicator-color="primary">
        <q-tab v-for="item in mobileTabs" :key="item.name" :name="item.name" :icon="item.icon" :label="item.label" @click="go(item.name)" />
      </q-tabs>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useQuasar } from 'quasar'
import { useRoute, useRouter } from 'vue-router'

import { useTheme } from 'src/composables/useTheme'

type RouteName =
  | 'discover'
  | 'my-list'
  | 'feed'
  | 'notifications'
  | 'watchparty'
  | 'profile'

interface NavItem {
  name: RouteName
  label: string
  icon: string
}

const $q = useQuasar()
const route = useRoute()
const router = useRouter()
const leftDrawerOpen = ref(false)
const { isDark, toggleDarkMode } = useTheme()

const navItems: NavItem[] = [
  { name: 'discover', label: 'Discover', icon: 'search' },
  { name: 'my-list', label: 'My List', icon: 'list' },
  { name: 'feed', label: 'Feed', icon: 'groups' },
  { name: 'watchparty', label: 'Watch Party', icon: 'live_tv' },
  { name: 'notifications', label: 'Notifications', icon: 'notifications' },
  { name: 'profile', label: 'Profile', icon: 'person' },
]

const mobileTabs: NavItem[] = [
  { name: 'discover', label: 'Discover', icon: 'search' },
  { name: 'my-list', label: 'My List', icon: 'list' },
  { name: 'feed', label: 'Feed', icon: 'groups' },
  { name: 'notifications', label: 'Alerts', icon: 'notifications' },
]

watch(
  () => $q.screen.lt.md,
  (isMobile) => {
    leftDrawerOpen.value = !isMobile
  },
  { immediate: true },
)

const activeTab = computed<RouteName>(() => {
  const name = route.name
  if (typeof name === 'string') {
    const matched = mobileTabs.find((tab) => tab.name === name)
    if (matched) {
      return matched.name
    }
  }

  return 'discover'
})

function go(name: RouteName): void {
  router.push({ name }).catch(() => undefined)
  leftDrawerOpen.value = false
}
</script>
