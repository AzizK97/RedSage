<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(defineProps<{
  variant?: 'default' | 'secondary' | 'outline' | 'destructive';
  class?: string;
  asChild?: boolean;
}>(), {
  variant: 'default',
});

const variantClass = computed(() => {
  switch (props.variant) {
    case 'secondary':
      return 'bg-surface-100 text-surface-800 border border-surface-200';
    case 'outline':
      return 'border border-surface-200 text-surface-700 bg-transparent';
    case 'destructive':
      return 'bg-red-50 text-red-700 border border-red-200';
    default:
      return 'bg-surface-900 text-white border border-surface-900';
  }
});
</script>

<template>
  <span :class="['inline-flex items-center rounded-full px-2.5 py-0.5 text-[10px] font-medium uppercase tracking-wider', variantClass, props.class]">
    <slot />
  </span>
</template>
