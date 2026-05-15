<template>
  <section v-if="interrupt" class="rs-widget__approval">
    <div class="rs-widget__approval-header">
      <div class="rs-widget__approval-mark">
        <ShieldCheck :size="18" />
      </div>
      <div>
        <h3 class="rs-widget__approval-title">Action approval required</h3>
        <p class="rs-widget__approval-subtitle">Review the proposed action before it is sent.</p>
      </div>
    </div>

    <div class="rs-widget__approval-body">
      <pre class="rs-widget__approval-preview">{{ prettyPayload }}</pre>

      <div class="rs-widget__approval-grid">
        <div class="rs-widget__field">
          <label class="rs-widget__field-label" :for="rejectFieldId">Reject note</label>
          <textarea
            :id="rejectFieldId"
            v-model="rejectMessage"
            class="rs-widget__textarea"
            placeholder="Explain why this action should be rejected"
          />
        </div>

        <div class="rs-widget__field">
          <label class="rs-widget__field-label" :for="editFieldId">Edit payload</label>
          <textarea
            :id="editFieldId"
            v-model="editMessage"
            class="rs-widget__textarea"
            placeholder="Provide an edited JSON payload"
          />
        </div>
      </div>

      <div class="rs-widget__approval-actions">
        <button type="button" class="rs-widget__primary-button" :disabled="disabled" @click="$emit('approve')">
          <CheckCircle2 :size="14" />
          <span>Approve</span>
        </button>
        <button type="button" class="rs-widget__danger-button" :disabled="disabled" @click="$emit('reject', rejectMessage)">
          <Ban :size="14" />
          <span>Reject</span>
        </button>
        <button type="button" class="rs-widget__ghost-button" :disabled="disabled" @click="$emit('edit', editMessage)">
          <PencilLine :size="14" />
          <span>Send edit</span>
        </button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { Ban, CheckCircle2, PencilLine, ShieldCheck } from 'lucide-vue-next';

const props = defineProps<{
  interrupt?: unknown | null;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  (event: 'approve'): void;
  (event: 'reject', message: string): void;
  (event: 'edit', message: string): void;
}>();

const rejectMessage = ref('');
const editMessage = ref('');
const rejectFieldId = `reject-${Math.random().toString(36).slice(2, 8)}`;
const editFieldId = `edit-${Math.random().toString(36).slice(2, 8)}`;

const prettyPayload = computed(() => {
  if (!props.interrupt) return '';
  if (typeof props.interrupt === 'string') return props.interrupt;
  try {
    return JSON.stringify(props.interrupt, null, 2);
  } catch {
    return String(props.interrupt);
  }
});
</script>
