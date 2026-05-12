<template>
  <nav class="rs-widget__tabs" aria-label="Widget navigation">
    <button
      type="button"
      class="rs-widget__tab"
      :class="{ 'rs-widget__tab--active': modelValue === 'chat' }"
      @click="$emit('update:modelValue', 'chat')"
    >
      Chat
      <span v-if="modelValue === 'chat'" class="rs-widget__tab-indicator" />
    </button>

    <button
      type="button"
      class="rs-widget__tab"
      :class="{ 'rs-widget__tab--active': modelValue === 'history' }"
      @click="$emit('update:modelValue', 'history')"
    >
      History
      <span v-if="modelValue === 'history'" class="rs-widget__tab-indicator" />
    </button>
  </nav>
</template>

<script setup lang="ts">
export type WidgetView = 'chat' | 'history';

defineProps<{
  modelValue: WidgetView;
}>();

defineEmits<{
  (event: 'update:modelValue', value: WidgetView): void;
}>();
</script>
