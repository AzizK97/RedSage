<template>
  <div class="rs-widget__history-list">
    <div v-if="groupedConversations.length === 0" class="rs-widget__empty-state rs-widget__history-empty">
      <History :size="28" />
      <p class="rs-widget__empty-state-title">No conversations yet</p>
      <p class="rs-widget__empty-state-text">Use the + button below to start a new thread.</p>
    </div>

    <template v-else>
      <div v-for="group in groupedConversations" :key="group.label" class="rs-widget__history-group">
        <div class="rs-widget__history-group-label">{{ group.label }}</div>

        <div class="rs-widget__history-items">
          <article
            v-for="conversation in group.items"
            :key="conversation.thread_id"
            class="rs-widget__history-item"
            :class="{ 'rs-widget__history-item--active': conversation.thread_id === activeThreadId }"
          >
            <button
              type="button"
              class="rs-widget__history-item-main"
              @click="$emit('select', conversation.thread_id)"
            >

              <span class="rs-widget__history-copy">
                <span class="rs-widget__history-item-title">{{ conversation.title || conversation.thread_id }}</span>
                <span class="rs-widget__history-item-preview">{{ conversation.preview || 'No preview available' }}</span>
              </span>
            </button>

            <div class="rs-widget__history-meta">
              <span class="rs-widget__history-time">{{ formatRelativeDate(conversation.updated_at) }}</span>
              <button
                type="button"
                class="rs-widget__history-delete"
                :aria-label="`Delete ${conversation.thread_id}`"
                @click="$emit('delete', conversation.thread_id)"
              >
                <Trash2 :size="14" />
              </button>
            </div>
          </article>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { History, Trash2 } from 'lucide-vue-next';
import type { ThreadSummary } from '../../types';

const props = defineProps<{
  conversations: ThreadSummary[];
  activeThreadId?: string | null;
}>();

defineEmits<{
  (event: 'new'): void;
  (event: 'select', threadId: string): void;
  (event: 'delete', threadId: string): void;
}>();

const groupedConversations = computed(() => {
  const groups = new Map<string, ThreadSummary[]>();
  const now = Date.now();

  for (const conversation of props.conversations) {
    const timestamp = new Date(conversation.updated_at || now).getTime();
    const daysAgo = Math.floor((now - timestamp) / (1000 * 60 * 60 * 24));

    let label = 'Older';
    if (daysAgo <= 1) {
      label = 'Today';
    } else if (daysAgo <= 7) {
      label = 'This week';
    } else if (daysAgo <= 30) {
      label = 'This month';
    }

    if (!groups.has(label)) {
      groups.set(label, []);
    }
    groups.get(label)!.push(conversation);
  }

  const order = ['Today', 'This week', 'This month', 'Older'];
  return order
    .filter((label) => groups.has(label))
    .map((label) => ({ label, items: groups.get(label)! }));
});

function formatRelativeDate(value?: string | number | null): string {
  if (!value) return '';

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';

  const diffMs = Date.now() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays <= 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays}d ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
  return date.toLocaleDateString();
}
</script>
