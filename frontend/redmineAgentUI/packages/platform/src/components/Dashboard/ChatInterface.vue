<script setup lang="ts">
import ConversationSidebar from "./ConversationSidebar.vue";
import MessageList from "./MessageList.vue";
import MessageInput from "./MessageInput.vue";
import ApprovalDialog from "./ApprovalDialog.vue";
import { useChat } from "@redsage/ui-core/composables/useChat";
import type { ApproveRequest } from "@redsage/ui-core/types";
import { computed, ref, watch } from "vue";
import { MessageSquare, AlertCircle, Bot } from "lucide-vue-next";

const props = defineProps<{
  token: string;
  userId: string;
  role: "admin" | "project_manager";
  openThreadId?: string | null;
}>();

const {
  messages,
  threadId,
  currentConversation,
  isLoading,
  loadingStatus,
  showLoadingStatus,
  isSyncing,
  pendingInterrupt,
  error,
  syncError,
  sendMessage,
  submitDecision,
  conversations,
  activeThreadId,
  createThread,
  setActiveThread,
  deleteThread,
} = useChat(props.token, props.userId);

// When parent requests opening a specific thread, set it active
watch(
  () => props.openThreadId,
  async (id) => {
    if (id) {
      try {
        await setActiveThread(id);
      } catch (e) {
        console.error("Failed to open thread from navigation:", e);
      }
    }
  },
  { immediate: true }
);

const isVirginChat = computed(() => messages.value.length === 0);
const visibleError = computed(() => error.value || syncError.value);
const virginDraft = ref("");
const hideThinkingBar = ref(false);
const starterSuggestions = [
  "Give me a list of all the projects",
  "List high-priority tasks that are due this week",
  "Summarize overdue tasks and next actions",
];

const showThinkingBar = computed(
  () => isLoading.value && showLoadingStatus.value && !hideThinkingBar.value,
);

watch(
  () => isLoading.value,
  (loadingNow) => {
    if (loadingNow) {
      hideThinkingBar.value = false;
    }
  },
);

function onSkipThinkingBar() {
  hideThinkingBar.value = true;
}

function setSuggestionDraft(suggestion: string) {
  virginDraft.value = suggestion;
}

function onSend(text: string) {
  sendMessage(text);
}

function onApprove() {
  submitDecision({ decision_type: "approve" });
}

function onReject(message: string) {
  submitDecision({ decision_type: "reject", message });
}

function onEdit(payload: { name: string; args: Record<string, any> }) {
  const request: ApproveRequest = {
    decision_type: "edit",
    edited_action: payload,
  };
  submitDecision(request);
}

async function startNewConversation() {
  try {
    await createThread();
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    alert(`Failed to create conversation: ${errorMsg}`);
  }
}

async function selectConversation(threadId: string) {
  try {
    await setActiveThread(threadId);
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    alert(`Failed to load conversation: ${errorMsg}`);
  }
}

async function removeConversation(threadId: string) {
  const conversation = conversations.value.find((item) => item.id === threadId);
  const label = conversation?.title ?? "this conversation";

  if (!window.confirm(`Delete ${label}? This cannot be undone.`)) {
    return;
  }

  try {
    await deleteThread(threadId);
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    alert(`Failed to delete conversation: ${errorMsg}`);
  }
}
</script>

