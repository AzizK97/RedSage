<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { Bot, Cpu, Route, MessageSquare, Sparkles, ShieldCheck, Zap, Container, ArrowRight, Github, ChevronDown } from 'lucide-vue-next';
import { useTheme } from '../../../composables/useTheme';

type ChatLine = {
  role: 'user' | 'agent';
  text: string;
};

const { isDark } = useTheme();

const subtextClass = computed(() => (isDark.value ? 'text-surface-400' : 'text-surface-600'));
const detailTextClass = computed(() => (isDark.value ? 'text-surface-500' : 'text-surface-700'));
const bubbleBodyClass = computed(() => (isDark.value ? 'text-surface-200' : 'text-surface-800'));
const glassCardClass = computed(() => (isDark.value ? 'bg-surface-900/50 border-surface-800' : 'bg-white/70 border-sage-200/30'));
const secondaryButtonClass = computed(() =>
  isDark.value
    ? 'bg-surface-900/50 border-surface-700 text-surface-300 hover:border-sage-500/40 hover:text-white'
    : 'bg-white/70 border-sage-300/40 text-sage-900 hover:border-sage-500/60 hover:text-sage-900'
);

const chatLines: ChatLine[] = [
  { role: 'user', text: 'What projects do we have?' },
  { role: 'agent', text: 'Found 3 projects: AI Platform, Backend API, and Mobile App. The AI Platform project has 24 open issues across 3 sprints.' },
  { role: 'user', text: 'List open issues in AI Platform assigned to me' },
  { role: 'agent', text: 'You have 5 open issues: #142 Model training pipeline, #156 API rate limiter, #178 Data validation, #189 Auth middleware, #201 Cache layer.' },
  { role: 'user', text: 'Create a new bug ticket: Login timeout on mobile' },
  { role: 'agent', text: 'Pending approval: Create issue "Login timeout on mobile" in AI Platform as Bug. Priority: Normal. Approve or reject?' },
];

const visibleLines = ref(0);
let timer: ReturnType<typeof setTimeout> | null = null;

function tick() {
  if (visibleLines.value < chatLines.length) {
    timer = setTimeout(() => {
      visibleLines.value += 1;
      tick();
    }, 1200);
  }
}

onMounted(() => tick());
onUnmounted(() => {
  if (timer) clearTimeout(timer);
});
</script>

