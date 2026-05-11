<script setup lang="ts">
import { Cpu, Zap, Bot, Container, Database, GitBranch, Terminal, Activity } from 'lucide-vue-next';
import AnimatedSection from './AnimatedSection.vue';
import { computed } from 'vue';
import { useTheme } from '../../../composables/useTheme';

const { isDark } = useTheme();

const descriptionTextClass = computed(() =>
  isDark.value
    ? 'text-surface-400'
    : 'text-surface-600'
);

const cardBg = computed(() =>
  isDark.value
    ? 'bg-sage-500/10'
    : 'bg-sage-200/20'
);

const cardBgHover = computed(() =>
  isDark.value
    ? 'group-hover:bg-sage-500/15'
    : 'group-hover:bg-sage-200/30'
);

const cardBorder = computed(() =>
  isDark.value
    ? 'border-sage-500/15'
    : 'border-sage-300/30'
);

const cardBorderHover = computed(() =>
  isDark.value
    ? 'group-hover:border-sage-500/25'
    : 'group-hover:border-sage-400/40'
);

const itemNameClass = computed(() =>
  isDark.value
    ? 'text-white'
    : 'text-sage-900'
);

const itemDescClass = computed(() =>
  isDark.value
    ? 'text-surface-500'
    : 'text-surface-700'
);

const glassCardBorder = computed(() =>
  isDark.value
    ? 'border-surface-800'
    : 'border-sage-200/30'
);

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
        <p :class="['text-lg max-w-2xl mx-auto', descriptionTextClass]">
          Production-grade technologies chosen for reliability, performance, and developer experience.
        </p>
      </AnimatedSection>

      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <AnimatedSection v-for="(item, i) in techItems" :key="item.name" :delay="i * 80">
          <div :class="['group glass-card p-5 transition-all duration-300 hover:-translate-y-0.5 border', glassCardBorder, isDark ? 'hover:border-sage-500/25' : 'hover:border-sage-400/40']">
            <div class="flex items-center gap-3 mb-3">
              <div :class="['w-9 h-9 rounded-lg border flex items-center justify-center transition-colors', cardBg, cardBorder, cardBgHover, cardBorderHover]">
                <component :is="item.icon" :size="18" class="text-sage-400" />
              </div>
              <h4 :class="['text-sm font-bold', itemNameClass]">{{ item.name }}</h4>
            </div>
            <p :class="['text-xs leading-relaxed', itemDescClass]">{{ item.desc }}</p>
          </div>
        </AnimatedSection>
      </div>
    </div>
  </section>
</template>
