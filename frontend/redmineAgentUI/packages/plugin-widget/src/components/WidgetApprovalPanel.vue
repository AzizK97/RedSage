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
          <label class="rs-widget__field-label" :for="actionNameFieldId">Action</label>
          <input
            :id="actionNameFieldId"
            v-model="editActionName"
            class="rs-widget__input"
            placeholder="Tool name (e.g. reassign_issue)"
          />
        </div>

        <div
          v-for="key in argKeys"
          :key="key"
          class="rs-widget__field"
        >
          <label class="rs-widget__field-label" :for="`arg-${key}`">{{ key }}</label>
          <textarea
            v-if="isStructuredArg(key)"
            :id="`arg-${key}`"
            v-model="editableArgs[key]"
            class="rs-widget__textarea"
            :placeholder="argPlaceholder(key)"
          />
          <input
            v-else
            :id="`arg-${key}`"
            v-model="editableArgs[key]"
            class="rs-widget__input"
            :placeholder="argPlaceholder(key)"
          />
        </div>

        <div class="rs-widget__field">
          <label class="rs-widget__field-label" :for="rejectFieldId">Reject note</label>
          <textarea
            :id="rejectFieldId"
            v-model="rejectMessage"
            class="rs-widget__textarea"
            placeholder="Explain why this action should be rejected"
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
        <button type="button" class="rs-widget__ghost-button" :disabled="disabled || !editActionName.trim()" @click="submitEdit">
          <PencilLine :size="14" />
          <span>Submit edited action</span>
        </button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { Ban, CheckCircle2, PencilLine, ShieldCheck } from 'lucide-vue-next';

const props = defineProps<{
  interrupt?: unknown | null;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  (event: 'approve'): void;
  (event: 'reject', message: string): void;
  (event: 'edit', payload: { name: string; args: Record<string, any> }): void;
}>();

const rejectMessage = ref('Rejected by user');
const editActionName = ref('');
const editableArgs = ref<Record<string, string>>({});
const originalArgs = ref<Record<string, any>>({});

const rejectFieldId = `reject-${Math.random().toString(36).slice(2, 8)}`;
const actionNameFieldId = `action-${Math.random().toString(36).slice(2, 8)}`;

function extractEditableAction(interrupt: unknown): { name: string; args: Record<string, any> } | null {
  if (!interrupt || typeof interrupt !== 'object') return null;

  const source = interrupt as Record<string, any>;
  const actionRequests = Array.isArray(source.action_requests) ? source.action_requests : [];
  const firstAction = actionRequests[0] ?? source.action_request ?? source;

  const name =
    firstAction?.name ??
    firstAction?.action?.name ??
    firstAction?.tool?.name ??
    '';

  const args =
    firstAction?.args ??
    firstAction?.action?.args ??
    firstAction?.tool?.args ??
    firstAction?.action_input ??
    {};

  if (!name || typeof name !== 'string') return null;
  if (!args || typeof args !== 'object' || Array.isArray(args)) {
    return { name: name.trim(), args: {} };
  }

  return { name: name.trim(), args };
}

function stringifyArg(value: unknown): string {
  if (value === null || value === undefined) return '';
  if (typeof value === 'object') {
    try {
      return JSON.stringify(value, null, 2);
    } catch {
      return String(value);
    }
  }
  return String(value);
}

watch(
  () => props.interrupt,
  (nextInterrupt) => {
    const extracted = extractEditableAction(nextInterrupt);
    if (!extracted) {
      editActionName.value = '';
      originalArgs.value = {};
      editableArgs.value = {};
      return;
    }

    editActionName.value = extracted.name;
    originalArgs.value = { ...extracted.args };

    const mapped: Record<string, string> = {};
    Object.entries(extracted.args).forEach(([key, value]) => {
      mapped[key] = stringifyArg(value);
    });
    editableArgs.value = mapped;
  },
  { immediate: true },
);

const argKeys = computed(() => Object.keys(editableArgs.value));

function isStructuredArg(key: string): boolean {
  const value = originalArgs.value[key];
  return Array.isArray(value) || (typeof value === 'object' && value !== null);
}

function argPlaceholder(key: string): string {
  const value = originalArgs.value[key];
  if (typeof value === 'number') return 'Enter a number';
  if (typeof value === 'boolean') return 'true or false';
  if (isStructuredArg(key)) return 'Enter valid JSON';
  return 'Enter value';
}

function parseEditedValue(raw: string, original: unknown): unknown {
  if (Array.isArray(original) || (typeof original === 'object' && original !== null)) {
    return JSON.parse(raw || '{}');
  }
  if (typeof original === 'number') {
    const parsed = Number(raw);
    if (Number.isNaN(parsed)) throw new Error('Invalid number');
    return parsed;
  }
  if (typeof original === 'boolean') {
    return ['true', '1', 'yes', 'on'].includes(raw.trim().toLowerCase());
  }
  if (original === null && raw.trim() === '') {
    return null;
  }
  return raw;
}

function submitEdit() {
  try {
    const args: Record<string, any> = {};
    Object.keys(editableArgs.value).forEach((key) => {
      args[key] = parseEditedValue(editableArgs.value[key] ?? '', originalArgs.value[key]);
    });

    emit('edit', {
      name: editActionName.value.trim(),
      args,
    });
  } catch {
    alert('Invalid value in edited fields. Please check JSON/number fields.');
  }
}

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
