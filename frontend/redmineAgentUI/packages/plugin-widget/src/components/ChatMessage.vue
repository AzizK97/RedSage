<script setup lang="ts">
import { computed } from 'vue';

defineProps<{
  message: {
    id: string | number;
    senderName?: string;
    body: string;
    timestamp?: string;
    isAgent?: boolean;
    title?: string;
    actions?: { id: string; label: string }[];
  };
}>()

const props = defineProps<any>();
const isAgent = computed(() => !!props.message.isAgent);
</script>

<template>
  <div :class="['rds-message', isAgent ? 'agent' : 'user', 'rds-animate-slide-up']">
    <div class="rds-message-row" style="display:flex;align-items:flex-start;gap:var(--rds-space-3);">
      <!-- Avatar for agent messages -->
      <div v-if="isAgent" class="rds-avatar" aria-hidden="true">RS</div>

      <div class="rds-message-bubble">
        <div class="rds-message-header" style="display:flex;align-items:center;justify-content:space-between;gap:var(--rds-space-2);">
          <div>
            <div class="rds-message-title rds-text-14 rds-font-600">{{ message.title || message.senderName || (isAgent ? 'RedSage' : 'You') }}</div>
            <div class="rds-message-ts" style="font-size:11px;color:rgba(0,0,0,0.45);margin-top:2px;">{{ message.timestamp }}</div>
          </div>
        </div>

        <div class="rds-message-body rds-text-14" style="margin-top:var(--rds-space-2);">{{ message.body }}</div>

        <div v-if="message.actions && message.actions.length" class="rds-message-actions" style="margin-top:var(--rds-space-3);display:flex;gap:var(--rds-space-2);">
          <button
            v-for="act in message.actions"
            :key="act.id"
            class="rds-action-btn"
            @click="$emit('action', { id: act.id, messageId: message.id })"
          >
            {{ act.label }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import "../styles/index.css";

.rds-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display:flex;
  align-items:center;
  justify-content:center;
  font-weight:600;
  color: #fff;
  background: linear-gradient(135deg,#ff7a18,#ff944d);
  flex: 0 0 32px;
}

.rds-message { margin-bottom: var(--rds-space-3); }

.rds-message-bubble {
  border-radius: 10px;
  background: #fff;
  padding: var(--rds-space-3) var(--rds-space-3);
  box-shadow: var(--rds-shadow-xs);
  border-left: 3px solid transparent;
}

.rds-message.agent .rds-message-bubble { border-left-color: #ff7a18; }
.rds-message.user { display:flex; justify-content:flex-end; }
.rds-message.user .rds-message-bubble { border-right: 3px solid rgba(0,0,0,0.08); }

.rds-message-title { line-height:1; }
.rds-message-body { white-space:pre-wrap; }

.rds-message-actions .rds-action-btn { padding: 6px 10px; border-radius:6px; font-size:13px; }

</style>
