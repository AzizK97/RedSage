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

          <!-- PDF download button — only shown for report-type messages -->
          <div
            v-if="message.role === 'assistant' && isReportMessage(message.content)"
            class="mt-3 flex"
          >
            <button
              @click="redirectToPlatformPreview()"
              class="rs-widget__report-download"
              type="button"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24"
                   fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10 9 9 9 8 9"/>
              </svg>
              Download as PDF
            </button>
          </div>
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
import type { Message } from '@redsage/ui-core/types';
import { isReportMessage } from '../../../ui-core/src/utils/reportDetection';

const props = defineProps<{
  messages: Message[];
  threadId?: string | null;
  platformUrl?: string;
}>();

const listRef = ref<HTMLElement | null>(null);
const markdown = new MarkdownIt({ breaks: true, linkify: true });

function renderMarkdown(content: string): string {
  return DOMPurify.sanitize(markdown.render(content || ''));
}

function redirectToPlatformPreview() {
  const threadId = props.threadId?.trim();
  if (!threadId) return;

  const base = (props.platformUrl || '').trim().replace(/\/$/, '') || `${window.location.origin}`;
  const target = `${base}/chat?threadId=${encodeURIComponent(threadId)}&preview=pdf`;
  window.open(target, '_blank', 'noopener,noreferrer');
}

async function scrollToBottom() {
  await nextTick();
  const el = listRef.value;
  if (!el) return;
  el.scrollTop = el.scrollHeight;
}

watch(
  () => props.messages.map((m) => `${m.timestamp}:${m.role}:${m.content.length}`).join('|'),
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

<style scoped>
.rs-widget__report-download {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.03);
  color: rgba(255, 255, 255, 0.72);
  font-size: 11px;
  font-weight: 600;
  transition: border-color 0.18s ease, color 0.18s ease, background 0.18s ease;
}

.rs-widget__report-download:hover {
  color: #ffffff;
  border-color: rgba(125, 154, 121, 0.65);
  background: rgba(125, 154, 121, 0.12);
}
</style>
