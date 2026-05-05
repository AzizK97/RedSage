<script setup lang="ts">
import { Terminal, Zap } from 'lucide-vue-next';
import AnimatedSection from './AnimatedSection.vue';

const steps = [
  { code: 'git clone https://github.com/AzizK97/Redmine-Agent.git', label: 'Clone the repository' },
  { code: 'cp .env.example .env', label: 'Configure environment' },
  { code: 'docker compose up -d', label: 'Launch the stack' },
  { code: 'python main.py', label: 'Start chatting' },
];

function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text);
}
</script>

<template>
  <section id="get-started" class="relative py-32">
    <div class="absolute inset-0">
      <div class="absolute top-0 left-0 right-0 section-divider" />
      <div class="absolute bottom-1/3 left-1/3 w-96 h-96 bg-sage-500/5 rounded-full blur-3xl" />
    </div>

    <div class="relative max-w-7xl mx-auto px-6">
      <AnimatedSection class="text-center mb-16">
        <span class="inline-block text-xs font-semibold uppercase tracking-widest text-sage-400 mb-4">Quick Start</span>
        <h2 class="text-4xl sm:text-5xl font-extrabold tracking-tight mb-6">
          Up and Running <span class="gradient-text-copper">in Minutes</span>
        </h2>
        <p class="text-lg text-surface-400 max-w-2xl mx-auto">
          Get the full stack — backend, Redmine, and database — running with a single Docker Compose command.
        </p>
      </AnimatedSection>

      <AnimatedSection class="max-w-2xl mx-auto">
        <div class="glass-card overflow-hidden">
          <div class="flex items-center gap-2 px-5 py-3 bg-surface-900/80 border-b border-surface-800">
            <div class="w-3 h-3 rounded-full bg-red-500/60" />
            <div class="w-3 h-3 rounded-full bg-yellow-500/60" />
            <div class="w-3 h-3 rounded-full bg-green-500/60" />
            <span class="ml-2 text-xs text-surface-500 font-mono">terminal</span>
          </div>

          <div class="p-5 space-y-4">
            <div v-for="(step, i) in steps" :key="step.code" class="group flex items-start gap-4">
              <span class="text-xs text-surface-600 font-mono mt-1.5 select-none">{{ String(i + 1).padStart(2, '0') }}</span>
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <code class="text-sm font-mono text-sage-300 group-hover:text-sage-200 transition-colors">{{ step.code }}</code>
                  <button
                    @click="copyToClipboard(step.code)"
                    class="opacity-0 group-hover:opacity-100 transition-opacity text-surface-500 hover:text-copper-400"
                    title="Copy"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                      <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
                    </svg>
                  </button>
                </div>
                <span class="text-xs text-surface-600 mt-1 block">{{ step.label }}</span>
              </div>
            </div>
          </div>
        </div>
      </AnimatedSection>

      <AnimatedSection :delay="200" class="mt-16 grid sm:grid-cols-2 gap-6 max-w-3xl mx-auto">
        <div class="glass-card p-6 group hover:border-sage-500/25 transition-all">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-lg bg-sage-500/10 border border-sage-500/15 flex items-center justify-center">
              <Terminal :size="20" class="text-sage-400" />
            </div>
            <h4 class="font-bold text-white">CLI Mode</h4>
          </div>
          <p class="text-sm text-surface-400 leading-relaxed">
            Interactive terminal interface for direct usage. Type queries and get instant responses.
          </p>
        </div>
        <div class="glass-card p-6 group hover:border-copper-500/25 transition-all">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-lg bg-copper-500/10 border border-copper-500/15 flex items-center justify-center">
              <Zap :size="20" class="text-copper-400" />
            </div>
            <h4 class="font-bold text-white">REST API</h4>
          </div>
          <p class="text-sm text-surface-400 leading-relaxed">
            Full FastAPI backend with Swagger docs at <code class="text-copper-300">/docs</code>. Integrate with any tool.
          </p>
        </div>
      </AnimatedSection>
    </div>
  </section>
</template>
