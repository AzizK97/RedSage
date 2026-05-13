<template>
  <div class="plugin-styles-provider" :class="{ 'plugin-styles-provider--expanded': expanded }">
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  expanded?: boolean;
}>();
</script>