<template>
  <section class="relative min-h-screen flex items-center pt-16 overflow-hidden">
    <div class="absolute inset-0">
      <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-sage-600/8 rounded-full blur-3xl animate-pulse-slow" />
      <div class="absolute bottom-1/3 right-1/4 w-80 h-80 bg-copper-600/6 rounded-full blur-3xl animate-pulse-slow" style="animation-delay: 2s" />
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-sage-500/3 rounded-full blur-3xl" />
      <div class="absolute inset-0 opacity-[0.025]"
        :style="{ backgroundImage: isDark ? 'linear-gradient(rgba(125,154,121,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(125,154,121,0.3) 1px, transparent 1px)' : 'linear-gradient(rgba(95,129,91,0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(95,129,91,0.15) 1px, transparent 1px)', backgroundSize: '60px 60px' }" />
    </div>

    <div class="relative max-w-7xl mx-auto px-6 py-20 grid lg:grid-cols-2 gap-16 items-center">
      <div class="space-y-8">
        <div class="animate-slide-up">
          <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-sage-500/10 border border-sage-500/20 text-sage-300 text-xs font-medium mb-6">
            <Sparkles :size="14" /> Multi-Agent AI for Redmine
          </div>
          <h1 class="text-5xl sm:text-6xl lg:text-7xl font-extrabold leading-[1.05] tracking-tight">
            Manage Redmine<br />
            <span class="gradient-text-hero">with Natural Language</span>
          </h1>
        </div>

        <p :class="['animate-slide-up-delayed text-lg leading-relaxed max-w-xl', subtextClass]">
          A supervisor-driven multi-agent system that routes your queries to specialized AI agents.
          Ask questions, create tickets, plan sprints, and generate reports — all through a simple chat interface.
        </p>

        <div class="animate-slide-up-delayed-2 flex flex-wrap gap-4">
          <a href="#get-started"
            class="group inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-copper-600 text-white font-semibold hover:bg-copper-500 transition-all shadow-xl shadow-copper-700/25 hover:shadow-copper-600/30">
            Get Started <ArrowRight :size="16" class="group-hover:translate-x-0.5 transition-transform" />
          </a>
          <a href="https://github.com/AzizK97/Redmine-Agent" target="_blank" rel="noopener noreferrer"
            :class="['inline-flex items-center gap-2 px-6 py-3 rounded-xl border font-semibold transition-all', secondaryButtonClass]">
            <Github :size="16" /> View on GitHub
          </a>
        </div>

        <div :class="['animate-slide-up-delayed-3 flex items-center gap-6 text-sm', detailTextClass]">
          <span class="flex items-center gap-1.5"><ShieldCheck :size="16" class="text-sage-500" /> Human-in-the-Loop</span>
          <span class="flex items-center gap-1.5"><Zap :size="16" class="text-copper-500" /> FastAPI + LangGraph</span>
          <span class="flex items-center gap-1.5"><Container :size="16" class="text-sage-500" /> Docker Ready</span>
        </div>
      </div>

      <div class="animate-fade-in relative">
        <div :class="['glass-card p-6 space-y-4 shadow-2xl shadow-sage-900/10 border', glassCardClass]">
          <div :class="['flex items-center gap-2 pb-3 border-b', isDark ? 'border-surface-800' : 'border-sage-200/30']">
            <div class="glow-dot" />
            <span :class="['text-sm font-medium', isDark ? 'text-surface-300' : 'text-sage-900']">RedSage Chat</span>
            <span :class="['ml-auto text-xs font-mono', isDark ? 'text-surface-500' : 'text-surface-600']">supervisor</span>
          </div>

          <div class="space-y-3 min-h-[320px]">
            <div v-for="(line, i) in chatLines.slice(0, visibleLines)" :key="i"
              :class="['flex animate-slide-up', line.role === 'user' ? 'justify-end' : 'justify-start']">
              <div :class="['max-w-[85%]', line.role === 'user' ? 'chat-bubble-user' : 'chat-bubble']">
                <div class="flex items-center gap-1.5 mb-1">
                  <Bot v-if="line.role === 'agent'" :size="12" class="text-sage-400" />
                  <MessageSquare v-else :size="12" class="text-copper-400" />
                  <span :class="['text-[10px] uppercase tracking-wider font-semibold', isDark ? 'text-surface-500' : 'text-surface-600']">{{ line.role }}</span>
                </div>
                <p :class="['text-sm leading-relaxed', bubbleBodyClass]">{{ line.text }}</p>
              </div>
            </div>
            <div v-if="visibleLines < chatLines.length" class="flex items-center gap-1.5 pl-2">
              <div class="w-1.5 h-1.5 rounded-full bg-sage-400 animate-bounce" style="animation-delay: 0ms" />
              <div class="w-1.5 h-1.5 rounded-full bg-sage-400 animate-bounce" style="animation-delay: 150ms" />
              <div class="w-1.5 h-1.5 rounded-full bg-sage-400 animate-bounce" style="animation-delay: 300ms" />
            </div>
          </div>
        </div>

        <div class="absolute -top-4 -right-4 w-20 h-20 bg-sage-500/5 rounded-2xl border border-sage-500/10 animate-float flex items-center justify-center">
          <Cpu :size="32" class="text-sage-500/40" />
        </div>
        <div class="absolute -bottom-4 -left-4 w-16 h-16 bg-copper-500/5 rounded-xl border border-copper-500/10 animate-float-delayed flex items-center justify-center">
          <Route :size="24" class="text-copper-500/40" />
        </div>
      </div>
    </div>

    <div :class="['absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 animate-bounce', isDark ? 'text-surface-500' : 'text-surface-600']">
      <span class="text-xs">Scroll to explore</span>
      <ChevronDown :size="16" />
    </div>
  </section>
</template>
