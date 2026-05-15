<template>
  <form class="rs-widget__composer" @submit.prevent="emitSend">
    <div class="rs-widget__composer-shell">
      <input
        :value="modelValue"
        class="rs-widget__composer-input"
        type="text"
        :placeholder="placeholder"
        :disabled="disabled"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      />

      <button type="submit" class="rs-widget__composer-send" :disabled="disabled || !modelValue.trim()">
        <SendHorizontal :size="16" />
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { SendHorizontal } from 'lucide-vue-next';

const props = defineProps<{
  modelValue: string;
  disabled?: boolean;
  placeholder?: string;
}>();

const emit = defineEmits<{
  (event: 'update:modelValue', value: string): void;
  (event: 'send'): void;
}>();

function emitSend() {
  if (props.disabled || !props.modelValue.trim()) return;
  emit('send');
}
</script>
