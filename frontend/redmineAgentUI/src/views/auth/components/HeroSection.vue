<script setup lang="ts">
import { useTheme } from '@/composables/useTheme';
import { ArrowRight, Play, Sparkles, ShieldCheck, Zap, Users } from 'lucide-vue-next';
import { computed } from 'vue';

const { isDark } = useTheme();

const dashboardDark = new URL('../../../assets/dashboard-view.png', import.meta.url).href;
const dashboardLight = new URL('../../../assets/dashboard-view-light.png', import.meta.url).href;

const imageUrl = computed(() => isDark.value ? dashboardDark : dashboardLight);

</script>

<template>
  <section class="relative min-h-screen flex items-center pt-16 overflow-hidden">
    <!-- <div class="absolute inset-0">
      <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-sage-200/40 dark:bg-sage-600/8 rounded-full blur-3xl animate-pulse-slow" />
      <div class="absolute bottom-1/3 right-1/4 w-80 h-80 bg-copper-200/30 dark:bg-copper-600/6 rounded-full blur-3xl animate-pulse-slow" style="animation-delay: 2s" />
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-sage-100/50 dark:bg-sage-500/3 rounded-full blur-3xl" />
      <div class="absolute inset-0 opacity-[0.03] dark:opacity-[0.025]"
        :style="{ backgroundImage: 'linear-gradient(rgba(95,129,91,0.4) 1px, transparent 1px), linear-gradient(90deg, rgba(95,129,91,0.4) 1px, transparent 1px)', backgroundSize: '60px 60px' }" />
    </div> -->

    <div class="relative max-w-7xl mx-auto px-6 py-20">
      <div class="text-center max-w-4xl mx-auto mb-14">
        <div class="animate-slide-up">
          <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-sage-100 dark:bg-sage-500/10 border border-sage-200 dark:border-sage-500/20 text-sage-700 dark:text-sage-300 text-xs font-medium mb-6">
            <Sparkles :size="14" /> AI-Powered Project Management
          </div>
          <h1 class="text-5xl sm:text-6xl lg:text-7xl font-extrabold leading-[1.05] tracking-tight text-sage-950 dark:text-white">
            Your Redmine,<br />
            <span class="gradient-text-hero">Powered by Conversation</span>
          </h1>
        </div>

        <p class="animate-slide-up-delayed text-lg sm:text-xl text-surface-600 dark:text-surface-400 leading-relaxed max-w-2xl mx-auto mt-8">
          RedSage turns natural language into Redmine actions. Ask questions, create tickets, plan sprints, and generate reports -- just by talking to your project.
        </p>

        <div class="animate-slide-up-delayed-2 flex flex-wrap justify-center gap-4 mt-10">
          <a href="#pricing"
            class="group inline-flex items-center gap-2 px-7 py-3.5 rounded-xl bg-copper-600 text-white font-semibold hover:bg-copper-500 transition-all shadow-lg shadow-copper-300/30 dark:shadow-copper-700/25 hover:shadow-copper-400/30">
            Start Free Trial <ArrowRight :size="16" class="group-hover:translate-x-0.5 transition-transform" />
          </a>
          <a href="#features"
            class="group inline-flex items-center gap-2 px-7 py-3.5 rounded-xl border border-sage-200 dark:border-surface-700 text-sage-700 dark:text-surface-300 font-semibold hover:border-sage-300 dark:hover:border-sage-500/40 hover:bg-sage-50 dark:hover:bg-surface-900/50 transition-all bg-white/60 dark:bg-surface-900/50">
            <Play :size="16" /> See How It Works
          </a>
        </div>

        <div class="animate-slide-up-delayed-3 flex items-center justify-center gap-8 text-sm text-surface-500 dark:text-surface-500 mt-10">
          <span class="flex items-center gap-1.5"><ShieldCheck :size="16" class="text-sage-600 dark:text-sage-500" /> Human-in-the-Loop</span>
          <span class="flex items-center gap-1.5"><Zap :size="16" class="text-copper-600 dark:text-copper-500" /> Instant Setup</span>
          <span class="flex items-center gap-1.5"><Users :size="16" class="text-sage-600 dark:text-sage-500" /> Team Ready</span>
        </div>
      </div>

      <!-- Dashboard Screenshot Placeholder -->
      <div class="animate-fade-in max-w-5xl mx-auto">
        <div class="relative rounded-2xl overflow-hidden border border-sage-200/60 dark:border-sage-700/20 shadow-2xl shadow-sage-300/20 dark:shadow-sage-900/10 bg-white dark:bg-surface-900">
          <!-- Browser chrome -->
          <div class="flex items-center gap-2 px-5 py-3 bg-sage-50 dark:bg-surface-900 border-b border-sage-100 dark:border-surface-800">
            <div class="w-3 h-3 rounded-full bg-red-300 dark:bg-red-500/60" />
            <div class="w-3 h-3 rounded-full bg-yellow-300 dark:bg-yellow-500/60" />
            <div class="w-3 h-3 rounded-full bg-green-300 dark:bg-green-500/60" />
            <div class="ml-4 flex-1 max-w-md">
              <div class="h-6 rounded-md bg-white dark:bg-surface-800 border border-sage-100 dark:border-surface-700 flex items-center px-3">
                <span class="text-xs text-surface-400 dark:text-surface-500 font-mono">app.redsage.io/dashboard</span>
              </div>
            </div>
          </div>

        
          <div class="relative aspect-[16/7.5] bg-gradient-to-br from-sage-50 to-surface-50 dark:from-surface-900 dark:to-surface-950 flex items-center justify-center">
            <img :src="imageUrl" alt="RedSage Dashboard" class="w-full h-full object-cover"/>
          </div>

        </div>

        <!-- Floating accent elements -->
        <div class="absolute -bottom-4 -left-4 w-20 h-20 bg-copper-100/60 dark:bg-copper-500/5 rounded-xl border border-copper-200/60 dark:border-copper-500/10 animate-float-delayed flex items-center justify-center">
          <Zap :size="24" class="text-copper-400/60 dark:text-copper-500/40" />
        </div>
      </div>
    </div>
  </section>
</template>
