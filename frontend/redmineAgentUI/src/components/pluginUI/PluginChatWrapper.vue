<script setup lang="ts">
import { computed, ref } from 'vue';
import { useChat } from '../../composables/useChat';
import type { Message } from '../../types';
import WidgetChatPane from './WidgetChatPane.vue';
import WidgetConversationList from './WidgetConversationList.vue';
import WidgetHeader from './WidgetHeader.vue';
import WidgetHistoryPage from './WidgetHistoryPage.vue';
import WidgetTabs, { type WidgetView } from './WidgetTabs.vue';

interface Props {
  token: string;
  userId: string;
  role: 'admin' | 'project_manager';
}

const props = defineProps<Props>();

const currentView = ref<WidgetView>('chat');
const isExpanded = ref(false);
const lastView = ref<WidgetView | null>(null);

const {
  messages,
  threadId,
  conversations,
  activeThreadId,
  isLoading,
  pendingInterrupt,
  error,
  loadingStatus,
  currentConversation,
  createThread,
  setActiveThread,
  deleteThread,
  sendMessage,
  submitDecision,
} = useChat(props.token, props.userId);

const starterSuggestions = [
  'Summarize the latest unresolved issues.',
  'Show me what needs approval today.',
  'Which threads were updated this week?',
];

const threadTitle = computed(() => currentConversation.value?.title ?? '');
const currentThreadId = threadId;
const visibleError = computed(() => error?.value ?? null);
const isVirginChat = computed(() => (messages.value ? messages.value.length === 0 : true));
const widgetConversations = computed(() =>
  conversations.value.map((conversation) => ({
    thread_id: conversation.id,
    title: conversation.title,
    preview: conversation.preview,
    updated_at: conversation.updatedAt,
  })),
);

function updateModalClass(expanded: boolean) {
  isExpanded.value = expanded;
  if (typeof window !== 'undefined' && typeof window.__updateModalClass === 'function') {
    window.__updateModalClass(expanded ? 'expanded' : '');
  }
}

function toggleExpanded() {
  updateModalClass(!isExpanded.value);
}

function handleClose() {
  (window as Window & { __redmineChatWidgetClose?: () => void }).__redmineChatWidgetClose?.();
}

function handleNewThread() {
  createThread();
  currentView.value = 'chat';
}

function handleSelectThread(threadId: string) {
  setActiveThread(threadId);
  lastView.value = currentView.value;
  currentView.value = 'chat';
}

function handleDeleteThread(threadId: string) {
  deleteThread(threadId);
}

function handleSuggestion(suggestion: string) {
  void sendMessage(suggestion);
}

async function handleApprove() {
  await submitDecision({ decision_type: 'approve' } as any);
}

async function handleReject(message: string) {
  await submitDecision({ decision_type: 'reject', reason: message } as any);
}

async function handleEdit(message: string) {
  let payload: any = { decision_type: 'edit' };
  try {
    payload.edited_action = JSON.parse(message);
  } catch {
    payload.edited_action = { name: String(message || 'edit'), args: {} };
  }
  await submitDecision(payload as any);
}
</script>

<template>
  <div class="rs-widget">
    <WidgetHeader
      title="Redmine Chat Assist"
      subtitle="Project-aware support for your team"
      :expanded="isExpanded"
      :showBack="lastView === 'history'"
      @close="handleClose"
      @toggle-expand="toggleExpanded"
      @back="() => { currentView.value = 'history'; lastView.value = null }"
    />

    <WidgetTabs v-model="currentView" />

    <div class="rs-widget__content">
      <div v-if="currentView === 'chat'" class="rs-widget__split" :class="{ 'rs-widget__split--compact': !isExpanded }">
        <WidgetConversationList
          v-if="isExpanded"
          :conversations="widgetConversations"
          :active-thread-id="activeThreadId"
          @new="handleNewThread"
          @select="handleSelectThread"
          @delete="handleDeleteThread"
        />

        <div class="rs-widget__main">
          <WidgetChatPane
            :messages="messages as Message[]"
            :is-loading="isLoading"
            :loading-status="loadingStatus"
            :pending-interrupt="pendingInterrupt"
            :visible-error="visibleError"
            :thread-id="currentThreadId"
            :thread-title="threadTitle"
            :is-virgin-chat="isVirginChat"
            :starter-suggestions="starterSuggestions"
            @send="sendMessage"
            @approve="handleApprove"
            @reject="handleReject"
            @edit="handleEdit"
            @suggestion="handleSuggestion"
          />
        </div>
      </div>

      <WidgetHistoryPage
        v-else
        :conversations="widgetConversations"
        :active-thread-id="activeThreadId"
        @new="handleNewThread"
        @select="handleSelectThread"
        @delete="handleDeleteThread"
      />
    </div>
  </div>
</template>