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
  gap: 0.5rem;
  padding: 1rem;
  background: #1f2937;
  border-top: 1px solid #374151;
}

input {
  flex: 1;
  padding: 0.65rem 0.8rem;
  border: 1px solid #4b5563;
  border-radius: 0.7rem;
  background: #374151;
  color: #fff;
}

input::placeholder {
  color: #9ca3af;
}

button {
  padding: 0.65rem 1rem;
  border: 1px solid #3b82f6;
  background: #3b82f6;
  color: white;
  border-radius: 0.7rem;
  font-weight: 600;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>