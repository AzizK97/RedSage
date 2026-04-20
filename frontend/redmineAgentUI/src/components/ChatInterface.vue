<script setup lang="ts">
import Header from "./Header.vue";
import ConversationSidebar from "./ConversationSidebar.vue";
import MessageList from "./MessageList.vue";
import MessageInput from "./MessageInput.vue";
import ApprovalDialog from "./ApprovalDialog.vue";
import { useChat } from "../composables/useChat";
import { useThreads } from "../composables/useThreads";
import type { ApproveRequest } from "../types";
import { computed, ref } from "vue";

const props = defineProps<{
  token: string;
  storageScope: string;
  role: "admin" | "project_manager";
}>();

const emit = defineEmits<{
  (event: "logout"): void;
}>();

const threadsStore = useThreads(props.token, props.storageScope);

const {
  messages,
  threadId,
  currentConversation,
  isLoading,
  loadingStatus,
  showLoadingStatus,
  pendingInterrupt,
  error,
  sendMessage,
  submitDecision,
} = useChat(props.token, threadsStore);

const {
  conversations,
  activeThreadId,
  createThread,
  setActiveThread,
  deleteThread,
} = threadsStore;

const isVirginChat = computed(() => conversations.value.length === 0 && !threadId.value);
const virginDraft = ref("");
const starterSuggestions = [
  "Give me a list of all the projects",
  "List high-priority issues assigned to me",
  "Summarize overdue tasks and next actions",
];

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
  await createThread();
}

function selectConversation(threadId: string) {
  setActiveThread(threadId);
}

async function removeConversation(threadId: string) {
  const conversation = conversations.value.find((item) => item.id === threadId);
  const label = conversation?.title ?? "this conversation";

  if (!window.confirm(`Delete ${label}? This cannot be undone.`)) {
    return;
  }

  try {
    await deleteThread(threadId);
    console.log(`✅ Conversation "${label}" deleted successfully`);
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    console.error(`❌ Failed to delete conversation "${label}":`, errorMsg);
    alert(`Failed to delete conversation: ${errorMsg}`);
  }
}

function logout() {
  emit("logout");
}
</script>

<template>
  <section class="chat-layout">
    <ConversationSidebar
      :conversations="conversations"
      :active-thread-id="activeThreadId"
      @new="startNewConversation"
      @select="selectConversation"
      @delete="removeConversation"
    />

    <div class="chat-panel">
      <Header />
      <div class="session-bar">
        <span class="session-role">Signed in as {{ props.role }}</span>
        <button type="button" class="logout-btn" @click="logout">Log out</button>
      </div>

      <div v-if="isVirginChat" class="virgin-shell">
        <div class="virgin-center">
          <h1 class="virgin-title">How can I help you today?</h1>
          <div class="suggestions" role="list" aria-label="Suggested prompts">
            <button
              v-for="suggestion in starterSuggestions"
              :key="suggestion"
              type="button"
              class="suggestion-chip"
              :disabled="isLoading || !!pendingInterrupt"
              @click="setSuggestionDraft(suggestion)"
            >
              {{ suggestion }}
            </button>
          </div>
          <MessageInput
            v-model="virginDraft"
            :disabled="isLoading || !!pendingInterrupt"
            @send="onSend"
          />
        </div>
      </div>
      <template v-else>
        <div class="chat-body">
          <div class="thread-row">
            <p class="thread">Thread: {{ threadId }}</p>
            <p class="conversation-name">{{ currentConversation?.title ?? "New conversation" }}</p>
          </div>

          <p v-if="error" class="error">{{ error }}</p>

          <div v-if="messages.length === 0" class="empty-thread-shell">
            <div class="empty-thread-center">
              <h2 class="empty-thread-title">Start this conversation</h2>
              <p class="empty-thread-subtitle">Send a message or pick a suggestion to continue.</p>
              <div class="suggestions" role="list" aria-label="Suggested prompts">
                <button
                  v-for="suggestion in starterSuggestions"
                  :key="`empty-${suggestion}`"
                  type="button"
                  class="suggestion-chip"
                  :disabled="isLoading || !!pendingInterrupt"
                  @click="setSuggestionDraft(suggestion)"
                >
                  {{ suggestion }}
                </button>
              </div>
            </div>
          </div>
          <MessageList v-else :messages="messages" />

          <div v-if="isLoading && showLoadingStatus" class="agent-status" role="status" aria-live="polite">
            <span class="status-dot" />
            <span class="status-text">{{ loadingStatus }}</span>
          </div>

          <ApprovalDialog
            :interrupt="pendingInterrupt"
            :disabled="isLoading"
            @approve="onApprove"
            @reject="onReject"
            @edit="onEdit"
          />
        </div>

        <div class="chat-input-docked">
          <MessageInput
            v-model="virginDraft"
            :disabled="isLoading || !!pendingInterrupt"
            @send="onSend"
          />
        </div>
      </template>
    </div>
  </section>
