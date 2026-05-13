<template>
  <section class="rs-widget__pane">
    <div v-if="visibleError" class="rs-widget__error-banner">
      <div class="rs-widget__error-card">
        <AlertTriangle :size="15" />
        <span>{{ visibleError }}</span>
      </div>
    </div>

    <header class="rs-widget__pane-header">
      <div class="rs-widget__pane-title-row">
        <span class="rs-widget__status-dot" />
        <div style="min-width: 0;">
          <p class="rs-widget__pane-title">Wiouuuu</p>
          <p class="rs-widget__pane-meta">Waaaaa333</p>
        </div>
      </div>

      <div class="rs-widget__pane-id" v-if="threadLabel">{{ threadLabel }}</div>
    </header>

    <template v-if="isVirginChat">
      <div class="rs-widget__hero">
        <div class="rs-widget__hero-card">
          <div class="rs-widget__hero-mark">
            <MessageCircleMore :size="36" />
          </div>
          <div>
            <h1 class="rs-widget__hero-title">Ask Redmine anything</h1>
            <p class="rs-widget__hero-subtitle">
              Summaries, issue status, approvals, and project updates — all in one place.
            </p>
          </div>

          <div class="rs-widget__suggestions">
            <button
              v-for="suggestion in starterSuggestions"
              :key="suggestion"
              type="button"
              class="rs-widget__suggestion"
              @click="$emit('suggestion', suggestion)"
            >
              <Sparkles class="rs-widget__suggestion-icon" :size="16" />
              <span class="rs-widget__suggestion-text">{{ suggestion }}</span>
            </button>
          </div>

          <WidgetMessageInput
            v-model="draft"
            :disabled="isBusy"
            placeholder="Ask about issues, tasks, or approvals..."
            @send="$emit('send', draft)"
          />
        </div>
      </div>
    </template>

    <template v-else>
      <div class="rs-widget__message-panel">
        <WidgetMessageList :messages="messages" />

        <div v-if="isLoading && loadingStatus" class="rs-widget__loading-pill">
          <span class="rs-widget__loading-dots" aria-hidden="true">
            <span class="rs-widget__loading-dot" />
            <span class="rs-widget__loading-dot" />
            <span class="rs-widget__loading-dot" />
          </span>
          <span class="rs-widget__loading-text">{{ loadingStatus }}</span>
        </div>
      </div>

      <WidgetApprovalPanel
        :interrupt="pendingInterrupt"
        :disabled="isBusy"
        @approve="$emit('approve')"
        @reject="$emit('reject', $event)"
        @edit="$emit('edit', $event)"
      />

      <WidgetMessageInput
        v-model="draft"
        :disabled="isBusy"
        placeholder="Write a message..."
        @send="$emit('send', draft)"
      />
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { AlertTriangle, MessageCircleMore, Sparkles } from 'lucide-vue-next';
import type { Message } from '../../types';
import WidgetMessageList from './WidgetMessageList.vue';
import WidgetMessageInput from './WidgetMessageInput.vue';
import WidgetApprovalPanel from './WidgetApprovalPanel.vue';

const props = defineProps<{
  messages: Message[];
  isLoading: boolean;
  loadingStatus: string;
  pendingInterrupt?: unknown | null;
  visibleError?: string | null;
  threadId?: string | null;
  threadTitle?: string | null;
  isVirginChat: boolean;
  starterSuggestions: string[];
}>();

defineEmits<{
  (event: 'send', message: string): void;
  (event: 'approve'): void;
  (event: 'reject', message: string): void;
  (event: 'edit', message: string): void;
  (event: 'suggestion', suggestion: string): void;
}>();

const draft = ref('');

const isBusy = computed(() => props.isLoading || Boolean(props.pendingInterrupt));
const heading = computed(() => (props.threadTitle ? props.threadTitle : 'Conversation'));
const subheading = computed(() => (props.threadId ? 'Active thread' : 'Start a new conversation'));
const threadLabel = computed(() => (props.threadId ? `#${props.threadId.slice(0, 8)}` : ''));

watch(
  () => props.messages.length,
  () => {
    if (!props.isLoading) {
      draft.value = '';
    }
  },
);

watch(
  () => props.threadId,
  () => {
    draft.value = '';
  },
);
</script>
