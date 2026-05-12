<template>
  <header class="rs-widget__header">
    <div class="rs-widget__brand">
      <div class="rs-widget__brand-row">
        <div class="rs-widget__brand-logo" aria-hidden="true">
          <MessageCircleMore :size="18" />
        </div>
        <button
          v-if="showBack"
          type="button"
          class="rs-widget__icon-button"
          aria-label="Back"
          @click="$emit('back')"
          style="margin-right:8px"
        >
          <ArrowLeft :size="16" />
        </button>
        <div class="rs-widget__title-wrap">
          <h2 class="rs-widget__title">{{ title }}</h2>
          <p class="rs-widget__subtitle">{{ subtitle }}</p>
        </div>
      </div>
    </div>

    <div class="rs-widget__header-actions">
      <button
        type="button"
        class="rs-widget__icon-button"
        :aria-label="expanded ? 'Collapse widget' : 'Expand widget'"
        @click="$emit('toggle-expand')"
      >
        <Maximize2 v-if="!expanded" :size="16" />
        <Minimize2 v-else :size="16" />
      </button>
      <button
        type="button"
        class="rs-widget__icon-button ai-chat-close"
        aria-label="Close widget"
        @click="$emit('close')"
      >
        <X :size="16" />
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { MessageCircleMore, Maximize2, Minimize2, X, ArrowLeft } from 'lucide-vue-next';

defineProps<{
  title: string;
  subtitle: string;
  expanded: boolean;
  showBack?: boolean;
}>();

defineEmits<{
  (event: 'close'): void;
  (event: 'toggle-expand'): void;
  (event: 'back'): void;
}>();
</script>
