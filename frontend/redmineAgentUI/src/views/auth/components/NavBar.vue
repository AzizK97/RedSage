<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { LampCeiling, LogIn, Menu, X, Sun, Moon } from 'lucide-vue-next';
import { useTheme } from '../../../composables/useTheme';

const emit = defineEmits<{ (e: 'start-login'): void }>();

const scrolled = ref(false);
const mobileOpen = ref(false);
const { isDark, toggleTheme } = useTheme();

const bgClass = computed(() => 
  scrolled.value 
    ? isDark.value 
      ? 'bg-surface-950/80 backdrop-blur-xl border-b border-sage-700/15 shadow-lg shadow-sage-900/10'
      : 'bg-white/80 backdrop-blur-xl border-b border-sage-200/60 shadow-sm'
    : 'bg-transparent'
);

const textClass = computed(() => isDark.value ? 'text-white' : 'text-sage-900');
const linkClass = computed(() => isDark.value ? 'text-surface-400 hover:text-sage-300' : 'text-surface-600 hover:text-sage-700');
const buttonBgClass = computed(() => isDark.value ? 'hover:bg-surface-800/50' : 'hover:bg-sage-50');

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
  <nav :class="['fixed top-0 left-0 right-0 z-50 transition-all duration-300', bgClass]">
    <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
      <a href="#" class="flex items-center gap-2.5 group">
        <div :class="['w-8 h-8 rounded-lg bg-gradient-to-br from-sage-400 to-copper-500 flex items-center justify-center shadow-lg transition-shadow', isDark ? 'shadow-sage-700/30 group-hover:shadow-copper-600/30' : 'shadow-sage-300/30 group-hover:shadow-copper-400/30']">
          <LampCeiling :size="18" class="text-white" />
        </div>
        <span :class="['font-bold text-lg tracking-tight', textClass]">Red<span class="gradient-text-copper">Sage</span></span>
      </a>

      <div class="hidden md:flex items-center gap-8">
        <a v-for="l in links" :key="l.href" :href="l.href" :class="['text-sm transition-colors duration-200', linkClass]">{{ l.label }}</a>
      </div>

      <div class="hidden md:flex items-center gap-3">
        <button 
          @click="toggleTheme"
          :class="['flex items-center justify-center w-10 h-10 rounded-lg transition-all', isDark ? 'text-surface-400 hover:text-white hover:bg-surface-800/50' : 'text-surface-600 hover:text-sage-800 hover:bg-sage-50']"
          :title="isDark ? 'Switch to light theme' : 'Switch to dark theme'"
        >
          <Sun v-if="isDark" :size="18" />
          <Moon v-else :size="18" />
        </button>
        <button @click="emit('start-login')"
          :class="['flex items-center gap-2 text-sm transition-colors px-3 py-1.5 rounded-lg', isDark ? 'text-surface-300 hover:text-white' : 'text-surface-700 hover:text-sage-900', buttonBgClass]">
          <LogIn :size="15" />
          Sign In
        </button>
        <a href="#get-started"
          :class="['text-sm font-medium px-4 py-2 rounded-lg text-white transition-colors shadow-lg', isDark ? 'bg-copper-600 hover:bg-copper-500 shadow-copper-700/25' : 'bg-copper-600 hover:bg-copper-500 shadow-copper-700/25']">
          Get Started
        </a>
      </div>

      <button @click="mobileOpen = !mobileOpen" :class="['md:hidden', isDark ? 'text-surface-300 hover:text-white' : 'text-surface-600 hover:text-sage-900']">
        <X v-if="mobileOpen" :size="24" />
        <Menu v-else :size="24" />
      </button>
    </div>

    <div v-if="mobileOpen" :class="['md:hidden backdrop-blur-xl px-6 py-4 space-y-3 border-t transition-colors', isDark ? 'bg-surface-950/95 border-surface-800' : 'bg-white/95 border-sage-200/60']">
      <a v-for="l in links" :key="l.href" :href="l.href" @click="mobileOpen = false"
        :class="['block text-sm py-2 transition-colors', linkClass]">{{ l.label }}</a>
      <button @click="toggleTheme(); mobileOpen = false"
        :class="['flex items-center gap-2 text-sm py-2 w-full transition-colors', isDark ? 'text-surface-400 hover:text-sage-300' : 'text-surface-600 hover:text-sage-700']">
        <Sun v-if="isDark" :size="16" />
        <Moon v-else :size="16" />
        {{ isDark ? 'Light Theme' : 'Dark Theme' }}
      </button>
      <button @click="emit('start-login'); mobileOpen = false"
        :class="['flex items-center gap-2 text-sm py-2 transition-colors', linkClass]">
        <LogIn :size="16" /> Sign In
      </button>
    </div>
  </nav>
</template>
