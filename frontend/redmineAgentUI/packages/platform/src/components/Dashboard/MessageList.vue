<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from "vue";
import type { Message } from "../../../../ui-core/src/types/index.ts";
import { isReportMessage } from "../../../../ui-core/src/utils/reportDetection";
import MarkDownIt from "markdown-it";
import DOMPurify from "dompurify";
import { Lightbulb } from "lucide-vue-next";
import ApprovalDialog from "./ApprovalDialog.vue";
import ChatReportPdfPreview from "./ChatReportPdfPreview.vue";

const props = defineProps<{
  messages: Message[];
  showThinkingBar?: boolean;
  loadingStatus?: string;
  token: string;
  interrupt: Record<string, any> | null;
  disabled: boolean;
  forceReportPreview?: boolean;
}>();

const emit = defineEmits<{
  (e: "skip-thinking"): void;
  (e: "approve"): void;
  (e: "reject", message: string): void;
  (e: "edit", payload: { name: string; args: Record<string, any> }): void;
  (e: "report-preview-opened"): void;
}>();

const listRef = ref<HTMLElement | null>(null);
const approvalDialogRef = ref<HTMLElement | null>(null);
const previewContent = ref<string | null>(null);

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

async function scrollApprovalDialogIntoView() {
  await nextTick();
  if (approvalDialogRef.value) {
    approvalDialogRef.value.scrollIntoView({ behavior: "smooth", block: "center" });
  }
}

function openReportPreview(content: string) {
  previewContent.value = content;
}

function closeReportPreview() {
  previewContent.value = null;
}

watch(
  () => props.messages,
  () => {
    scrollToBottom();
  },
  { deep: true },
);

watch(
  () => props.interrupt,
  () => {
    if (props.interrupt) {
      scrollApprovalDialogIntoView();
    }
  },
);

watch(
  () => props.forceReportPreview,
  (enabled) => {
    if (!enabled) return;
    const latestReport = [...props.messages]
      .reverse()
      .find((m) => m.role === "assistant" && isReportMessage(m.content));

    if (latestReport) {
      openReportPreview(latestReport.content);
      emit("report-preview-opened");
    }
  },
  { immediate: true },
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

            <!-- PDF download button — only shown for report-type messages -->
            <div
              v-if="msg.role === 'assistant' && isReportMessage(msg.content)"
              class="mt-3 flex"
            >
              <button
                @click="openReportPreview(msg.content)"
                class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium
                       rounded-lg border transition-colors
                       text-surface-400 border-surface-700/60 hover:text-white
                       hover:border-sage-600/60 hover:bg-sage-900/20"
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
        </div>
      </div>

      <!-- Approval Dialog as inline message -->
      <div
        v-if="interrupt"
        ref="approvalDialogRef"
        class="flex gap-4 sm:gap-6 animate-in fade-in slide-in-from-bottom-2 duration-300"
      >
        <div class="flex flex-col max-w-[85%] sm:max-w-[100%] items-start w-full">
          <ApprovalDialog
            :token="token"
            :interrupt="interrupt"
            :disabled="disabled"
            inline
            @approve="$emit('approve')"
            @reject="(msg) => $emit('reject', msg)"
            @edit="(payload) => $emit('edit', payload)"
          />
        </div>
      </div>

      <div
        v-if="showThinkingBar"
        class="flex gap-4 sm:gap-6 animate-in fade-in slide-in-from-bottom-2 duration-300"
      >
        <div class="flex flex-col max-w-[85%] sm:max-w-[100%] items-start w-full">
          <div class="w-full px-1 py-1">
            <div class="flex items-center justify-between text-surface-400">
              <button
                type="button"
                class="inline-flex items-center gap-2 text-xl font-bold tracking-tight text-surface-500"
                disabled
              >
                <Lightbulb :size="16" class="text-surface-600" />
                <div class="mt-3 flex items-center gap-2 text-surface-600" aria-label="assistant thinking animation">
                  <span class="w-1.5 h-1.5 rounded-full bg-copper-500/80 animate-thinking-dot" />
                  <span class="w-1.5 h-1.5 rounded-full bg-copper-500/80 animate-thinking-dot" style="animation-delay: .12s" />
                  <span class="w-1.5 h-1.5 rounded-full bg-copper-500/80 animate-thinking-dot" style="animation-delay: .24s" />
                </div>
                <!-- <ChevronRight :size="14" class="text-surface-600" /> -->
              </button>

              <!-- <button
                type="button"
                class="text-lg text-surface-500 hover:text-surface-300 transition-colors"
                @click="$emit('skip-thinking')"
              >
                Skip
              </button> -->
            </div>

            <p v-if="loadingStatus" class="mt-2 text-xs font-semibold uppercase tracking-widest text-surface-600">
              {{ loadingStatus }}
            </p>
          </div>
        </div>
      </div>

      <!-- Chat report PDF preview modal -->
      <ChatReportPdfPreview
        v-if="previewContent !== null"
        :content="previewContent"
        @close="closeReportPreview"
      />
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

@keyframes thinking-dot {
  0%,
  80%,
  100% {
    transform: translateY(0);
    opacity: 0.45;
  }
  40% {
    transform: translateY(-3px);
    opacity: 1;
  }
}

.animate-thinking-dot {
  animation: thinking-dot 1s infinite ease-in-out;
}
</style>