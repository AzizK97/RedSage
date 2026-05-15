<script setup lang="ts">
import { MessageSquare, Cpu, Layers, ShieldCheck, Eye, ListChecks, CalendarDays, BarChart3 } from 'lucide-vue-next';
import AnimatedSection from './AnimatedSection.vue';
import { useTheme } from '@redsage/ui-core/composables/useTheme';

const steps = [
  { icon: MessageSquare, title: 'Ask in Plain Language', description: 'Type your question or command naturally. No special syntax, no learning curve -- just talk to RedSage like you would a colleague.' },
  { icon: Cpu, title: 'AI Routes Intelligently', description: 'RedSage\'s supervisor analyzes your intent and dispatches to the optimal specialized agent in milliseconds.' },
  { icon: Layers, title: 'Action Executed', description: 'The right agent queries your Redmine instance, processes data, and prepares a clear response or action.' },
  { icon: ShieldCheck, title: 'You Stay in Control', description: 'Write operations require your approval. Nothing changes in Redmine without your explicit sign-off.' },
];

const agents = [
  { icon: Eye, name: 'Overview', gradient: 'from-sage-300 to-sage-500', shadowColor: 'shadow-sage-300/30 dark:shadow-sage-500/25' },
  { icon: ListChecks, name: 'Tasks', gradient: 'from-copper-400 to-copper-600', shadowColor: 'shadow-copper-300/30 dark:shadow-copper-500/25' },
  { icon: CalendarDays, name: 'Planning', gradient: 'from-amber-400 to-amber-600', shadowColor: 'shadow-amber-300/30 dark:shadow-amber-500/25' },
  { icon: BarChart3, name: 'Report', gradient: 'from-rose-400 to-rose-600', shadowColor: 'shadow-rose-300/30 dark:shadow-rose-500/25' },
];

const { isDark } = useTheme();
</script>

<template>
  <section id="how-it-works" class="relative py-32">
    <div class="absolute inset-0">
      <div class="absolute top-0 left-0 right-0 section-divider" />
    </div>

    <div class="max-w-7xl mx-auto px-6">
      <AnimatedSection class="text-center mb-20">
        <span class="inline-block text-xs font-semibold uppercase tracking-widest text-sage-600 dark:text-sage-400 mb-4">How It Works</span>
        <h2 class="text-4xl sm:text-5xl font-extrabold tracking-tight mb-6 text-sage-950 dark:text-white">
          From Question to Action<br /><span class="gradient-text">in Seconds</span>
        </h2>
        <p class="text-lg text-surface-600 dark:text-surface-400 max-w-2xl mx-auto">
          Four simple steps, with safety built in at every stage. Your data stays yours.
        </p>
      </AnimatedSection>

      <div class="grid md:grid-cols-4 gap-8 relative">
        <div class="hidden md:block absolute top-16 left-[12.5%] right-[12.5%] h-0.5 bg-gradient-to-r from-sage-200/60 via-copper-300/40 to-sage-200/60 dark:from-sage-600/20 dark:via-copper-500/30 dark:to-sage-600/20" />

        <AnimatedSection v-for="(step, i) in steps" :key="step.title" :delay="150 * i">
          <div class="relative text-center group">
            <div class="relative inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-white dark:bg-surface-900 border border-sage-200 dark:border-sage-600/20 mb-6 mx-auto group-hover:border-sage-300 dark:group-hover:border-sage-500/40 transition-colors shadow-md dark:shadow-lg dark:shadow-sage-900/10">
              <component :is="step.icon" :size="28" class="text-sage-600 dark:text-sage-400" />
              <div class="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-copper-600 text-white text-xs font-bold flex items-center justify-center shadow-md shadow-copper-300/30 dark:shadow-copper-700/30">
                {{ i + 1 }}
              </div>
            </div>
            <h3 class="text-base font-bold text-sage-900 dark:text-white mb-2">{{ step.title }}</h3>
            <p class="text-sm text-surface-600 dark:text-surface-400 leading-relaxed">{{ step.description }}</p>
          </div>
        </AnimatedSection>
      </div>

      <AnimatedSection class="mt-20">
        <div class="glass-card p-8 max-w-4xl mx-auto" :class="{ 'bg-white': !isDark, 'dark:bg-surface-900': isDark }">
          <h3 class="text-center text-sm font-semibold uppercase tracking-wider text-surface-400 dark:text-surface-500 mb-8">Intelligent Routing Under the Hood</h3>
          <div class="flex flex-col items-center gap-6">
        <div class="flex items-center gap-3 px-5 py-3 rounded-xl bg-white dark:bg-surface-800/80 border border-sage-200 dark:border-surface-700 shadow-sm">
          <MessageSquare :size="20" class="text-copper-600 dark:text-copper-400" />
          <span class="text-sm font-medium text-sage-800 dark:text-surface-300">Your Query</span>
        </div>

        <div class="w-px h-8 bg-gradient-to-b from-sage-200 to-sage-400/40 dark:from-surface-600 dark:to-sage-500/40" />

        <div class="relative flex items-center gap-3 px-6 py-3.5 rounded-xl bg-sage-50 dark:bg-sage-500/10 border border-sage-300 dark:border-sage-500/25 shadow-md shadow-sage-200/40 dark:shadow-none animate-glow">
          <Cpu :size="20" class="text-sage-600 dark:text-sage-400" />
          <span class="text-sm font-bold text-sage-700 dark:text-sage-300">RedSage Supervisor</span>
          <span class="text-[10px] text-surface-400 dark:text-surface-500 ml-2">AI-Powered</span>
        </div>

        <div class="w-full grid grid-cols-4 gap-4 pt-4">
          <div v-for="agent in agents" :key="agent.name" class="flex flex-col items-center gap-2">
            <div class="w-px h-6 bg-gradient-to-b from-sage-300/40 to-transparent dark:from-sage-500/30 dark:to-transparent" />
            <div :class="['w-10 h-10 rounded-lg bg-gradient-to-br flex items-center justify-center shadow-md', agent.gradient, agent.shadowColor]">
          <component :is="agent.icon" :size="20" class="text-white" />
            </div>
            <span class="text-[11px] text-surface-500 dark:text-surface-500 font-medium text-center">{{ agent.name }}</span>
          </div>
        </div>
          </div>
        </div>
      </AnimatedSection>
    </div>
  </section>
</template>
