<script setup lang="ts">
import { Cpu, Zap, Bot, Container, Database, GitBranch, Terminal, Activity } from 'lucide-vue-next';
import AnimatedSection from './AnimatedSection.vue';

const techItems = [
  { icon: Cpu, name: 'LangChain + LangGraph', desc: 'Agent orchestration & routing' },
  { icon: Zap, name: 'FastAPI', desc: 'High-performance REST API' },
  { icon: Bot, name: 'OpenRouter', desc: 'LLM provider (OpenAI-compatible)' },
  { icon: Container, name: 'Docker Compose', desc: 'One-command deployment' },
  { icon: Database, name: 'MySQL', desc: 'Redmine database backend' },
  { icon: GitBranch, name: 'K3s', desc: 'Kubernetes deployment ready' },
  { icon: Terminal, name: 'CLI + API', desc: 'Dual interface modes' },
  { icon: Activity, name: 'Benchmarking', desc: 'Built-in validation framework' },
];
</script>

<template>
  <section id="tech-stack" class="relative py-32">
    <div class="absolute inset-0">
      <div class="absolute top-0 left-0 right-0 section-divider" />
    </div>

    <div class="max-w-7xl mx-auto px-6">
      <AnimatedSection class="text-center mb-16">
        <span class="inline-block text-xs font-semibold uppercase tracking-widest text-sage-400 mb-4">Under the Hood</span>
        <h2 class="text-4xl sm:text-5xl font-extrabold tracking-tight mb-6">
          Built with <span class="gradient-text">Modern Stack</span>
        </h2>
        <p class="text-lg text-surface-400 max-w-2xl mx-auto">
          Production-grade technologies chosen for reliability, performance, and developer experience.
        </p>
      </AnimatedSection>

      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <AnimatedSection v-for="(item, i) in techItems" :key="item.name" :delay="i * 80">
          <div class="group glass-card p-5 hover:border-sage-500/25 transition-all duration-300 hover:-translate-y-0.5">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-9 h-9 rounded-lg bg-sage-500/10 border border-sage-500/15 flex items-center justify-center group-hover:bg-sage-500/15 group-hover:border-sage-500/25 transition-colors">
                <component :is="item.icon" :size="18" class="text-sage-400" />
              </div>
              <h4 class="text-sm font-bold text-white">{{ item.name }}</h4>
            </div>
            <p class="text-xs text-surface-500 leading-relaxed">{{ item.desc }}</p>
          </div>
        </AnimatedSection>
      </div>
    </div>
  </section>
</template>
