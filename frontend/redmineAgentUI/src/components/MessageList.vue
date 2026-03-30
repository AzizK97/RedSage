<script setup lang="ts">
import type { Message } from "../types";

defineProps<{
  messages: Message[];
}>();

function formatTime(ts: number) {
  return new Date(ts).toLocaleTimeString();
}
</script>

<template>
  <div class="list">
    <div
      v-for="(msg, idx) in messages"
      :key="idx"
      class="row"
      :class="msg.role === 'user' ? 'user' : 'assistant'"
    >
      <div class="bubble">
        <p>{{ msg.content }}</p>
        <small>{{ formatTime(msg.timestamp) }}</small>
      </div>
    </div>
  </div>
</template>

<style scoped>
.list {
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 0.75rem;
  background: #fafafa;
}
.row {
  display: flex;
  margin-bottom: 0.75rem;
}
.row.user {
  justify-content: flex-end;
}
.row.assistant {
  justify-content: flex-start;
}
.bubble {
  max-width: 75%;
  padding: 0.6rem 0.8rem;
  border-radius: 10px;
  background: white;
  border: 1px solid #e5e7eb;
}
.row.user .bubble {
  background: #dbeafe;
  border-color: #bfdbfe;
}
small {
  display: block;
  margin-top: 0.35rem;
  color: #6b7280;
}
</style>