<template>
  <section class="h-full flex bg-surface-950 overflow-hidden relative">
    <!-- Sidebar -->
    <ConversationSidebar
      :conversations="conversations"
      :active-thread-id="activeThreadId"
      @new="startNewConversation"
      @select="selectConversation"
      @delete="removeConversation"
    />

    <!-- Main Panel -->
    <div class="flex-1 flex flex-col min-w-0 bg-surface-950/40 relative">
      <div v-if="isVirginChat" class="flex-1 flex items-center justify-center p-8">
        <div class="w-full max-w-3xl flex flex-col items-center gap-12 text-center">
          <div class="space-y-6">
            <div class="w-20 h-20 rounded-[2.5rem] bg-gradient-to-br from-sage-400 to-copper-500 p-px mx-auto shadow-2xl shadow-sage-900/40">
              <div class="w-full h-full rounded-[inherit] bg-surface-950 flex items-center justify-center text-white">
                <Bot :size="40" class="text-sage-400 animate-pulse" />
              </div>
            </div>
            <div class="space-y-2">
              <h1 class="text-4xl sm:text-5xl font-black text-white tracking-tighter">How can I help today?</h1>
              <p class="text-surface-500 font-medium text-lg">AI-powered Redmine orchestration and insight engine.</p>
            </div>
          </div>

          <div class="w-full grid grid-cols-1 sm:grid-cols-3 gap-3">
            <button
              v-for="suggestion in starterSuggestions"
              :key="suggestion"
              type="button"
              class="p-4 rounded-2xl bg-surface-900 border border-surface-800 text-surface-400 text-xs font-bold uppercase tracking-wider text-left hover:bg-surface-800 hover:border-sage-500/20 hover:text-sage-400 transition-all group"
              :disabled="isLoading || !!pendingInterrupt"
              @click="setSuggestionDraft(suggestion)"
            >
               <MessageSquare :size="14" class="mb-3 opacity-30 group-hover:opacity-100 transition-opacity" />
               <span class="leading-relaxed">{{ suggestion }}</span>
            </button>
          </div>

          <div class="w-full">
            <MessageInput
              v-model="virginDraft"
              :disabled="isLoading || !!pendingInterrupt"
              @send="onSend"
            />
          </div>
        </div>
      </div>

      <template v-else>
        <div class="flex-1 flex flex-col min-h-0">
          <div class="px-6 py-4 border-b border-surface-800 bg-surface-950/50 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-2 h-2 rounded-full bg-sage-500 animate-pulse" />
              <h2 class="text-sm font-bold text-surface-200 truncate">{{ currentConversation?.title || "New Thread" }}</h2>
              <span class="text-[10px] font-black text-surface-600 uppercase tracking-widest hidden sm:inline">id: {{ threadId?.slice(0,8) }}</span>
            </div>
            <div v-if="isSyncing" class="flex items-center gap-2 text-[10px] font-black text-sage-500 uppercase tracking-widest">
              <div class="w-1.5 h-1.5 border-t-2 border-sage-500 rounded-full animate-spin" />
              Syncing
            </div>
          </div>

          <div class="flex-1 min-h-0 relative">
            <div v-if="visibleError" class="absolute top-4 left-1/2 -translate-x-1/2 z-50 w-full max-w-xl px-4 animate-slide-down">
              <div class="p-4 rounded-xl bg-red-500/10 border border-red-500/20 backdrop-blur-md flex items-center gap-4 text-red-400 shadow-2xl">
                <AlertCircle :size="20" class="shrink-0" />
                <p class="text-sm font-bold truncate">{{ visibleError }}</p>
              </div>
            </div>

            <div class="h-full overflow-hidden">
               <MessageList
                :messages="messages"
                :show-thinking-bar="showThinkingBar"
                :loading-status="loadingStatus"
                @skip-thinking="onSkipThinkingBar"
              />
            </div>
          </div>

          <div class="px-6 py-4 bg-transparent">
             <ApprovalDialog
                :token="token"
              :interrupt="pendingInterrupt"
              :disabled="isLoading"
              @approve="onApprove"
              @reject="onReject"
              @edit="onEdit"
            />
            <div class="mt-2">
              <MessageInput :disabled="isLoading || !!pendingInterrupt" @send="onSend" />
            </div>
          </div>
        </div>
      </template>
    </div>
  </section>
</template>

<style>
@keyframes slide-down {
  from { transform: translate(-50%, -100%); opacity: 0; }
  to { transform: translate(-50%, 0); opacity: 1; }
}
.animate-slide-down {
  animation: slide-down 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
</style>