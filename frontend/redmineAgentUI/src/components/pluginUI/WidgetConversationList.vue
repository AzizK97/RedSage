<template>
  <section class="rs-widget__sidebar">
    <div class="rs-widget__sidebar-header">
      <div>
        <h3 class="rs-widget__sidebar-title">Conversation history</h3>
        <p class="rs-widget__sidebar-meta">Pick up where you left off</p>
      </div>

      <button type="button" class="rs-widget__primary-button" @click="$emit('new')">
        <Plus :size="14" />
        <span>New</span>
      </button>
    </div>

    <div class="rs-widget__sidebar-list">
      <div v-if="groupedConversations.length === 0" class="rs-widget__empty-state">
        <History :size="30" />
        <p class="rs-widget__empty-state-title">No conversations yet</p>
        <p class="rs-widget__empty-state-text">Start a new thread to see it here.</p>
      </div>

      <template v-else>
        <div v-for="group in groupedConversations" :key="group.label" class="rs-widget__group">
          <div class="rs-widget__group-label">{{ group.label }}</div>

          <button
            v-for="conversation in group.items"
            :key="conversation.thread_id"
            type="button"
            class="rs-widget__conversation-item"
            :class="{ 'rs-widget__conversation-item--active': conversation.thread_id === activeThreadId }"
            @click="$emit('select', conversation.thread_id)"
          >
            <p class="rs-widget__conversation-title">{{ conversation.title || conversation.thread_id }}</p>
            <p class="rs-widget__conversation-preview">{{ conversation.preview || 'No preview available' }}</p>

            <div class="rs-widget__conversation-footer">
              <span>{{ formatRelativeDate(conversation.updated_at) }}</span>
              <span class="rs-widget__conversation-actions">
                <button
                  type="button"
                  class="rs-widget__text-button"
                  :aria-label="`Delete ${conversation.thread_id}`"
                  @click.stop="$emit('delete', conversation.thread_id)"
                >
                  <Trash2 :size="14" />
                </button>
              </span>
            </div>
          </button>
        </div>
      </template>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { History, Plus, Trash2 } from 'lucide-vue-next';
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
