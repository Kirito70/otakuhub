<template>
  <q-dialog v-model="model">
    <q-card style="min-width: 320px; max-width: 480px; width: 100%">
      <q-card-section>
        <div class="text-h6">Add to list</div>
        <div class="text-caption text-grey-7">{{ title }}</div>
      </q-card-section>

      <q-card-section class="q-gutter-md">
        <q-select v-model="status" :options="statusOptions" label="Status" outlined />
        <q-input v-model.number="progress" type="number" label="Progress" outlined min="0" />
        <q-input v-model.number="score" type="number" label="Score (0-10)" outlined min="0" max="10" step="0.5" />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" @click="model = false" />
        <q-btn color="primary" label="Save" :loading="isSaving" @click="onSave" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useTrackingStore } from 'src/stores/tracking'
import type { WatchStatus } from 'src/types/tracking'

const props = defineProps<{
  modelValue: boolean
  mediaId: string
  title: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'saved'): void
}>()

const trackingStore = useTrackingStore()
const isSaving = ref(false)
const status = ref<WatchStatus>('plan_to_watch')
const progress = ref(0)
const score = ref<number | null>(null)

const statusOptions: WatchStatus[] = [
  'watching',
  'reading',
  'completed',
  'paused',
  'dropped',
  'plan_to_watch',
  'plan_to_read',
  'rewatching',
  'rereading',
]

const model = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value),
})

async function onSave(): Promise<void> {
  isSaving.value = true

  try {
    await trackingStore.addToList({
      media_id: props.mediaId,
      status: status.value,
      progress: progress.value,
      score: score.value ?? undefined,
    })

    emit('saved')
    model.value = false
  } finally {
    isSaving.value = false
  }
}
</script>
