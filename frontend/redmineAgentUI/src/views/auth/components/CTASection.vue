<script setup lang="ts">
import { Play, ArrowRight, Github, Flame } from 'lucide-vue-next';
import AnimatedSection from './AnimatedSection.vue';
</script>

<template>
  <section class="relative py-32">
    <div class="absolute inset-0">
      <div class="absolute top-0 left-0 right-0 section-divider" />
      <div class="absolute inset-0 bg-gradient-to-b from-sage-500/3 via-transparent to-transparent" />
    </div>

    <div class="relative max-w-4xl mx-auto px-6 text-center">
      <AnimatedSection>
        <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-copper-500/10 border border-copper-500/20 text-copper-300 text-xs font-medium mb-8">
          <Flame :size="14" /> Ready to Ship
        </div>
        <h2 class="text-4xl sm:text-5xl font-extrabold tracking-tight mb-6">
          Transform Your<br /><span class="gradient-text-hero">Redmine Workflow</span>
        </h2>
        <p class="text-lg text-surface-400 max-w-xl mx-auto mb-10">
          Stop clicking through menus. Start asking questions. Let AI agents handle the heavy lifting while you stay in control.
        </p>
        <div class="flex flex-wrap justify-center gap-4">
          <a href="https://github.com/AzizK97/Redmine-Agent" target="_blank" rel="noopener noreferrer"
            class="group inline-flex items-center gap-2.5 px-8 py-4 rounded-xl bg-copper-600 text-white font-bold text-lg hover:bg-copper-500 transition-all shadow-xl shadow-copper-700/25 hover:shadow-copper-600/30">
            <Play :size="20" /> Get Started <ArrowRight :size="20" class="group-hover:translate-x-0.5 transition-transform" />
          </a>
          <a href="https://github.com/AzizK97/Redmine-Agent" target="_blank" rel="noopener noreferrer"
            class="inline-flex items-center gap-2.5 px-8 py-4 rounded-xl border border-surface-700 text-surface-300 font-bold text-lg hover:border-sage-500/40 hover:text-white transition-all bg-surface-900/50">
            <Github :size="20" /> Star on GitHub
          </a>
        </div>
      </AnimatedSection>
    </div>
  </section>
</template>
