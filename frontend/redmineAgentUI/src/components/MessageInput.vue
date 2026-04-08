<script setup lang="ts">
import { ref } from "vue";

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
  <div class="input-wrap">
    <input
      v-model="text"
      type="text"
      placeholder="Type your message..."
      :disabled="disabled"
      @keydown.enter="submit"
    />
    <button :disabled="disabled || !text.trim()" @click="submit">Send</button>
  </div>
</template>

<style scoped>
.input-wrap {
  display: flex;
  gap: var(--space-md);
  padding: var(--space-lg) var(--space-md);
  background: var(--bg-primary);
  border-top: 1px solid var(--border-subtle);
  justify-content: center;
}

input {
  flex: 1;
  max-width: 900px;
  padding: var(--space-md) var(--space-lg);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: var(--text-base);
  line-height: 1.5;
  transition: all var(--transition-fast);
}

input:focus {
  outline: none;
  border-color: var(--accent-blue);
  background: var(--bg-tertiary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

input::placeholder {
  color: var(--text-secondary);
}

button {
  padding: var(--space-md) var(--space-lg);
  border: none;
  background: var(--accent-blue);
  color: white;
  border-radius: var(--radius-lg);
  font-weight: 500;
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  min-width: 4rem;
}

button:hover:not(:disabled) {
  background: var(--accent-blue-hover);
  transform: translateY(-1px);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>