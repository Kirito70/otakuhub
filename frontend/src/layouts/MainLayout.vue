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
      class="overflow-hidden"
    >
      <div class="column full-height overflow-hidden">
        <!-- Navigation items -->
        <q-list padding class="col overflow-auto">
          <q-item
            v-for="item in navItems"
            :key="item.name"
            :data-testid="`nav-${item.name}`"
            clickable
            v-ripple
            @click="go(item.name)"
          >
            <q-item-section avatar>
              <q-icon :name="item.icon" />
            </q-item-section>
            <q-item-section>{{ item.label }}</q-item-section>
          </q-item>
        </q-list>

        <!-- User section at bottom -->
        <q-separator />
        <q-list v-if="auth.isAuthenticated" padding class="overflow-hidden">
          <q-item clickable v-ripple>
            <q-item-section avatar>
              <q-avatar
                v-if="auth.user?.avatar_url"
                size="32px"
              >
                <img :src="auth.user.avatar_url" alt="avatar" />
              </q-avatar>
              <q-avatar v-else color="primary" size="32px" text-color="white">
                {{ auth.avatarInitial }}
              </q-avatar>
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ auth.displayName }}</q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-icon name="arrow_drop_down" />
            </q-item-section>

            <!-- Dropdown menu anchored to this q-item -->
            <q-menu anchor="top end" self="top start" :offset="[8, 0]">
              <q-list style="min-width: 200px">
                <q-item clickable v-close-popup @click="go('profile')" data-testid="menu-profile">
                  <q-item-section avatar>
                    <q-icon name="person" />
                  </q-item-section>
                  <q-item-section>Profile</q-item-section>
                </q-item>
                <q-item clickable v-close-popup @click="userDetailsDialog = true" data-testid="menu-details">
                  <q-item-section avatar>
                    <q-icon name="info" />
                  </q-item-section>
                  <q-item-section>Account Details</q-item-section>
                </q-item>
                <q-separator />
                <q-item clickable v-close-popup @click="onLogout" data-testid="menu-logout">
                  <q-item-section avatar>
                    <q-icon name="logout" />
                  </q-item-section>
                  <q-item-section>Logout</q-item-section>
                </q-item>
              </q-list>
            </q-menu>
          </q-item>
        </q-list>
        <q-list v-else padding>
          <q-item clickable v-ripple @click="go('login')" data-testid="nav-login">
            <q-item-section avatar>
              <q-icon name="login" />
            </q-item-section>
            <q-item-section>Log In</q-item-section>
          </q-item>
        </q-list>
      </div>
    </q-drawer>

    <!-- Account Details dialog -->
    <q-dialog v-model="userDetailsDialog">
      <q-card style="min-width: 340px; max-width: 420px">
        <q-card-section class="text-center">
          <q-avatar
            v-if="auth.user?.avatar_url"
            size="64px"
            class="q-mb-sm"
          >
            <img :src="auth.user.avatar_url" alt="avatar" />
          </q-avatar>
          <q-avatar v-else color="primary" size="64px" text-color="white" class="q-mb-sm">
            {{ auth.avatarInitial }}
          </q-avatar>
          <div class="text-h6">{{ auth.displayName }}</div>
          <div class="text-caption text-grey-7">@{{ auth.user?.username }}</div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-list dense>
            <q-item>
              <q-item-section>
                <q-item-label caption>Email</q-item-label>
                <q-item-label>{{ auth.user?.email }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item v-if="auth.user?.bio">
              <q-item-section>
                <q-item-label caption>Bio</q-item-label>
                <q-item-label>{{ auth.user.bio }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item>
              <q-item-section>
                <q-item-label caption>Timezone</q-item-label>
                <q-item-label>{{ auth.user?.timezone ?? 'UTC' }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item>
              <q-item-section>
                <q-item-label caption>Member since</q-item-label>
                <q-item-label>{{ memberSince }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Close" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-page-container>
      <router-view />
    </q-page-container>

    <q-footer v-if="$q.screen.lt.md" bordered>
      <q-tabs :model-value="activeTab" align="justify" indicator-color="primary">
        <q-route-tab
          v-for="item in mobileTabs"
          :key="item.name"
          :name="item.name"
          :icon="item.icon"
          :label="item.label"
          :to="tabRoute(item)"
          exact
        />
      </q-tabs>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useQuasar } from 'quasar'
import { useRoute, useRouter } from 'vue-router'
import type { RouteLocationRaw } from 'vue-router'

import { useTheme } from 'src/composables/useTheme'
import { useAuthStore } from 'src/stores/auth'

type NavRouteName =
  | 'discover'
  | 'my-list-status'
  | 'feed'
  | 'notifications'
  | 'watchparty'
  | 'profile'
  | 'login'

interface NavItem {
  name: NavRouteName
  label: string
  icon: string
  /** Override route location for items that need params. */
  route?: RouteLocationRaw
}

const $q = useQuasar()
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const leftDrawerOpen = ref(false)
const userDetailsDialog = ref(false)
const { isDark, toggleDarkMode } = useTheme()

function formatDate(iso: string | undefined): string {
  if (!iso) return 'Unknown'
  try {
    const d = new Date(iso)
    return d.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
  } catch {
    return 'Unknown'
  }
}

const memberSince = computed(() => formatDate(auth.user?.created_at))

const navItems: NavItem[] = [
  { name: 'discover', label: 'Discover', icon: 'search' },
  { name: 'my-list-status', label: 'My List', icon: 'list', route: { name: 'my-list-status', params: { status: 'watching' } } },
  { name: 'feed', label: 'Feed', icon: 'groups' },
  { name: 'watchparty', label: 'Watch Party', icon: 'live_tv' },
  { name: 'notifications', label: 'Notifications', icon: 'notifications' },
  { name: 'profile', label: 'Profile', icon: 'person' },
]

const mobileTabs: NavItem[] = [
  { name: 'discover', label: 'Discover', icon: 'search' },
  { name: 'my-list-status', label: 'My List', icon: 'list', route: { name: 'my-list-status', params: { status: 'watching' } } },
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

const activeTab = computed<string>(() => {
  const name = route.name
  if (typeof name === 'string') {
    const matched = mobileTabs.find(
      (tab) => name === tab.name || (tab.name === 'my-list-status' && name === 'my-list-status'),
    )
    if (matched) {
      return matched.name
    }
  }

  return 'discover'
})

function tabRoute(item: NavItem): RouteLocationRaw {
  return item.route ?? { name: item.name }
}

function go(name: NavRouteName): void {
  if (name === 'my-list-status') {
    router.push({ name: 'my-list-status', params: { status: 'watching' } }).catch(() => undefined)
  } else {
    router.push({ name }).catch(() => undefined)
  }

  if ($q.screen.lt.md) {
    leftDrawerOpen.value = false
  }
}

async function onLogout(): Promise<void> {
  await auth.logout()
  router.push({ name: 'login' }).catch(() => undefined)
}
</script>
