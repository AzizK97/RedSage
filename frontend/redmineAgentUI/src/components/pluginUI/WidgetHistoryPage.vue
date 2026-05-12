<template>
  <section class="rs-widget__history-page">

    <div class="rs-widget__page-body rs-widget__page-body--history">
      <WidgetConversationList
        :conversations="conversations"
        :active-thread-id="activeThreadId"
        @new="$emit('new')"
        @select="$emit('select', $event)"
        @delete="$emit('delete', $event)"
      />
    </div>

    <button
      type="button"
      class="rs-widget__fab"
      aria-label="New thread"
      title="New thread"
      @click="$emit('new')"
    >
      <Plus :size="22" />
    </button>
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
