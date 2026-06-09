<template>
  <div class="section-header">
    <h2 class="section-title">{{ title }}</h2>
    <slot name="actions"></slot>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
}>()
</script>

<style scoped lang="scss">
@use 'src/css/tokens' as *;

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: $space-4;

  .section-title {
    font-size: $font-size-xl;
    font-weight: 700;
    color: $text-primary;
    margin: 0;
  }
}
</style>
