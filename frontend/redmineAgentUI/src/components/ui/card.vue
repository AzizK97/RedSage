<script setup lang="ts">
const props = defineProps<{ class?: string; accent?: 'sage' | 'copper' | 'amber' | 'red' | 'blue' | string }>();
</script>

<template>
  <div :data-accent="props.accent" :class="['stat-card', props.class]">
    <div class="card-body"><slot /></div>
  </div>
</template>

