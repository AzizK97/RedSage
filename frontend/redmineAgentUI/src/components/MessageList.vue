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

// function formatTime(ts: number) {
//   return new Date(ts).toLocaleTimeString("en-US", {
//     hour: "2-digit",
//     minute: "2-digit",
//   });
// }

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
        
        <!-- <small>{{ formatTime(msg.timestamp) }}</small> -->
      </div>
    </div>
  </div>
</template>

<style scoped>
.list {
  flex: 1;
  overflow-y: auto;
  padding: 0 var(--space-md);
  background: var(--bg-primary);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  margin: 0 auto;
  width: min(100%, 850px);
  min-width: 640px;
}

.row {
  display: flex;
  animation: slideIn 200ms ease-out;
}

.row.user {
  justify-content: flex-end;
}

.row.assistant {
  justify-content: flex-start;
}

.bubble {
  max-width: 100%;
  padding: var(--space-md) var(--space-lg);
  word-wrap: break-word;
}

.row.user .bubble {
  background: #252525;
  border-radius: 20px;
  color: white;
}

.row.assistant .bubble {
  width: 100%;
  color: var(--text-primary);
}

small {
  display: block;
  margin-top: var(--space-sm);
  color: var(--text-secondary);
  font-size: var(--text-xs);
}

.text {
  white-space: pre-wrap;
  margin: 0;
  line-height: 1.6;
}

:deep(.md-content) {
  font-size: var(--text-base);
  line-height: 1.6;
}

:deep(.md-content p) {
  margin: var(--space-sm) 0;
}

:deep(.md-content h1),
:deep(.md-content h2),
:deep(.md-content h3) {
  margin: var(--space-md) 0 var(--space-sm);
  font-weight: 600;
  color: var(--text-primary);
}

:deep(.md-content ul),
:deep(.md-content ol) {
  margin: var(--space-sm) 0;
  padding-left: var(--space-lg);
}

:deep(.md-content li) {
  margin: var(--space-xs) 0;
}

:deep(.md-content table) {
  width: 100%;
  border-collapse: collapse;
  margin: var(--space-md) 0;
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  overflow: hidden;
  font-size: var(--text-xs);
}

:deep(.md-content th) {
  background: var(--bg-tertiary);
  padding: var(--space-md);
  text-align: left;
  font-weight: 600;
  border-bottom: 1px solid var(--bg-tertiary);
  color: var(--text-primary);
}

:deep(.md-content td) {
  padding: var(--space-md);
  border: 1px solid var(--bg-tertiary);
  color: var(--text-primary);
}

:deep(.md-content code) {
  background: var(--bg-secondary);
  color: var(--accent-green);
  padding: 0.125rem 0.375rem;
  border-radius: var(--radius-sm);
  font-family: 'Montserrat', 'Courier New', monospace;
  font-size: 0.85em;
}

:deep(.md-content pre) {
  background: var(--bg-secondary);
  color: var(--text-secondary);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  overflow-x: auto;
  font-size: var(--text-xs);
  line-height: 1.4;
}

:deep(.md-content blockquote) {
  margin: var(--space-md) 0;
  padding: var(--space-md) var(--space-lg);
  border-left: 3px solid var(--accent-blue);
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .list {
    width: 100%;
    min-width: 0;
    padding: var(--space-md);
  }
  
  .bubble {
    max-width: 85%;
  }
}
</style>