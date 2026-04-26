<script setup lang="ts">
const props = defineProps<{
  role: "admin" | "project_manager";
}>();
</script>

<template>
  <header class="chat-header">
    <div>
      <h1 class="chat-title">Redmine Chat Assist</h1>
      <span class="chat-subtitle">{{ props.role === "admin" ? "Admin session" : "Project manager session" }}</span>
    </div>
  </header>
</template>

<style scoped>
.chat-header {
  padding: var(--space-md) var(--space-lg);
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.chat-title {
  margin: 0;
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.chat-subtitle {
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: 400;
}

</style>
