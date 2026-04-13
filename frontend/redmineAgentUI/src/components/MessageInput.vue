<script setup lang="ts">
import { ref } from "vue";
import { Send } from '@lucide/vue';

const props = defineProps<{
  disabled: boolean;
}>();

const emit = defineEmits<{
  (e: "send", text: string): void;
}>();

const text = ref("");

function submit() {
  const value = text.value.trim();
  if (!value || props.disabled) return;
  emit("send", value);
  text.value = "";
}
</script>

<template>
  <form class="input-wrap" @submit.prevent="submit">
    <div class="composer" :class="{ 'is-disabled': disabled }">

      <input
        v-model="text"
        type="text"
        placeholder="How can I help you today?"
        :disabled="disabled"
      />

      <button
        type="submit"
        class="icon-btn send-btn"
        :disabled="disabled || !text.trim()"
        aria-label="Send message"
      >
        <Send />
        <!-- <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 6v12M6 12l6-6 6 6" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
        </svg> -->
      </button>
    </div>
  </form>
</template>

<style scoped>
.input-wrap {
  display: flex;
  justify-content: center;
  padding-bottom: 1.5vw;
}

.composer {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex: 1;
  max-width: 760px;
  padding: var(--space-sm);
  border: 1px solid transparent;
  border-radius: 50px;
  background: var(--bg-secondary);
}

.composer:focus-within {
  border-color: #252525;
}

.composer.is-disabled {
  opacity: 0.7;
}

input {
  flex: 1;
  min-width: 0;
  padding: var(--space-sm) var(--space-xs);
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: var(--text-base);
  line-height: 1.5;
}

input:focus {
  outline: none;
}

input::placeholder {
  color: var(--text-secondary);
}

.model-select,
.icon-btn {
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-secondary);
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  height: 2rem;
  transition: all var(--transition-fast);
}

.model-select {
  padding: 0 var(--space-sm);
  font-size: var(--text-sm);
}

.icon-btn {
  cursor: pointer;
  width: 2rem;
  padding: 0;
}

.icon-btn svg,
.model-select svg {
  width: 1rem;
  height: 1rem;
}

.icon-plus {
  border-color: var(--border-subtle);
}

.model-select:hover:not(:disabled),
.icon-btn:hover:not(:disabled) {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.send-btn {
  background: #c03a2a;
  color: var(--text-primary);
}

.send-btn:hover:not(:disabled) {
  background: #d94a3a;
}

.icon-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>