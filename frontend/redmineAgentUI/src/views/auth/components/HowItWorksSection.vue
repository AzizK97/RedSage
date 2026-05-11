<script setup lang="ts">
import { MessageSquare, Cpu, Layers, ShieldCheck, Eye, ListChecks, CalendarDays, BarChart3 } from 'lucide-vue-next';
import AnimatedSection from './AnimatedSection.vue';
import { computed } from 'vue';
import { useTheme } from '../../../composables/useTheme';

const { isDark } = useTheme();

const descriptionTextClass = computed(() =>
  isDark.value
    ? 'text-surface-400'
    : 'text-surface-600'
);

const stepTitleClass = computed(() =>
  isDark.value
    ? 'text-white'
    : 'text-sage-900'
);

const stepBgClass = computed(() =>
  isDark.value
    ? 'bg-surface-900'
    : 'bg-white/40'
);

const stepBorderClass = computed(() =>
  isDark.value
    ? 'border-sage-600/20'
    : 'border-sage-300/30'
);

const lineGradientClass = computed(() =>
  isDark.value
    ? 'from-sage-600/20 via-copper-500/30 to-sage-600/20'
    : 'from-sage-400/20 via-copper-400/25 to-sage-400/20'
);

const steps = [
  { icon: MessageSquare, title: 'Ask in Natural Language', description: 'Type your question or command in plain English. No API calls, no complex queries needed.' },
  { icon: Cpu, title: 'Supervisor Routes', description: 'The supervisor agent analyzes intent and dispatches to the optimal specialized agent.' },
  { icon: Layers, title: 'Agent Executes', description: 'The selected agent queries Redmine, processes data, and prepares a response or action.' },
  { icon: ShieldCheck, title: 'Human Approves', description: 'Write operations are suspended until you approve. Full control stays with you.' },
];

const agents = [
  { icon: Eye, name: 'Overview', gradient: 'from-sage-300 to-sage-500', shadowColor: 'shadow-sage-500/25' },
  { icon: ListChecks, name: 'Tasks', gradient: 'from-copper-400 to-copper-600', shadowColor: 'shadow-copper-500/25' },
  { icon: CalendarDays, name: 'Planning', gradient: 'from-amber-400 to-amber-600', shadowColor: 'shadow-amber-500/25' },
  { icon: BarChart3, name: 'Report', gradient: 'from-rose-400 to-rose-600', shadowColor: 'shadow-rose-500/25' },
];
</script>

<template>
  <section id="how-it-works" class="relative py-32">
    <div class="absolute inset-0">
      <div class="absolute top-0 left-0 right-0 section-divider" />
    </div>

    <div class="max-w-7xl mx-auto px-6">
      <AnimatedSection class="text-center mb-20">
        <span class="inline-block text-xs font-semibold uppercase tracking-widest text-sage-400 mb-4">Architecture</span>
        <h2 class="text-4xl sm:text-5xl font-extrabold tracking-tight mb-6">
          How It <span class="gradient-text">Works</span>
        </h2>
        <p :class="['text-lg max-w-2xl mx-auto', descriptionTextClass]">
          From natural language to Redmine action in four steps, with safety built in at every stage.
        </p>
      </AnimatedSection>

      <div class="grid md:grid-cols-4 gap-8 relative">
        <div :class="['hidden md:block absolute top-16 left-[12.5%] right-[12.5%] h-0.5 bg-gradient-to-r', lineGradientClass]" />

        <AnimatedSection v-for="(step, i) in steps" :key="step.title" :delay="i * 150">
          <div class="relative text-center group">
            <div :class="['relative inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-6 mx-auto transition-colors shadow-lg shadow-sage-900/10', stepBgClass, stepBorderClass, 'border', isDark ? 'group-hover:border-sage-500/40' : 'group-hover:border-sage-400/60']">
              <component :is="step.icon" :size="28" class="text-sage-400" />
              <div class="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-copper-600 text-white text-xs font-bold flex items-center justify-center shadow-lg shadow-copper-700/30">
                {{ i + 1 }}
              </div>
            </div>
            <h3 :class="['text-base font-bold mb-2', stepTitleClass]">{{ step.title }}</h3>
            <p :class="['text-sm leading-relaxed', descriptionTextClass]">{{ step.description }}</p>
          </div>
        </AnimatedSection>
      </div>

      <AnimatedSection class="mt-20">
        <div class="glass-card p-8 max-w-4xl mx-auto">
          <h3 :class="['text-center text-sm font-semibold uppercase tracking-wider mb-8', isDark ? 'text-surface-500' : 'text-surface-600']">Supervisor Routing Diagram</h3>
          <div class="flex flex-col items-center gap-6">
            <div :class="['flex items-center gap-3 px-5 py-3 rounded-xl border', isDark ? 'bg-surface-800/80 border-surface-700' : 'bg-sage-100/60 border-sage-300/40']">
              <MessageSquare :size="20" class="text-copper-400" />
              <span :class="['text-sm font-medium', isDark ? 'text-surface-300' : 'text-sage-900']">User Query</span>
            </div>

            <div class="w-px h-8 bg-gradient-to-b from-surface-600 to-sage-500/40" />

            <div class="relative flex items-center gap-3 px-6 py-3.5 rounded-xl bg-sage-500/10 border border-sage-500/25 animate-glow">
              <Cpu :size="20" class="text-sage-400" />
                <span :class="['text-sm font-bold', isDark ? 'text-sage-300' : 'text-sage-700']">Supervisor Agent</span>
              <span :class="['text-[10px] ml-2', isDark ? 'text-surface-500' : 'text-surface-600']">LangGraph</span>
            </div>

            <div class="w-full grid grid-cols-4 gap-4 pt-4">
              <div v-for="agent in agents" :key="agent.name" class="flex flex-col items-center gap-2">
                <div class="w-px h-6 bg-gradient-to-b from-sage-500/30 to-transparent" />
                <div :class="['w-10 h-10 rounded-lg bg-gradient-to-br flex items-center justify-center shadow-lg', agent.gradient, agent.shadowColor]">
                  <component :is="agent.icon" :size="20" class="text-white" />
                </div>
                <span :class="['text-[11px] font-medium text-center', isDark ? 'text-surface-500' : 'text-surface-600']">{{ agent.name }}</span>
              </div>
            </div>
          </div>
        </div>
      </AnimatedSection>
    </div>
  </section>
</template>
