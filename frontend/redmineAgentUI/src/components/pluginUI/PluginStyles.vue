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

<style scoped>
.plugin-styles-provider {
  --plugin-width: 360px;
  --plugin-height: 700px;
  --plugin-z-index: 40;
  --plugin-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
  --plugin-radius: 20px;

  width: var(--plugin-width);
  max-width: 95vw;
  height: var(--plugin-height);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  border-radius: var(--plugin-radius);
  box-shadow: var(--plugin-shadow);
  z-index: var(--plugin-z-index);
  overflow-y: auto;
  transition: width 0.3s ease, height 0.3s ease;
}

.plugin-styles-provider--expanded {
  /* --plugin-width: 800px; */
  width: 800px;
  /* --plugin-height: 85vh; */
  height: 85vh;
}

@media (max-width: 1024px) {
  .plugin-styles-provider--expanded {
    width:90vw;
  }
}

@media (max-width: 480px) {
  .plugin-styles-provider,
  .plugin-styles-provider--expanded {
    width: 100vw;
    max-width: 100vw;
    height: 100vh;
    max-height: 100vh;
    border-radius: 24px 24px 0 0;
  }
}
</style>