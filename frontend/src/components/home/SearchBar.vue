<template>
  <div class="search-bar-wrapper">
    <div class="search-input-wrapper">
      <input
        ref="inputRef"
        v-model="localQuery"
        type="text"
        class="search-input"
        :placeholder="placeholder"
        @input="onInput"
        @keydown.enter="onEnter"
        @focus="onFocus"
        @blur="onBlur"
      />
      <button
        v-if="localQuery.length > 0"
        class="search-clear-btn"
        @click="onClear"
        aria-label="Clear search"
      >
        ✕
      </button>
      <span v-else class="search-icon">🔍</span>
    </div>

    <!-- Autocomplete dropdown -->
    <Transition name="dropdown">
      <div v-if="showDropdown && localQuery.length > 0" class="search-dropdown" @mousedown.prevent>
        <div v-if="searchLoading" class="dropdown-loading">
          <span class="spinner" />
          Searching...
        </div>
        <template v-else-if="searchError">
          <div class="dropdown-error">{{ searchError }}</div>
        </template>
        <template v-else-if="searchResults.length === 0">
          <div class="dropdown-empty">No results found</div>
        </template>
        <template v-else>
          <div
            v-for="item in searchResults"
            :key="item.id"
            class="dropdown-item"
            @click="onSelect(item)"
          >
            <img
              v-if="item.coverImage"
              :src="item.coverImage"
              :alt="item.title"
              class="dropdown-item-cover"
              loading="lazy"
            />
            <div v-else class="dropdown-item-cover placeholder" />
            <div class="dropdown-item-info">
              <div class="dropdown-item-title">{{ item.title }}</div>
              <div class="dropdown-item-meta">
                <span class="meta-type">{{ item.mediaType }}</span>
                <span v-if="item.format" class="meta-format">{{ item.format }}</span>
              </div>
            </div>
          </div>
        </template>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { api } from 'src/boot/axios'
import { mapApiMediaToMediaItem } from 'src/types/home'
import type { MediaItem } from 'src/types/media'

const props = withDefaults(defineProps<{
  placeholder?: string
  debounceMs?: number
}>(), {
  placeholder: 'Search anime, manga, manhwa...',
  debounceMs: 300,
})

const emit = defineEmits<{
  submit: [query: string]
  select: [item: MediaItem]
}>()

const router = useRouter()
const inputRef = ref<HTMLInputElement | null>(null)
const localQuery = ref('')
const showDropdown = ref(false)
const searchResults = ref<MediaItem[]>([])
const searchLoading = ref(false)
const searchError = ref<string | null>(null)
let debounceTimer: ReturnType<typeof setTimeout> | null = null

function onInput(): void {
  showDropdown.value = true
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    if (localQuery.value.trim().length > 0) {
      fetchResults(localQuery.value.trim())
    } else {
      searchResults.value = []
      searchLoading.value = false
      searchError.value = null
    }
  }, props.debounceMs)
}

function onEnter(): void {
  showDropdown.value = false
  emit('submit', localQuery.value.trim())
  router.push({ name: 'search', query: { q: localQuery.value.trim() } }).catch(() => undefined)
}

function onClear(): void {
  localQuery.value = ''
  searchResults.value = []
  searchError.value = null
  searchLoading.value = false
  showDropdown.value = false
  inputRef.value?.focus()
}

function onFocus(): void {
  if (localQuery.value.length > 0) {
    showDropdown.value = true
  }
}

function onBlur(): void {
  // Delay to allow click on dropdown item
  setTimeout(() => {
    showDropdown.value = false
  }, 200)
}

function onSelect(item: MediaItem): void {
  showDropdown.value = false
  localQuery.value = ''
  searchResults.value = []
  emit('select', item)
  router.push({ name: 'media-detail', params: { id: item.id } }).catch(() => undefined)
}

async function fetchResults(query: string): Promise<void> {
  searchLoading.value = true
  searchError.value = null
  try {
    const { data } = await api.get<{ items: Record<string, unknown>[] }>('/api/v1/media/search', {
      params: { query, limit: 5 },
    })
    searchResults.value = (data.items ?? []).map(mapApiMediaToMediaItem)
  } catch {
    searchError.value = 'Search failed'
    searchResults.value = []
  } finally {
    searchLoading.value = false
  }
}
</script>

<style scoped lang="scss">
@use 'src/css/tokens' as *;

.search-bar-wrapper {
  position: relative;
  flex: 1;
  max-width: 480px;
  margin: 0 $space-3;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  background: $bg-elevated;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: $radius-full;
  padding: 0 $space-3;
  transition: border-color $transition;

  &:focus-within {
    border-color: $accent-primary;
  }
}

.search-input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: $text-primary;
  font-size: $font-size-sm;
  padding: $space-2 0;
  min-width: 0;

  &::placeholder {
    color: $text-muted;
  }
}

.search-icon {
  color: $text-muted;
  font-size: $font-size-sm;
}

.search-clear-btn {
  background: none;
  border: none;
  color: $text-muted;
  cursor: pointer;
  font-size: $font-size-xs;
  padding: 0;
  line-height: 1;

  &:hover {
    color: $text-primary;
  }
}

// Dropdown
.search-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: $bg-elevated;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: $radius-md;
  max-height: 360px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.dropdown-loading,
.dropdown-error,
.dropdown-empty {
  padding: $space-4;
  text-align: center;
  color: $text-muted;
  font-size: $font-size-sm;
}

.dropdown-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $space-2;
}

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top-color: $accent-primary;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.dropdown-item {
  display: flex;
  gap: $space-2;
  padding: $space-2 $space-3;
  cursor: pointer;
  transition: background $transition;

  &:hover {
    background: $bg-hover;
  }

  &:not(:last-child) {
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }
}

.dropdown-item-cover {
  width: 36px;
  height: 52px;
  border-radius: $radius-sm;
  object-fit: cover;
  flex-shrink: 0;

  &.placeholder {
    background: $bg-hover;
  }
}

.dropdown-item-info {
  flex: 1;
  min-width: 0;
}

.dropdown-item-title {
  font-size: $font-size-sm;
  color: $text-primary;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-item-meta {
  display: flex;
  gap: $space-2;
  margin-top: 2px;

  .meta-type,
  .meta-format {
    font-size: 11px;
    color: $text-muted;
    text-transform: uppercase;
  }
}

// Transition
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
