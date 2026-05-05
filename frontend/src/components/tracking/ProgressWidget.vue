<template>
  <div class="row items-center q-gutter-sm">
    <q-btn dense flat round icon="remove" @click="decrement" />
    <q-input
      v-model.number="localValue"
      type="number"
      dense
      outlined
      style="max-width: 90px"
      min="0"
      @blur="emitUpdate"
      @keyup.enter="emitUpdate"
    />
    <q-btn dense flat round icon="add" @click="increment" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  modelValue: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: number): void
  (e: 'change', value: number): void
}>()

const localValue = ref(props.modelValue)

watch(
  () => props.modelValue,
  (next) => {
    localValue.value = next
  },
)

function increment(): void {
  localValue.value += 1
  emitUpdate()
}

function decrement(): void {
  localValue.value = Math.max(0, localValue.value - 1)
  emitUpdate()
}

function emitUpdate(): void {
  const safeValue = Number.isFinite(localValue.value) ? Math.max(0, Math.floor(localValue.value)) : 0
  localValue.value = safeValue
  emit('update:modelValue', safeValue)
  emit('change', safeValue)
}
</script>
