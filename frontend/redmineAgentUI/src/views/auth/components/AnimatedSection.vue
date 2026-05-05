<script setup lang="ts">
import { computed } from 'vue';
import { useInView } from '../../../composables/useInView';

const props = withDefaults(defineProps<{ delay?: number }>(), { delay: 0 });

const { el, isVisible } = useInView();
void el;

const style = computed(() => ({
  transitionDelay: `${props.delay}ms`,
}));
</script>

<template>
  <div
    ref="el"
    :class="['transition-all duration-700', isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8']"
    :style="style"
  >
    <slot />
  </div>
</template>
