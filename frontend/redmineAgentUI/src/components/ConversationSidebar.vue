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
  width: 300px;
  min-width: 300px;
  height: 100%;
  background: #1f2937;
  border-right: 1px solid #374151;
  color: #f9fafb;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid #374151;
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: center;
}

h2 {
  margin: 0;
  font-size: 1rem;
}

p {
  margin: 0.15rem 0 0;
  color: #9ca3af;
  font-size: 0.8rem;
}

.new-btn {
  border: 1px solid #3b82f6;
  background: #3b82f6;
  color: white;
  border-radius: 0.65rem;
  padding: 0.45rem 0.8rem;
  cursor: pointer;
}

.conversation-list {
  padding: 0.75rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.conversation-item {
  width: 100%;
  border: 1px solid #374151;
  background: #111827;
  color: #f9fafb;
  border-radius: 0.85rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.conversation-select {
  text-align: left;
  width: 100%;
  border: 0;
  background: transparent;
  color: inherit;
  padding: 0.85rem;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.conversation-item.active {
  border-color: #60a5fa;
  background: #172554;
}

.conversation-item.active .conversation-select {
  background: #172554;
}

.conversation-meta {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.conversation-meta strong {
  font-size: 0.92rem;
}

.conversation-meta small {
  color: #cbd5e1;
  line-height: 1.35;
}

.conversation-time {
  color: #9ca3af;
  font-size: 0.72rem;
}

.conversation-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.delete-btn {
  margin: 0 0.85rem 0.85rem;
  border: 1px solid #7f1d1d;
  background: rgba(127, 29, 29, 0.35);
  color: #fecaca;
  border-radius: 0.55rem;
  padding: 0.35rem 0.6rem;
  cursor: pointer;
  font-size: 0.72rem;
}
</style>
