<script setup lang="ts">
import { computed, ref } from "vue";
import { Send } from 'lucide-vue-next';

const props = defineProps<{
  disabled: boolean;
  modelValue?: string;
}>();

const emit = defineEmits<{
  (e: "send", text: string): void;
  (e: "update:modelValue", value: string): void;
}>();

const internalText = ref("");

const text = computed({
  get: () => props.modelValue ?? internalText.value,
  set: (value: string) => {
    if (props.modelValue !== undefined) {
      emit("update:modelValue", value);
      return;
    }
    internalText.value = value;
  },
});

function submit() {
  const value = text.value.trim();
  if (!value || props.disabled) return;
  emit("send", value);
  text.value = "";
}
</script>

<template>
  <form class="flex justify-center w-full px-6 py-4" @submit.prevent="submit">
    <div 
      :class="[
        'flex items-center gap-3 flex-1 max-w-3xl p-1.5 rounded-2xl bg-surface-900 border border-surface-800 shadow-2xl transition-all duration-300 ring-1 ring-white/5',
        disabled ? 'opacity-60 grayscale cursor-not-allowed' : 'focus-within:border-sage-500/40 focus-within:ring-4 focus-within:ring-sage-500/5'
      ]"
    >
      <input
        v-model="text"
        type="text"
        placeholder="How can I help you today?"
        :disabled="disabled"
        class="flex-1 bg-transparent border-none px-4 py-2 text-surface-100 text-sm outline-none placeholder:text-surface-600"
      />

      <button
        type="submit"
        :disabled="disabled || !text.trim()"
        class="w-10 h-10 rounded-xl bg-gradient-to-br from-sage-600 to-sage-500 text-white flex items-center justify-center shadow-lg shadow-sage-900/30 enabled:hover:scale-105 enabled:active:scale-95 disabled:opacity-30 disabled:grayscale transition-all"
        aria-label="Send message"
      >
        <Send :size="18" />
      </button>
    </div>
  </form>
</template>