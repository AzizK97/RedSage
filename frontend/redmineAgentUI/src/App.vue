<script setup lang="ts">
import ChatInterface from "./components/ChatInterface.vue";
</script>

<template>
  <main class="app-shell">
    <ChatInterface />
  </main>
</template>

<style scoped>
.app-shell {
  max-width: 900px;
  margin: 0 auto;
  padding: 1rem;
  height: 100vh;
  box-sizing: border-box;
}
</style>