</template>

<style scoped>
.chat-layout {
  height: 100vh;
  display: flex;
  background: var(--bg-primary);
}

.chat-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.chat-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
  gap: 0;
}

.session-bar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: var(--space-sm);
  padding: 0 var(--space-lg) var(--space-sm);
}

.session-role {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.logout-btn {
  border: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: var(--radius-sm);
  padding: 0.25rem 0.6rem;
  font-size: var(--text-xs);
  cursor: pointer;
}

.virgin-shell {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-lg);
}

.virgin-center {
  width: min(760px, 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-lg);
}

.suggestions {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
  justify-content: center;
}

.suggestion-chip {
  border: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border-radius: 999px;
  padding: var(--space-xs) var(--space-md);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: color var(--transition-fast), background-color var(--transition-fast), border-color var(--transition-fast);
}

.suggestion-chip:hover:not(:disabled) {
  color: var(--text-primary);
  background: var(--bg-tertiary);
  border-color: var(--text-secondary);
}

.suggestion-chip:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.virgin-title {
  margin: 0;
  text-align: left;
  color: var(--text-primary);
  font-size: clamp(1.75rem, 2.6vw, 2.25rem);
  font-weight: 600;
}

.chat-input-docked {
  padding: 0 var(--space-md) var(--space-md);
}

.thread-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 var(--space-md) var(--space-sm);
}

.thread {
  color: var(--text-secondary);
  font-size: var(--text-xs);
  margin: 0;
}

.conversation-name {
  color: var(--text-primary);
  font-size: var(--text-sm);
  margin: 0;
}

.empty-thread-shell {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-lg);
}

.empty-thread-center {
  width: min(760px, 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-md);
}

.empty-thread-title {
  margin: 0;
  color: var(--text-primary);
  font-size: clamp(1.25rem, 2vw, 1.75rem);
  font-weight: 600;
}

.empty-thread-subtitle {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.error {
  color: #fca5a5;
  background: rgba(127, 29, 29, 0.2);
  border: 1px solid #7f1d1d;
  padding: var(--space-md);
  border-radius: var(--radius-lg);
  margin: var(--space-md);
  font-size: var(--text-sm);
}

.agent-status {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md);
  color: var(--text-secondary);
  min-height: 2rem;
  justify-content: center;
  font-size: var(--text-sm);
}

.status-text {
  font-size: var(--text-sm);
}

.status-dot {
  width: 0.375rem;
  height: 0.375rem;
  border-radius: 999px;
  background: var(--accent-green);
  animation: pulse 1.2s ease-in-out infinite;
}

@keyframes pulse {
  0% {
    opacity: 0.4;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.4;
  }
}

@media (max-width: 900px) {
  .chat-layout {
    flex-direction: column;
  }

  .chat-panel {
    min-height: 0;
  }
}
</style>