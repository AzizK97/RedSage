<script setup lang="ts">
const props = defineProps<{
  role: "admin" | "project_manager";
}>();

const emit = defineEmits<{
  (event: "logout"): void;
}>();
</script>

<template>
  <header class="chat-header">
    <div>
      <h1 class="chat-title">Redmine Chat Assist</h1>
      <span class="chat-subtitle">{{ props.role === "admin" ? "Admin session" : "Project manager session" }}</span>
    </div>
    <button class="logout-btn" type="button" @click="emit('logout')">Log out</button>
  </header>
</template>

<style scoped>
.chat-header {
  padding: var(--space-md) var(--space-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
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

.logout-btn {
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  padding: 0.45rem 0.75rem;
  font-size: var(--text-sm);
  background: var(--bg-tertiary);
  color: var(--text-primary);
  cursor: pointer;
}
</style>
