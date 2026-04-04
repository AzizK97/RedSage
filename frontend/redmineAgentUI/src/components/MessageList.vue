<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from "vue";
import type { Message } from "../types";
import MarkDownIt from "markdown-it";
import DOMPurify from "dompurify";

const props = defineProps<{
  messages: Message[];
}>();

const listRef = ref<HTMLElement | null>(null);

const md = new MarkDownIt({
  html: false,
  linkify: true,
  breaks: true,
});

function formatTime(ts: number) {
  return new Date(ts).toLocaleTimeString();
}

function renderMarkdown(text: string) {
  const raw = md.render(text || "");
  return DOMPurify.sanitize(raw);
}

async function scrollToBottom() {
  await nextTick();
  if (!listRef.value) return;
  listRef.value.scrollTop = listRef.value.scrollHeight;
}

watch(
  () => props.messages,
  () => {
    scrollToBottom();
  },
  { deep: true },
);

onMounted(() => {
  scrollToBottom();
});
</script>

<template>
  <div id="chat-container" ref="listRef" class="list">
    <div
      v-for="(msg, idx) in messages"
      :key="idx"
      class="row"
      :class="msg.role === 'user' ? 'user' : 'assistant'"
    >
      <div class="bubble">
        <p v-if="msg.role === 'user'" class="text">{{ msg.content }}</p>
        <div v-else class="md-content" v-html="renderMarkdown(msg.content)"></div>
        <small>{{ formatTime(msg.timestamp) }}</small>
      </div>
    </div>
  </div>
</template>

<style scoped>
.list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
  border-radius: 12px;
  background: #111827;
}

.row {
  display: flex;
  margin-bottom: 0.85rem;
}

.row.user {
  justify-content: flex-end;
}

.row.assistant {
  justify-content: flex-start;
}

.bubble {
  max-width: 75%;
  padding: 0.65rem 0.85rem;
  border-radius: 0.7rem;
}

.row.user .bubble {
  background: #2563eb;
  color: #fff;
}

.row.assistant .bubble {
  color: #fff;
}

small {
  display: block;
  margin-top: 0.35rem;
  color: #d1d5db;
  font-size: 0.75rem;
}

.text {
  white-space: pre-wrap;
  margin: 0;
}

:deep(.md-content table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0.85rem 0;
  background: #111827;
  border-radius: 0.5rem;
  overflow: hidden;
}

:deep(.md-content th) {
  background: #1f2937;
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #374151;
  color: #e5e7eb;
}

:deep(.md-content td) {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #374151;
  color: #e5e7eb;
}

:deep(.md-content p) {
  margin: 0.3rem 0;
}
</style>