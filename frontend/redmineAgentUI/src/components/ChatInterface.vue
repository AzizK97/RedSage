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

.thread-row {
  display: none;
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