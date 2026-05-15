<script setup lang="ts">
import { Eye, ListChecks, CalendarDays, BarChart3 } from 'lucide-vue-next';
import AnimatedSection from './AnimatedSection.vue';
import { computed } from 'vue';
import { useTheme } from '@redsage/ui-core/composables/useTheme';

const { isDark } = useTheme();

const dashboardDark = new URL('../../../../../ui-core/src/assets/chat-view.png', import.meta.url).href;
const dashboardLight = new URL('../../../../../ui-core/src/assets/chat-view-light.png', import.meta.url).href;

const imageUrl = computed(() => isDark.value ? dashboardDark : dashboardLight);

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

const features = [
  {
    icon: Eye,
    name: 'Project Overview',
    gradient: 'from-sage-300 to-sage-500',
    shadowColor: 'shadow-sage-300/30 dark:shadow-sage-500/25',
    description: 'Get instant project summaries, team info, and status updates. Ask "What\'s the status of Backend API?" and get a complete picture.',
    examples: ['What projects exist?', 'Show team members for AI Platform', 'What is the status of Backend API?'],
  },
  {
    icon: ListChecks,
    name: 'Task Management',
    gradient: 'from-copper-400 to-copper-600',
    shadowColor: 'shadow-copper-300/30 dark:shadow-copper-500/25',
    description: 'Create, update, and manage tasks through conversation. Filter, assign, and track issues without touching a form.',
    examples: ['List open issues', 'Create ticket "Bug fix"', 'Log 2 hours on #142', 'Reassign #156 to Sarah'],
  },
  {
    icon: CalendarDays,
    name: 'Sprint Planning',
    gradient: 'from-amber-400 to-amber-600',
    shadowColor: 'shadow-amber-300/30 dark:shadow-amber-500/25',
    description: 'Plan sprints, track milestones, and analyze risks. Let AI help you organize your next iteration.',
    examples: ['Create sprint "Q2 Sprint 3"', 'Analyze sprint 2', 'What are the milestones?'],
  },
  {
    icon: BarChart3,
    name: 'Reports & Analytics',
    gradient: 'from-rose-400 to-rose-600',
    shadowColor: 'shadow-rose-300/30 dark:shadow-rose-500/25',
    description: 'Generate comprehensive project health reports with metrics, velocity trends, and actionable insights.',
    examples: ['Generate project report', 'Show velocity trends', 'What is the bug ratio?'],
  },
];
</script>

<template>
  <section id="features" class="relative py-32">
    <div class="max-w-7xl mx-auto px-6">
      <AnimatedSection class="text-center mb-20">
        <span class="inline-block text-xs font-semibold uppercase tracking-widest text-sage-600 dark:text-sage-400 mb-4">Features</span>
        <h2 class="text-4xl sm:text-5xl font-extrabold tracking-tight mb-6 text-sage-950 dark:text-white">
          Everything You Need,<br /><span class="gradient-text">One Conversation Away</span>
        </h2>
        <p class="text-lg text-surface-600 dark:text-surface-400 max-w-2xl mx-auto">
          RedSage understands your intent and routes to the right capability. No menus, no clicks -- just ask.
        </p>
      </AnimatedSection>

      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <AnimatedSection v-for="(feature, i) in features" :key="feature.name" :delay="i * 100">
          <div :class="['group glass-card p-6 h-full transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-sage-900/10 shimmer-bg', glassCardBorder, isDark ? 'hover:border-sage-500/25' : 'hover:border-sage-400/40']">
            <div :class="['w-12 h-12 rounded-xl bg-gradient-to-br flex items-center justify-center mb-5 shadow-lg group-hover:scale-110 transition-transform duration-300', feature.gradient, feature.shadowColor]">
              <component :is="feature.icon" :size="24" class="text-white" />
            </div>
            <h3 :class="['text-lg font-bold mb-2', isDark ? 'text-white' : 'text-sage-900']">{{ feature.name }}</h3>
            <p :class="['text-sm mb-5 leading-relaxed', agentDescriptionClass]">{{ feature.description }}</p>
            <div class="space-y-2">
              <div v-for="ex in feature.examples" :key="ex" :class="['flex items-start gap-2 text-xs', exampleTextClass]">
                <span class="text-copper-400 mt-0.5 shrink-0">&gt;</span>
                <span class="font-mono">{{ ex }}</span>
              </div>
            </div>
          </div>
        </AnimatedSection>
      </div>

      <AnimatedSection class="mt-20" :delay="200">
        <div class="max-w-5xl mx-auto">
          <div class="text-center mb-10">
            <h3 class="text-2xl sm:text-3xl font-extrabold text-sage-950 dark:text-white mb-3">Your New Project Command Center</h3>
            <p class="text-surface-600 dark:text-surface-400">A single chat interface that connects you to every Redmine capability.</p>
          </div>

          <div class="relative rounded-2xl overflow-hidden border border-sage-200/60 dark:border-sage-700/20 shadow-2xl shadow-sage-300/20 dark:shadow-sage-900/10 bg-white dark:bg-surface-900">
            <!-- App chrome -->
            <div class="flex items-center gap-3 px-5 py-3 bg-sage-50 dark:bg-surface-900 border-b border-sage-100 dark:border-surface-800">
              <div class="w-3 h-3 rounded-full bg-red-300 dark:bg-red-500/60" />
              <div class="w-3 h-3 rounded-full bg-yellow-300 dark:bg-yellow-500/60" />
              <div class="w-3 h-3 rounded-full bg-green-300 dark:bg-green-500/60" />
              <div class="ml-4 flex-1 max-w-md">
                <div class="h-6 rounded-md bg-white dark:bg-surface-800 border border-sage-100 dark:border-surface-700 flex items-center px-3">
                  <span class="text-xs text-surface-400 dark:text-surface-500 font-mono">app.redsage.io/chat</span>
                </div>
              </div>
            </div>

            
            <div class="relative aspect-[16/7.5] bg-gradient-to-br from-sage-50 to-surface-50 dark:from-surface-900 dark:to-surface-950 flex items-center justify-center">
                <img :src="imageUrl" alt="RedSage Chat Interface" class="w-full h-full object-cover" />
            </div>
          </div>
        </div>
      </AnimatedSection>
    </div>
  </section>
</template>
