<template>
  <div class="min-h-screen bg-[#0a0a0a] text-white">
    <!-- Mobile sidebar overlay -->
    <Transition name="fade">
      <div
        v-if="mobileNavOpen"
        class="fixed inset-0 z-50 bg-black/50 lg:hidden"
        @click="mobileNavOpen = false"
      />
    </Transition>

    <!-- Mobile sidebar drawer -->
    <Transition name="slide">
      <div
        v-if="mobileNavOpen"
        class="fixed inset-y-0 left-0 z-50 w-64 lg:hidden"
      >
        <Sidebar />
      </div>
    </Transition>

    <!-- Desktop sidebar (lg+) -->
    <aside class="fixed left-0 top-0 z-30 h-full w-60 hidden lg:block">
      <Sidebar />
    </aside>

    <!-- Main content area -->
    <div class="lg:pl-60 flex flex-col min-h-screen">
      <TopBar @toggle-mobile-nav="mobileNavOpen = !mobileNavOpen" />

      <main class="flex-1">
        <router-view />
      </main>
    </div>

    <!-- Mobile bottom navigation -->
    <nav class="fixed bottom-0 left-0 right-0 z-40 lg:hidden">
      <BottomNav />
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Sidebar from './Sidebar.vue'
import TopBar from './TopBar.vue'
import BottomNav from './BottomNav.vue'

const mobileNavOpen = ref(false)
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.2s ease;
}
.slide-enter-from {
  transform: translateX(-100%);
}
.slide-leave-to {
  transform: translateX(-100%);
}
</style>
