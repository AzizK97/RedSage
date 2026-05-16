<script setup lang="ts">
import { ArrowRight, Flame } from 'lucide-vue-next';
import AnimatedSection from './AnimatedSection.vue';
import { computed } from 'vue';
import { useTheme } from '@redsage/ui-core/composables/useTheme';

const { isDark } = useTheme();

const descriptionTextClass = computed(() =>
  isDark.value
    ? 'text-surface-400'
    : 'text-surface-600'
);

const secondaryButtonClass = computed(() =>
  isDark.value
    ? 'bg-surface-900/50 border-surface-700 text-surface-300 hover:border-sage-500/40 hover:text-white'
    : 'bg-white/70 border-sage-300/40 text-sage-900 hover:border-sage-500/60 hover:text-sage-900'
);

const emit = defineEmits<{ (e: 'start-onboarding'): void }>();
</script>

<template>
  <section class="relative py-32">
    <div class="absolute inset-0">
      <div class="absolute top-0 left-0 right-0 section-divider" />
      <div class="absolute inset-0 bg-gradient-to-b from-sage-500/3 via-transparent to-transparent" />
    </div>

    <div class="relative max-w-4xl mx-auto px-6 text-center">
      <AnimatedSection>
        <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-copper-50 dark:bg-copper-500/10 border border-copper-200 dark:border-copper-500/20 text-copper-700 dark:text-copper-300 text-xs font-medium mb-8">
          <Flame :size="14" /> Ready to Transform Your Workflow
        </div>
        <h2 class="text-4xl sm:text-5xl font-extrabold tracking-tight mb-6 text-sage-950 dark:text-white">
          Stop Clicking.<br /><span class="gradient-text-hero">Start Asking.</span>
        </h2>
        <p :class="['text-lg max-w-xl mx-auto mb-10', descriptionTextClass]">
          Join teams using RedSage to manage Redmine through natural language. Free to start, powerful at scale.
        </p>
        <div class="flex flex-wrap justify-center gap-4">
          <button
            @click="emit('start-onboarding')"
            class="group inline-flex items-center gap-2.5 px-8 py-4 rounded-xl bg-copper-600 text-white font-bold text-lg hover:bg-copper-500 transition-all shadow-xl shadow-copper-300/30 dark:shadow-copper-700/25 hover:shadow-copper-400/30">
            Start Free Trial <ArrowRight :size="20" class="group-hover:translate-x-0.5 transition-transform" />
          </button>
          <a href="#features"
            class="inline-flex items-center gap-2.5 px-8 py-4 rounded-xl border font-bold text-lg transition-all" :class="secondaryButtonClass">
            Explore Features
          </a>
        </div>
      </AnimatedSection>
    </div>
  </section>
</template>
