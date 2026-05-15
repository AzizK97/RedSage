<script setup lang="ts">
import { Globe, RefreshCw, Clock, BarChart3, Cpu, Zap, Container, Terminal } from 'lucide-vue-next';
import AnimatedSection from './AnimatedSection.vue';
import { useTheme } from '@redsage/ui-core/composables/useTheme';

const capabilities = [
  { icon: Globe, name: 'Works With Your Redmine', desc: 'Connects to any Redmine instance via API. No migration, no setup changes, no risk to existing workflows.' },
  { icon: Cpu, name: 'AI-Powered Routing', desc: 'Supervisor agent analyzes intent and dispatches to the right specialist agent automatically.' },
  { icon: Zap, name: 'Instant Responses', desc: 'Read-only queries return in under 2 seconds. Get answers faster than navigating the Redmine UI.' },
  { icon: Container, name: 'Cloud or Self-Hosted', desc: 'Deploy on your infrastructure or use our managed cloud. Your data never leaves your control.' },
  { icon: RefreshCw, name: 'Real-Time Sync', desc: 'Changes reflect in Redmine instantly. No stale data, no sync delays, no cache issues.' },
  { icon: Clock, name: 'Audit Trail', desc: 'Every action is logged with timestamps, user context, and full reasoning chain for compliance.' },
  { icon: Terminal, name: 'Chat & API Access', desc: 'Use the conversational UI or integrate via REST API. Both interfaces share the same backend.' },
  { icon: BarChart3, name: 'Usage Analytics', desc: 'Track team adoption, query patterns, and time saved. Measure the ROI of AI-assisted management.' },
];

const { isDark } = useTheme();

const delays = [0, 80, 160, 240, 320, 400, 480, 560];
</script>

<template>
  <section id="tech-stack" class="relative py-32">
    <div class="absolute inset-0">
      <div class="absolute top-0 left-0 right-0 section-divider" />
    </div>

    <div class="max-w-7xl mx-auto px-6">
      <AnimatedSection class="text-center mb-16">
        <span class="inline-block text-xs font-semibold uppercase tracking-widest text-sage-600 dark:text-sage-400 mb-4">Platform</span>
        <h2 class="text-4xl sm:text-5xl font-extrabold tracking-tight mb-6 text-sage-950 dark:text-white">
          Built for <span class="gradient-text">Enterprise Reliability</span>
        </h2>
        <p class="text-lg text-surface-600 dark:text-surface-400 max-w-2xl mx-auto">
          Production-grade infrastructure with the flexibility to match your team's needs.
        </p>
      </AnimatedSection>

      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <AnimatedSection v-for="(item, i) in capabilities" :key="item.name" :delay="delays[i]">
          <div class="group glass-card p-5 transition-all duration-300 hover:-translate-y-0.5" :class="{ 'bg-white': !isDark, 'dark:bg-surface-900': isDark }">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-9 h-9 rounded-lg bg-sage-50 dark:bg-sage-500/10 border border-sage-100 dark:border-sage-500/15 flex items-center justify-center group-hover:bg-sage-100 dark:group-hover:bg-sage-500/15 group-hover:border-sage-200 dark:group-hover:border-sage-500/25 transition-colors">
                <component :is="item.icon" :size="18" class="text-sage-600 dark:text-sage-400" />
              </div>
              <h4 class="text-sm font-bold text-sage-900 dark:text-white">{{ item.name }}</h4>
            </div>
            <p class="text-xs text-surface-500 dark:text-surface-500 leading-relaxed">{{ item.desc }}</p>
          </div>
        </AnimatedSection>
      </div>
    </div>
  </section>
</template>
