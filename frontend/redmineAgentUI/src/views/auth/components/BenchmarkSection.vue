<script setup lang="ts">
import AnimatedSection from './AnimatedSection.vue';
import { useTheme } from '../../../composables/useTheme';

const { isDark } = useTheme();

const metrics = [
  { label: 'Routing Accuracy', value: '95%+', desc: 'Correct agent selection' },
  { label: 'Avg Response', value: '<2s', desc: 'End-to-end latency' },
  { label: 'Time Saved', value: '4x', desc: 'vs. manual Redmine use' },
  { label: 'Uptime', value: '99.9%', desc: 'Platform reliability' },
];
</script>

<template>
  <section class="relative py-24">
    <div class="absolute inset-0">
      <div class="absolute top-0 left-0 right-0 section-divider" />
    </div>

    <div class="max-w-7xl mx-auto px-6">
      <AnimatedSection class="text-center mb-12">
        <span class="inline-block text-xs font-semibold uppercase tracking-widest text-sage-600 dark:text-sage-400 mb-4">Performance</span>
        <h2 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-sage-950 dark:text-white">
          Numbers That <span class="gradient-text">Speak for Themselves</span>
        </h2>
      </AnimatedSection>

      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-6" >
        <AnimatedSection v-for="(m, i) in metrics" :key="m.label" :delay="100 * i">
          <div class="glass-card p-6 text-center transition-all" :class="{ 'bg-white': !isDark, 'dark:bg-surface-900': isDark }">
            <div class="text-3xl font-extrabold gradient-text-copper mb-1">{{ m.value }}</div>
            <div class="text-sm font-semibold text-sage-900 dark:text-white mb-1">{{ m.label }}</div>
            <div class="text-xs text-surface-500 dark:text-surface-500">{{ m.desc }}</div>
          </div>
        </AnimatedSection>
      </div>
    </div>
  </section>
</template>
