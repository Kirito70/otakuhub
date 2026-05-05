<template>
  <div class="row items-center q-gutter-sm">
    <q-rating v-model="starValue" size="1.2em" max="10" color="amber" @update:model-value="onStarChange" />
    <q-input
      v-model.number="localValue"
      type="number"
      dense
      outlined
      style="max-width: 90px"
      min="0"
      max="10"
      step="0.5"
      @blur="emitUpdate"
      @keyup.enter="emitUpdate"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

const props = defineProps<{
  modelValue: number | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: number | null): void
  (e: 'change', value: number | null): void
}>()

const localValue = ref<number | null>(props.modelValue)

watch(
  () => props.modelValue,
  (next) => {
    localValue.value = next
  },
)

const starValue = computed({
  get: () => localValue.value ?? 0,
  set: (value: number) => {
    localValue.value = value
    emitUpdate()
  },
})

function onStarChange(value: number): void {
  localValue.value = value
  emitUpdate()
}

function emitUpdate(): void {
  if (localValue.value === null || !Number.isFinite(localValue.value)) {
    emit('update:modelValue', null)
    emit('change', null)
    return
  }

  const bounded = Math.max(0, Math.min(10, localValue.value))
  const rounded = Math.round(bounded * 2) / 2
  localValue.value = rounded
  emit('update:modelValue', rounded)
  emit('change', rounded)
}
</script>
