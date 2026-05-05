<script setup lang="ts">
import AnimatedSection from './AnimatedSection.vue';

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
          <div class="glass-card p-6 text-center hover:border-sage-500/25 transition-all">
            <div class="text-3xl font-extrabold gradient-text-copper mb-1">{{ m.value }}</div>
            <div class="text-sm font-semibold text-white mb-1">{{ m.label }}</div>
            <div class="text-xs text-surface-500">{{ m.desc }}</div>
          </div>
        </AnimatedSection>
      </div>
    </div>
  </section>
</template>
