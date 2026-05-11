<script setup lang="ts">
import { ShieldCheck, Terminal, Activity, ThumbsUp, ThumbsDown } from 'lucide-vue-next';
import AnimatedSection from './AnimatedSection.vue';
import { computed } from 'vue';
import { useTheme } from '../../../composables/useTheme';

const { isDark } = useTheme();

const descriptionTextClass = computed(() =>
  isDark.value
    ? 'text-surface-400'
    : 'text-surface-600'
);

const headingTextClass = computed(() =>
  isDark.value
    ? 'text-surface-300'
    : 'text-sage-900'
);

const itemTextClass = computed(() =>
  isDark.value
    ? 'text-surface-400'
    : 'text-surface-600'
);

const mutedTextClass = computed(() =>
  isDark.value
    ? 'text-surface-500'
    : 'text-surface-600'
);

const glassCardBorder = computed(() =>
  isDark.value
    ? 'border-surface-800'
    : 'border-sage-200/30'
);

const panelClass = computed(() =>
  isDark.value
    ? 'bg-surface-900/80 border-surface-800'
    : 'bg-white/70 border-sage-200/40'
);

const subPanelClass = computed(() =>
  isDark.value
    ? 'bg-surface-900/80 border-surface-800'
    : 'bg-sage-50/80 border-sage-200/40'
);

const actionTextClass = computed(() =>
  isDark.value
    ? 'text-surface-200'
    : 'text-sage-900'
);

const dividerTextClass = computed(() =>
  isDark.value
    ? 'text-surface-700'
    : 'text-sage-300'
);

const writeOps = [
  'Creating issues',
  'Updating status',
  'Reassigning issues',
  'Adding comments',
  'Logging time',
  'Creating / updating versions',
];
</script>

<template>
  <section id="safety" class="relative py-32">
    <div class="absolute inset-0">
      <div class="absolute top-0 left-0 right-0 section-divider" />
    </div>

    <div class="max-w-7xl mx-auto px-6">
      <div class="grid lg:grid-cols-2 gap-16 items-center">
        <AnimatedSection>
          <span class="inline-block text-xs font-semibold uppercase tracking-widest text-sage-400 mb-4">Safety First</span>
          <h2 class="text-4xl sm:text-5xl font-extrabold tracking-tight mb-6">
            Human-in-the-Loop <span class="gradient-text-copper">Protection</span>
          </h2>
          <p :class="['text-lg leading-relaxed mb-8', descriptionTextClass]">
            AI agents are powerful, but unchecked write operations are risky. Every action that modifies your Redmine data is suspended until you explicitly approve it.
          </p>

          <div class="space-y-4 mb-8">
            <h4 :class="['text-sm font-semibold uppercase tracking-wider', headingTextClass]">Protected Operations</h4>
            <div class="grid sm:grid-cols-2 gap-3">
              <div v-for="op in writeOps" :key="op" :class="['flex items-center gap-2.5 text-sm', itemTextClass]">
                <ShieldCheck :size="16" class="text-sage-500 shrink-0" />
                {{ op }}
              </div>
            </div>
          </div>

          <div :class="['flex items-center gap-3 text-sm', mutedTextClass]">
            <Terminal :size="16" class="text-copper-500" />
            <code :class="['font-mono', isDark ? 'text-copper-300' : 'text-copper-600']">POST /approve/&#123;thread_id&#125;</code>
          </div>
        </AnimatedSection>

        <AnimatedSection :delay="200">
          <div class="glass-card p-6 space-y-4">
            <div :class="['flex items-center gap-2 pb-3 border-b', glassCardBorder]">
              <Activity :size="16" class="text-amber-400" />
              <span class="text-sm font-semibold text-amber-300">Pending Approval</span>
            </div>

            <div :class="['rounded-xl p-4 space-y-3', panelClass]">
              <div class="flex items-center justify-between">
                <span class="text-xs font-semibold uppercase tracking-wider text-surface-500">Action</span>
                <span class="text-xs px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">Pending</span>
              </div>
              <p :class="['text-sm', actionTextClass]">Create issue <span class="font-mono text-copper-300">"Login timeout on mobile"</span> in AI Platform as Bug</p>
              <div :class="['flex items-center gap-2 text-xs', mutedTextClass]">
                <span>Project: AI Platform</span>
                <span :class="dividerTextClass">|</span>
                <span>Priority: Normal</span>
                <span :class="dividerTextClass">|</span>
                <span>Tracker: Bug</span>
              </div>
            </div>

            <div class="flex gap-3 pt-2">
              <button class="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg bg-sage-600 text-white text-sm font-semibold hover:bg-sage-500 transition-colors shadow-lg shadow-sage-700/20">
                <ThumbsUp :size="16" /> Approve
              </button>
              <button :class="['flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg border text-sm font-semibold transition-colors', isDark ? 'bg-surface-800 border-surface-700 text-surface-300 hover:border-red-500/30 hover:text-red-400' : 'bg-white border-sage-200/40 text-sage-800 hover:border-red-400/40 hover:text-red-500']">
                <ThumbsDown :size="16" /> Reject
              </button>
            </div>

            <div :class="['rounded-xl p-4 space-y-3 opacity-50', subPanelClass]">
              <div class="flex items-center justify-between">
                <span class="text-xs font-semibold uppercase tracking-wider text-surface-500">Action</span>
                <span class="text-xs px-2 py-0.5 rounded-full bg-sage-500/10 text-sage-400 border border-sage-500/20">Approved</span>
              </div>
              <p :class="['text-sm line-through opacity-60', actionTextClass]">Reassign issue #156 to Sarah</p>
            </div>
          </div>
        </AnimatedSection>
      </div>
    </div>
  </section>
</template>
