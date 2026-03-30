<script setup lang="ts">
import MessageList from "./MessageList.vue";
import MessageInput from "./MessageInput.vue";
import ApprovalDialog from "./ApprovalDialog.vue";
import { useChat } from "../composables/useChat";
import type { ApproveRequest } from "../types";

const {
  messages,
  threadId,
  isLoading,
  pendingInterrupt,
  error,
  sendMessage,
  submitDecision,
} = useChat();

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
</script>

<template>
  <section class="chat-layout">
    <header class="chat-header">
      <h1>Redmine Agent UI</h1>
      <small>Thread: {{ threadId }}</small>
    </header>

    <p v-if="error" class="error">{{ error }}</p>

    <MessageList :messages="messages" />

    <ApprovalDialog
      :interrupt="pendingInterrupt"
      :disabled="isLoading"
      @approve="onApprove"
      @reject="onReject"
      @edit="onEdit"
    />

    <MessageInput :disabled="isLoading || !!pendingInterrupt" @send="onSend" />
  </section>
</template>

<style scoped>
.chat-layout {
  display: grid;
  grid-template-rows: auto auto 1fr auto auto;
  gap: 0.75rem;
  height: 100%;
}
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}
.error {
  color: #b91c1c;
  background: #fee2e2;
  border: 1px solid #fecaca;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
}
</style>