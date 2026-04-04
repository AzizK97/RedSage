<script setup lang="ts">
import Header from "./Header.vue";
import ConversationSidebar from "./ConversationSidebar.vue";
import MessageList from "./MessageList.vue";
import MessageInput from "./MessageInput.vue";
import ApprovalDialog from "./ApprovalDialog.vue";
import { useChat } from "../composables/useChat";
import { useThreads } from "../composables/useThreads";
import type { ApproveRequest } from "../types";

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
} = useChat();

const {
  conversations,
  activeThreadId,
  createThread,
  setActiveThread,
  deleteThread,
} = useThreads();

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

function startNewConversation() {
  createThread();
}

function selectConversation(threadId: string) {
  setActiveThread(threadId);
}

function removeConversation(threadId: string) {
  const conversation = conversations.value.find((item) => item.id === threadId);
  const label = conversation?.title ?? "this conversation";

  if (!window.confirm(`Delete ${label}? This cannot be undone.`)) {
    return;
  }

  deleteThread(threadId);
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

      <div class="chat-body">
        <div class="thread-row">
          <p class="thread">Thread: {{ threadId }}</p>
          <p class="conversation-name">{{ currentConversation?.title ?? "New conversation" }}</p>
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <MessageList :messages="messages" />

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

      <MessageInput :disabled="isLoading || !!pendingInterrupt" @send="onSend" />
    </div>
  </section>
</template>

<style scoped>
.chat-layout {
  height: 100vh;
  display: flex;
  background: #111827;
}

.chat-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.chat-body {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  gap: 0.75rem;
}

.thread-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: baseline;
  flex-wrap: wrap;
}

.thread {
  color: #9ca3af;
  font-size: 0.75rem;
  margin: 0;
}

.conversation-name {
  color: #e5e7eb;
  font-size: 0.9rem;
  margin: 0;
}

.error {
  color: #fca5a5;
  background: #3b1f1f;
  border: 1px solid #7f1d1d;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
}

.agent-status {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.25rem 0.35rem 0.1rem;
  color: #9ca3af;
  min-height: 1.5rem;
}

.status-text {
  font-size: 0.95rem;
}

.status-dot {
  width: 0.45rem;
  height: 0.45rem;
  border-radius: 999px;
  background: #9ca3af;
  animation: pulse 1.2s ease-in-out infinite;
}

@keyframes pulse {
  0% {
    opacity: 0.35;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.35;
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