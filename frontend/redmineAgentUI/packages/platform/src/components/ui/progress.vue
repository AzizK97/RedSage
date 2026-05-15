<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(defineProps<{
  modelValue?: number;
  class?: string;
}>(), {
  modelValue: 0,
});

const value = computed(() => Math.max(0, Math.min(100, props.modelValue ?? 0)));
</script>

<template>
  <div :class="['relative h-2 w-full overflow-hidden rounded-full bg-surface-100', props.class]">
    <div
      class="h-full rounded-full bg-sage-500 transition-all duration-500 ease-out"
      :style="{ width: `${value}%` }"
    />
  </div>
</template>
