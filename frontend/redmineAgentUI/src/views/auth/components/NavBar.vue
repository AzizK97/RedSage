<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { Leaf, LogIn, Menu, X } from 'lucide-vue-next';

const emit = defineEmits<{ (e: 'start-login'): void }>();

const scrolled = ref(false);
const mobileOpen = ref(false);

function onScroll() {
  scrolled.value = window.scrollY > 40;
}

onMounted(() => window.addEventListener('scroll', onScroll));
onUnmounted(() => window.removeEventListener('scroll', onScroll));

const links = [
  { label: 'Agents', href: '#agents' },
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'Safety', href: '#safety' },
  { label: 'Tech Stack', href: '#tech-stack' },
  { label: 'Get Started', href: '#get-started' },
];
</script>

<template>
  <nav :class="['fixed top-0 left-0 right-0 z-50 transition-all duration-300', scrolled ? 'bg-surface-950/80 backdrop-blur-xl border-b border-sage-700/15 shadow-lg shadow-sage-900/10' : 'bg-transparent']">
    <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
      <a href="#" class="flex items-center gap-2.5 group">
        <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-sage-400 to-copper-500 flex items-center justify-center shadow-lg shadow-sage-700/30 group-hover:shadow-copper-600/30 transition-shadow">
          <Leaf :size="18" class="text-white" />
        </div>
        <span class="font-bold text-lg text-white tracking-tight">Red<span class="gradient-text-copper">Sage</span></span>
      </a>

      <div class="hidden md:flex items-center gap-8">
        <a v-for="l in links" :key="l.href" :href="l.href" class="text-sm text-surface-400 hover:text-sage-300 transition-colors duration-200">{{ l.label }}</a>
      </div>

      <div class="hidden md:flex items-center gap-3">
        <button @click="emit('start-login')"
          class="flex items-center gap-2 text-sm text-surface-300 hover:text-white transition-colors px-3 py-1.5 rounded-lg hover:bg-surface-800/50">
          <LogIn :size="15" />
          Sign In
        </button>
        <a href="#get-started"
          class="text-sm font-medium px-4 py-2 rounded-lg bg-copper-600 text-white hover:bg-copper-500 transition-colors shadow-lg shadow-copper-700/25">
          Get Started
        </a>
      </div>

      <button @click="mobileOpen = !mobileOpen" class="md:hidden text-surface-300 hover:text-white">
        <X v-if="mobileOpen" :size="24" />
        <Menu v-else :size="24" />
      </button>
    </div>

    <div v-if="mobileOpen" class="md:hidden bg-surface-950/95 backdrop-blur-xl border-t border-surface-800 px-6 py-4 space-y-3">
      <a v-for="l in links" :key="l.href" :href="l.href" @click="mobileOpen = false"
        class="block text-sm text-surface-400 hover:text-sage-300 py-2">{{ l.label }}</a>
      <button @click="emit('start-login'); mobileOpen = false"
        class="flex items-center gap-2 text-sm text-surface-300 hover:text-sage-300 py-2">
        <LogIn :size="16" /> Sign In
      </button>
    </div>
  </nav>
</template>
