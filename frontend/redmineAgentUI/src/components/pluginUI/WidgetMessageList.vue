<template>
  <div ref="listRef" class="rs-widget__message-list">
    <div v-if="messages.length === 0" class="rs-widget__empty-state">
      <Sparkles :size="30" />
      <p class="rs-widget__empty-state-title">Ready when you are</p>
      <p class="rs-widget__empty-state-text">Send a message to start the conversation.</p>
    </div>

    <div v-else class="rs-widget__message-stack">
      <article
        v-for="(message,idx) in messages"
        :key="idx || `${message.role}-${message.timestamp}`"
        class="rs-widget__message-row"
        :class="message.role === 'user' ? 'rs-widget__message-row--user' : 'rs-widget__message-row--assistant'"
      >
        <div class="rs-widget__bubble" :class="message.role === 'user' ? 'rs-widget__bubble--user' : 'rs-widget__bubble--assistant'">
          <div v-if="message.role === 'assistant'" class="rs-widget__message-markdown" v-html="renderMarkdown(message.content)" />
          <p v-else>{{ message.content }}</p>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { Sparkles } from 'lucide-vue-next';
import DOMPurify from 'dompurify';
import MarkdownIt from 'markdown-it';
import type { Message } from '../../types';

const props = defineProps<{
  messages: Message[];
}>();

const listRef = ref<HTMLElement | null>(null);
const markdown = new MarkdownIt({ breaks: true, linkify: true });

function renderMarkdown(content: string): string {
  return DOMPurify.sanitize(markdown.render(content || ''));
}

async function scrollToBottom() {
  await nextTick();
  const el = listRef.value;
  if (!el) return;
  el.scrollTop = el.scrollHeight;
}

watch(
  () => props.messages.length,
  () => {
    void scrollToBottom();
  },
);

onMounted(() => {
  void scrollToBottom();
});

onBeforeUnmount(() => {
  listRef.value = null;
});
</script>
