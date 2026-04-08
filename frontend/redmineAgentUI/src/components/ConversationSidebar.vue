<script setup lang="ts">
import type { ConversationSummary } from "../composables/useThreads";

const props = defineProps<{
  conversations: ConversationSummary[];
  activeThreadId: string;
}>();

const emit = defineEmits<{
  (e: "select", threadId: string): void;
  (e: "new"): void;
  (e: "delete", threadId: string): void;
}>();

function formatTime(timestamp: number) {
  return new Date(timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div>
        <h2>Conversations</h2>
        <p>Previous chats</p>
      </div>

      <button class="new-btn" @click="emit('new')">New</button>
    </div>

    <div class="conversation-list">
      <div
        v-for="conversation in props.conversations"
        :key="conversation.id"
        class="conversation-item"
        :class="{ active: conversation.id === props.activeThreadId }"
      >
        <button class="conversation-select" type="button" @click="emit('select', conversation.id)">
          <div class="conversation-meta">
            <strong>{{ conversation.title }}</strong>
            <small>{{ conversation.preview }}</small>
          </div>
          <span class="conversation-time">{{ formatTime(conversation.updatedAt) }}</span>
        </button>

        <button
          class="delete-btn"
          type="button"
          @click="emit('delete', conversation.id)"
        >
          Delete
        </button>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 280px;
  min-width: 280px;
  height: 100%;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-subtle);
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  padding: var(--space-md) var(--space-lg);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  justify-content: space-between;
  gap: var(--space-md);
  align-items: flex-start;
}

h2 {
  margin: 0;
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
}

p {
  margin: 0.25rem 0 0;
  color: var(--text-secondary);
  font-size: var(--text-xs);
}

.new-btn {
  border: none;
  background: var(--accent-blue);
  color: white;
  border-radius: var(--radius-lg);
  padding: var(--space-sm) var(--space-md);
  cursor: pointer;
  font-size: var(--text-xs);
  font-weight: 500;
  white-space: nowrap;
  transition: all var(--transition-fast);
}

.new-btn:hover {
  background: var(--accent-blue-hover);
  transform: translateY(-1px);
}

.conversation-list {
  padding: var(--space-md);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.conversation-item {
  width: 100%;
  border: 1px solid var(--border-subtle);
  background: var(--bg-primary);
  color: var(--text-primary);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all var(--transition-fast);
}

.conversation-item:hover {
  border-color: var(--accent-blue);
  background: var(--bg-tertiary);
}

.conversation-select {
  text-align: left;
  width: 100%;
  border: 0;
  background: transparent;
  color: inherit;
  padding: var(--space-md);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  transition: all var(--transition-fast);
}

.conversation-item.active {
  border-color: var(--accent-blue);
  background: rgba(59, 130, 246, 0.1);
}

.conversation-item.active .conversation-select {
  background: transparent;
}

.conversation-meta {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.conversation-meta strong {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.conversation-meta small {
  color: var(--text-secondary);
  line-height: 1.4;
  font-size: var(--text-xs);
}

.conversation-time {
  color: var(--text-secondary);
  font-size: var(--text-xs);
}

.delete-btn {
  margin: 0 var(--space-md) var(--space-md);
  border: 0px solid white;
  background: rgba(106, 106, 106, 0.1);
  color: white;
  border-radius: var(--radius-md);
  padding: var(--space-xs) var(--space-md);
  cursor: pointer;
  font-size: var(--text-xs);
  font-weight: 400;
  transition: all var(--transition-fast);
}

.delete-btn:hover {
  background: rgba(198, 198, 198, 0.2);
}
</style>
