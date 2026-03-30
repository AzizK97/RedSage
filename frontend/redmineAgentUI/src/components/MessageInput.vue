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
}
input {
  flex: 1;
  padding: 0.65rem 0.8rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
}
button {
  padding: 0.65rem 1rem;
  border: 1px solid #2563eb;
  background: #2563eb;
  color: white;
  border-radius: 8px;
}
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>