<template>
  <q-card bordered flat class="q-mb-md">
    <q-card-section class="row items-center q-gutter-sm">
      <q-avatar :color="direction === 'incoming' ? 'positive' : 'info'" text-color="white" size="32px">
        <q-icon :name="direction === 'incoming' ? 'arrow_downward' : 'arrow_upward'" size="sm" />
      </q-avatar>
      <div class="text-caption text-grey-7">
        <template v-if="direction === 'incoming'">
          Recommendation from <span class="text-weight-medium text-primary">#{{ rec.from_user_id.slice(0, 8) }}</span>
        </template>
        <template v-else>
          Sent to <span class="text-weight-medium text-primary">#{{ rec.to_user_id.slice(0, 8) }}</span>
        </template>
        <span class="q-ml-xs">· {{ relativeTime }}</span>
      </div>
    </q-card-section>

    <q-card-section v-if="rec.message" class="q-pt-none">
      <q-item-label class="text-body2 text-italic">"{{ rec.message }}"</q-item-label>
    </q-card-section>

    <q-card-section class="q-pt-none">
      <q-item-label caption>
        Media: <span class="text-weight-medium">{{ rec.media_id.slice(0, 8) }}...</span>
      </q-item-label>
      <q-item-label v-if="rec.is_acknowledged" caption class="text-positive">
        <q-icon name="check_circle" size="xs" class="q-mr-xs" />
        Acknowledged
      </q-item-label>
    </q-card-section>

    <q-separator />

    <q-card-actions align="right" class="q-pa-sm">
      <q-btn
        v-if="direction === 'incoming' && !rec.is_acknowledged"
        flat
        dense
        color="primary"
        label="Acknowledge"
        :loading="isAcknowledging"
        :disable="isAcknowledging"
        @click="$emit('acknowledge')"
      />
      <q-btn
        flat
        dense
        color="secondary"
        label="View Media"
        @click="$emit('view-media')"
      />
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import type { Recommendation } from 'src/types/social'

const props = defineProps<{
  rec: Recommendation
  direction: 'incoming' | 'sent'
  isAcknowledging?: boolean
}>()

defineEmits<{
  acknowledge: []
  'view-media': []
}>()

const relativeTime = computed(() => {
  const now = Date.now()
  const created = new Date(props.rec.created_at).getTime()
  const diffMs = now - created
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return new Date(props.rec.created_at).toLocaleDateString()
})
</script>
