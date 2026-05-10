<script setup lang="ts">
import AnimatedSection from './AnimatedSection.vue';
import { computed } from 'vue';
import { useTheme } from '../../../composables/useTheme';

const { isDark } = useTheme();

const descriptionTextClass = computed(() =>
  isDark.value
    ? 'text-surface-400'
    : 'text-surface-600'
);

const metricLabelClass = computed(() =>
  isDark.value
    ? 'text-white'
    : 'text-sage-900'
);

const metricDescClass = computed(() =>
  isDark.value
    ? 'text-surface-500'
    : 'text-surface-700'
);

const cardBorderClass = computed(() =>
  isDark.value
    ? 'hover:border-sage-500/25'
    : 'hover:border-sage-400/40'
);

const metrics = [
  { label: 'Routing Accuracy', value: '95%+', desc: 'Correct agent selection' },
  { label: 'Avg Latency', value: '<2s', desc: 'End-to-end response' },
  { label: 'Pass Rate', value: '92%+', desc: 'Benchmark test suite' },
  { label: 'Uptime', value: '99.9%', desc: 'Docker stack reliability' },
];
</script>

<template>
  <section class="relative py-24">
    <div class="absolute inset-0">
      <div class="absolute top-0 left-0 right-0 section-divider" />
    </div>

    <div class="max-w-7xl mx-auto px-6">
      <AnimatedSection class="text-center mb-12">
        <span class="inline-block text-xs font-semibold uppercase tracking-widest text-sage-400 mb-4">Performance</span>
        <h2 class="text-3xl sm:text-4xl font-extrabold tracking-tight">
          Validated by <span class="gradient-text">Benchmarks</span>
        </h2>
      </AnimatedSection>

        <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <AnimatedSection v-for="(m, i) in metrics" :key="m.label" :delay="i * 100">
          <div :class="['glass-card p-6 text-center transition-all', cardBorderClass]">
            <div class="text-3xl font-extrabold gradient-text-copper mb-1">{{ m.value }}</div>
            <div :class="['text-sm font-semibold mb-1', metricLabelClass]">{{ m.label }}</div>
            <div :class="['text-xs', metricDescClass]">{{ m.desc }}</div>
          </div>
        </AnimatedSection>
      </div>
    </div>
  </section>
</template>
