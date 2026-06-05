<template>
  <q-item clickable v-ripple @click="$emit('click')">
    <q-item-section avatar>
      <q-avatar :color="avatarColor" text-color="white" size="36px">
        {{ avatarInitial }}
      </q-avatar>
    </q-item-section>

    <q-item-section>
      <q-item-label class="text-body2">
        <span class="text-weight-medium">{{ eventLabel }}</span>
      </q-item-label>
      <q-item-label caption>
        <span v-if="newStatus" class="text-primary text-weight-medium">{{ newStatus }}</span>
        <span v-if="newProgress !== null && newProgress !== undefined">
          &nbsp;· {{ newProgress }} {{ unit }}
        </span>
        <span v-if="newScore !== null && newScore !== undefined">
          &nbsp;· Score: {{ newScore }}
        </span>
      </q-item-label>
      <q-item-label caption class="text-grey-7">
        {{ relativeTime }}
      </q-item-label>
    </q-item-section>

    <q-item-section v-if="note" side>
      <q-icon name="chat_bubble_outline" color="grey-5" size="sm" />
    </q-item-section>
  </q-item>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import type { FeedActivityItem } from 'src/types/social'

const props = defineProps<{
  item: FeedActivityItem
}>()

defineEmits<{
  click: []
}>()

const avatarColor = computed(() => {
  const colors = ['primary', 'secondary', 'accent', 'positive', 'info', 'warning']
  const index = (props.item.user_id.charCodeAt(0) + props.item.user_id.length) % colors.length
  return colors[index]
})

const avatarInitial = computed(() => {
  // Use first char of event_type as fallback avatar indicator
  return props.item.event_type.charAt(0).toUpperCase()
})

const eventLabel = computed(() => {
  switch (props.item.event_type) {
    case 'status_changed':
      return `Changed status to ${props.item.new_status ?? 'unknown'}`
    case 'progress_updated':
      return `Updated progress${
        props.item.new_status ? ` (${props.item.new_status})` : ''
      }`
    case 'score_set':
      return `Set score to ${props.item.new_score ?? 'N/A'}`
    case 'added':
      return `Added to list`
    case 'removed':
      return `Removed from list`
    default:
      return props.item.event_type.replace(/_/g, ' ')
  }
})

const unit = computed(() => {
  // Rough guess: events with status like 'reading' are likely manga chapters
  return props.item.new_status === 'reading' || props.item.new_status === 'rereading'
    ? 'ch.'
    : 'ep.'
})

const newStatus = computed(() => props.item.new_status)
const newProgress = computed(() => props.item.new_progress)
const newScore = computed(() => props.item.new_score)
const note = computed(() => props.item.note)

const relativeTime = computed(() => {
  const now = Date.now()
  const created = new Date(props.item.created_at).getTime()
  const diffMs = now - created
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return new Date(props.item.created_at).toLocaleDateString()
})
</script>
