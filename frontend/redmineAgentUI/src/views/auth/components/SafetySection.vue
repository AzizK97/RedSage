<script setup lang="ts">
import { Activity, ThumbsUp, ThumbsDown, Lock, Eye, UserCheck } from 'lucide-vue-next';
import AnimatedSection from './AnimatedSection.vue';
import { useTheme } from '@/composables/useTheme';

const trustFeatures = [
  { icon: Lock, title: 'Data Stays Yours', desc: 'RedSage reads and writes only through your existing Redmine API. No data leaves your infrastructure.' },
  { icon: Eye, title: 'Full Transparency', desc: 'Every action is logged. You can see exactly what RedSage did, why, and when.' },
  { icon: UserCheck, title: 'Approval Required', desc: 'Write operations are suspended until you approve. Nothing changes without your consent.' },
];

const { isDark } = useTheme();
</script>

<template>
  <section id="safety" class="relative py-32">
    <div class="absolute inset-0">
      <div class="absolute top-0 left-0 right-0 section-divider" />
    </div>

    <div class="max-w-7xl mx-auto px-6">
      <div class="grid lg:grid-cols-2 gap-16 items-center">
        <AnimatedSection>
          <span class="inline-block text-xs font-semibold uppercase tracking-widest text-sage-600 dark:text-sage-400 mb-4">Trust & Safety</span>
          <h2 class="text-4xl sm:text-5xl font-extrabold tracking-tight mb-6 text-sage-950 dark:text-white">
            You Approve.<br /><span class="gradient-text-copper">Nothing Else Ships.</span>
          </h2>
          <p class="text-lg text-surface-600 dark:text-surface-400 leading-relaxed mb-8">
            AI is powerful, but trust requires control. Every write operation in RedSage is suspended until you explicitly approve it. Read-only queries? Instant. Data changes? Your call.
          </p>

          <div class="space-y-5 mb-8">
            <div v-for="feat in trustFeatures" :key="feat.title" class="flex items-start gap-3">
              <div class="w-9 h-9 rounded-lg bg-sage-50 dark:bg-sage-500/10 border border-sage-100 dark:border-sage-500/15 flex items-center justify-center shrink-0 mt-0.5">
                <component :is="feat.icon" :size="18" class="text-sage-600 dark:text-sage-400" />
              </div>
              <div>
                <h4 class="text-sm font-bold text-sage-900 dark:text-white mb-0.5">{{ feat.title }}</h4>
                <p class="text-sm text-surface-600 dark:text-surface-400 leading-relaxed">{{ feat.desc }}</p>
              </div>
            </div>
          </div>
        </AnimatedSection>

        <AnimatedSection :delay="200">
          <div class="glass-card p-6 space-y-4" :class="{ 'bg-white': !isDark, 'dark:bg-surface-900': isDark }">
            <div class="flex items-center gap-2 pb-3 border-b border-sage-100 dark:border-surface-800">
              <Activity :size="16" class="text-amber-600 dark:text-amber-400" />
              <span class="text-sm font-semibold text-amber-700 dark:text-amber-300">Pending Your Approval</span>
            </div>

            <div class="rounded-xl bg-white dark:bg-surface-900/80 border border-sage-100 dark:border-surface-800 p-4 space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-xs font-semibold uppercase tracking-wider text-surface-400 dark:text-surface-500">Action</span>
                <span class="text-xs px-2 py-0.5 rounded-full bg-amber-50 dark:bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-500/20">Pending</span>
              </div>
              <p class="text-sm text-sage-900 dark:text-surface-200">Create issue <span class="font-mono text-copper-700 dark:text-copper-300">"Login timeout on mobile"</span> in AI Platform as Bug</p>
              <div class="flex items-center gap-2 text-xs text-surface-400 dark:text-surface-500">
                <span>Project: AI Platform</span>
                <span class="text-sage-200 dark:text-surface-700">|</span>
                <span>Priority: Normal</span>
                <span class="text-sage-200 dark:text-surface-700">|</span>
                <span>Tracker: Bug</span>
              </div>
            </div>

            <div class="flex gap-3 pt-2">
              <button class="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg bg-sage-600 text-white text-sm font-semibold hover:bg-sage-500 transition-colors shadow-md shadow-sage-300/20 dark:shadow-sage-700/20">
                <ThumbsUp :size="16" /> Approve
              </button>
              <button class="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg bg-white dark:bg-surface-800 border border-sage-200 dark:border-surface-700 text-sage-700 dark:text-surface-300 text-sm font-semibold hover:border-red-300 dark:hover:border-red-500/30 hover:text-red-600 dark:hover:text-red-400 transition-colors">
                <ThumbsDown :size="16" /> Reject
              </button>
            </div>

            <div class="rounded-xl bg-white dark:bg-surface-900/80 border border-sage-100 dark:border-surface-800 p-4 space-y-3 opacity-50">
              <div class="flex items-center justify-between">
                <span class="text-xs font-semibold uppercase tracking-wider text-surface-400 dark:text-surface-500">Action</span>
                <span class="text-xs px-2 py-0.5 rounded-full bg-sage-50 dark:bg-sage-500/10 text-sage-700 dark:text-sage-400 border border-sage-200 dark:border-sage-500/20">Approved</span>
              </div>
              <p class="text-sm text-sage-800 dark:text-surface-200 line-through opacity-60">Reassign issue #156 to Sarah</p>
            </div>
          </div>
        </AnimatedSection>
      </div>
    </div>
  </section>
</template>
