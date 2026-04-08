<template>
  <header class="chat-header">
    <h1 class="chat-title">Redmine Chat Assist</h1>
    <span class="chat-subtitle">AI Assistant</span>
  </header>
</template>

<style scoped>
.chat-header {
  padding: var(--space-md) var(--space-lg);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
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
</style>
