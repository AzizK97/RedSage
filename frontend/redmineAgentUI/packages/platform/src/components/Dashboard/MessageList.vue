<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from "vue";
import type { Message } from "../../../../ui-core/src/types/index.ts";
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
  <div id="chat-container" ref="listRef" class="h-full overflow-y-auto px-4 sm:px-0 py-8 space-y-8 scroll-smooth custom-scrollbar">
    <div class="max-w-5xl mx-auto w-full space-y-8">
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        :class="[
          'flex gap-4 sm:gap-6 group animate-in fade-in slide-in-from-bottom-2 duration-300',
          msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'
        ]"
      >

        <!-- Content -->
        <div 
          :class="[
            'flex flex-col max-w-[85%] sm:max-w-[100%]',
            msg.role === 'user' ? 'items-end' : 'items-start'
          ]"
        >
          <div 
            :class="[
              'px-5 py-3 rounded-2xl text-sm leading-relaxed shadow-sm transition-all',
              msg.role === 'user' 
                ? 'bg-surface-800 text-surface-100 rounded-tr-none border border-surface-700/50' 
                : 'text-surface-300 rounded-tl-none'
            ]"
          >
            <p v-if="msg.role === 'user'" class="whitespace-pre-wrap">{{ msg.content }}</p>
            <div 
              v-else 
              class="prose dark:prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-pre:bg-surface-900 prose-pre:border prose-pre:border-surface-800 prose-code:text-sage-400 prose-code:bg-surface-900 prose-code:px-1 prose-code:rounded prose-code:before:content-none prose-code:after:content-none prose-th:text-surface-200 prose-td:text-surface-400" 
              v-html="renderMarkdown(msg.content)"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #2a2d29;
  border-radius: 99px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #3c5439;
}

/* Custom Markdown Content Styles */
:deep(.prose table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
  font-size: 0.8rem;
  background: rgba(15, 15, 15, 0.4);
  border-radius: 0.75rem;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

:deep(.prose th) {
  background: rgba(42, 45, 41, 0.4);
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

:deep(.prose td) {
  padding: 0.75rem 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

:deep(.prose pre) {
  border-radius: 1rem;
  padding: 1.25rem;
  margin: 1.5rem 0;
}
</style>