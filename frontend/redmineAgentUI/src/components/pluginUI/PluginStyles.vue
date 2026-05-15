<script setup lang="ts">
import '../../widget/chat-widget.css'
defineProps<{
  expanded?: boolean;
}>();
</script>

<template>
  <div class="plugin-styles-provider" :class="{ 'plugin-styles-provider--expanded': expanded }">
    <slot />
  </div>
</template>