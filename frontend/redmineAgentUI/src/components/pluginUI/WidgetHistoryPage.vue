<template>
  <section class="rs-widget__history-page">
    <div class="rs-widget__page-header">
      <div>
        <h3 class="rs-widget__page-title">Thread history</h3>
        <p class="rs-widget__page-meta">Return to earlier conversations anytime</p>
      </div>

      <button type="button" class="rs-widget__primary-button" @click="$emit('new')">
        <Plus :size="14" />
        <span>New thread</span>
      </button>
    </div>

    <div class="rs-widget__page-body">
      <WidgetConversationList
        :conversations="conversations"
        :active-thread-id="activeThreadId"
        @new="$emit('new')"
        @select="$emit('select', $event)"
        @delete="$emit('delete', $event)"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { Plus } from 'lucide-vue-next';
import type { ThreadSummary } from '../../types';
import WidgetConversationList from './WidgetConversationList.vue';

defineProps<{
  conversations: ThreadSummary[];
  activeThreadId?: string | null;
}>();

defineEmits<{
  (event: 'new'): void;
  (event: 'select', threadId: string): void;
  (event: 'delete', threadId: string): void;
}>();
</script>
