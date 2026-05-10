<template>
  <div>
    <div v-if="isLoading" class="row justify-center q-my-lg">
      <q-spinner color="primary" size="34px" />
      <div class="q-ml-sm text-grey-7">{{ loadingLabel }}</div>
    </div>

    <q-banner v-else-if="error" class="bg-negative text-white q-mb-md" dense>
      {{ error }}
      <template #action>
        <q-btn
          v-if="showRetry"
          flat
          color="white"
          label="Retry"
          @click="$emit('retry')"
        />
      </template>
    </q-banner>

    <div v-else-if="isEmpty" class="text-grey-7 q-mt-md">
      {{ emptyLabel }}
    </div>

    <slot v-else />
  </div>
</template>

<script setup lang="ts">
defineEmits<{ (event: 'retry'): void }>()

withDefaults(
  defineProps<{
    isLoading: boolean
    error: string | null
    isEmpty: boolean
    loadingLabel?: string
    emptyLabel?: string
    showRetry?: boolean
  }>(),
  {
    loadingLabel: 'Loading... please wait.',
    emptyLabel: 'No results to display yet.',
    showRetry: true,
  },
)
</script>
