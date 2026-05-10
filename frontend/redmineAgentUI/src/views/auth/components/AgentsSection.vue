<script setup lang="ts">
import { Eye, ListChecks, CalendarDays, BarChart3 } from 'lucide-vue-next';
import AnimatedSection from './AnimatedSection.vue';
import { computed } from 'vue';
import { useTheme } from '../../../composables/useTheme';

const { isDark } = useTheme();

const descriptionTextClass = computed(() =>
  isDark.value
    ? 'text-surface-400'
    : 'text-surface-600'
);

const agentDescriptionClass = computed(() =>
  isDark.value
    ? 'text-surface-400'
    : 'text-surface-600'
);

const exampleTextClass = computed(() =>
  isDark.value
    ? 'text-surface-500'
    : 'text-surface-700'
);

const glassCardBorder = computed(() =>
  isDark.value
    ? 'border-surface-800'
    : 'border-sage-200/30'
);

const agents = [
  {
    icon: Eye,
    name: 'Overview Agent',
    gradient: 'from-sage-300 to-sage-500',
    shadowColor: 'shadow-sage-500/25',
    description: 'Project summaries, team info, and general status queries.',
    examples: ['What projects exist?', 'Show team members for AI Platform', 'What is the status of Backend API?'],
  },
  {
    icon: ListChecks,
    name: 'Tasks Agent',
    gradient: 'from-copper-400 to-copper-600',
    shadowColor: 'shadow-copper-500/25',
    description: 'Task listing, filtering, creation, status updates, and time logging.',
    examples: ['List open issues', 'Create ticket "Bug fix"', 'Log 2 hours on #142', 'Reassign #156 to Sarah'],
  },
  {
    icon: CalendarDays,
    name: 'Planning Agent',
    gradient: 'from-amber-400 to-amber-600',
    shadowColor: 'shadow-amber-500/25',
    description: 'Sprint management, milestone tracking, and risk analysis.',
    examples: ['Create sprint "Q2 Sprint 3"', 'Analyze sprint 2', 'What are the milestones?'],
  },
  {
    icon: BarChart3,
    name: 'Report Agent',
    gradient: 'from-rose-400 to-rose-600',
    shadowColor: 'shadow-rose-500/25',
    description: 'Complete project health reports with metrics and analysis.',
    examples: ['Generate project report', 'Show velocity trends', 'What is the bug ratio?'],
  },
];
</script>

<template>
  <section id="agents" class="relative py-32">
    <div class="max-w-7xl mx-auto px-6">
      <AnimatedSection class="text-center mb-20">
        <span class="inline-block text-xs font-semibold uppercase tracking-widest text-sage-400 mb-4">Specialized Intelligence</span>
        <h2 class="text-4xl sm:text-5xl font-extrabold tracking-tight mb-6">
          Four Agents, <span class="gradient-text">One Supervisor</span>
        </h2>
        <p :class="['text-lg max-w-2xl mx-auto', descriptionTextClass]">
          Each agent is purpose-built for a specific domain. The supervisor analyzes your request and routes it to the right agent automatically.
        </p>
      </AnimatedSection>

      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <AnimatedSection v-for="(agent, i) in agents" :key="agent.name" :delay="i * 100">
          <div :class="['group glass-card p-6 h-full transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-sage-900/10 shimmer-bg', glassCardBorder, isDark.value ? 'hover:border-sage-500/25' : 'hover:border-sage-400/40']">
            <div :class="['w-12 h-12 rounded-xl bg-gradient-to-br flex items-center justify-center mb-5 shadow-lg group-hover:scale-110 transition-transform duration-300', agent.gradient, agent.shadowColor]">
              <component :is="agent.icon" :size="24" class="text-white" />
            </div>
            <h3 :class="['text-lg font-bold mb-2', isDark.value ? 'text-white' : 'text-sage-900']">{{ agent.name }}</h3>
            <p :class="['text-sm mb-5 leading-relaxed', agentDescriptionClass]">{{ agent.description }}</p>
            <div class="space-y-2">
              <div v-for="ex in agent.examples" :key="ex" :class="['flex items-start gap-2 text-xs', exampleTextClass]">
                <span class="text-copper-400 mt-0.5 shrink-0">&gt;</span>
                <span class="font-mono">{{ ex }}</span>
              </div>
            </div>
          </div>
        </AnimatedSection>
      </div>
    </div>
  </section>
</template>
