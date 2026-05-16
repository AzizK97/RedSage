<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { Leaf, Menu, X, Sun, Moon } from 'lucide-vue-next';
import { useTheme } from '@redsage/ui-core/composables/useTheme';

const { isDark, toggleTheme } = useTheme();
const scrolled = ref(false);
const mobileOpen = ref(false);

function onScroll() {
  scrolled.value = window.scrollY > 40;
}

onMounted(() => window.addEventListener('scroll', onScroll));
onUnmounted(() => window.removeEventListener('scroll', onScroll));

const links = [
  { label: 'Features', href: '#features' },
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'Safety', href: '#safety' },
  { label: 'Pricing', href: '#pricing' },
];

const emit = defineEmits<{
  (e: 'start-login'): void;
  (e: 'start-onboarding'): void;
}>();
</script>

<template>
  <nav :class="['fixed top-0 left-0 right-0 z-50 transition-all duration-300', scrolled ? 'bg-white/80 dark:bg-surface-950/80 backdrop-blur-xl border-b border-sage-200/60 dark:border-sage-700/15 shadow-sm dark:shadow-lg dark:shadow-sage-900/10' : 'bg-transparent']">
    <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
      <a href="#" class="flex items-center gap-2.5 group">
        <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-sage-400 to-copper-500 flex items-center justify-center shadow-md shadow-sage-300/30 dark:shadow-sage-700/30 group-hover:shadow-copper-400/30 dark:group-hover:shadow-copper-600/30 transition-shadow">
          <Leaf :size="18" class="text-white" />
        </div>
        <span class="font-bold text-lg text-sage-900 dark:text-white tracking-tight">Red<span class="gradient-text-copper">Sage</span></span>
      </a>

      <div class="hidden md:flex items-center gap-8">
        <a v-for="l in links" :key="l.href" :href="l.href" class="text-sm text-surface-500 dark:text-surface-400 hover:text-sage-700 dark:hover:text-sage-300 transition-colors duration-200">{{ l.label }}</a>
      </div>

      <div class="hidden md:flex items-center gap-3">
        <button @click="toggleTheme" class="p-2 rounded-lg text-surface-500 dark:text-surface-400 hover:bg-sage-50 dark:hover:bg-surface-800/50 transition-colors" :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'">
          <Sun v-if="isDark" :size="18" />
          <Moon v-else :size="18" />
        </button>
        <button @click="emit('start-login')"
          class="text-sm font-medium px-4 py-2 rounded-lg text-sage-700 dark:text-surface-300 hover:bg-sage-50 dark:hover:bg-surface-800/50 transition-colors">
          Sign In
        </button>
        <button
          @click="emit('start-onboarding')"
          class="text-sm font-medium px-4 py-2 rounded-lg bg-copper-600 text-white hover:bg-copper-500 transition-colors shadow-md shadow-copper-300/30 dark:shadow-copper-700/25">
          Start Free Trial
        </button>
      </div>

      <div class="flex md:hidden items-center gap-2">
        <button @click="toggleTheme" class="p-2 rounded-lg text-surface-500 dark:text-surface-400 hover:bg-sage-50 dark:hover:bg-surface-800/50 transition-colors">
          <Sun v-if="isDark" :size="18" />
          <Moon v-else :size="18" />
        </button>
        <button @click="mobileOpen = !mobileOpen" class="text-surface-600 dark:text-surface-300 hover:text-sage-800 dark:hover:text-white">
          <X v-if="mobileOpen" :size="24" />
          <Menu v-else :size="24" />
        </button>
      </div>
    </div>

    <div v-if="mobileOpen" class="md:hidden bg-white/95 dark:bg-surface-950/95 backdrop-blur-xl border-t border-sage-100 dark:border-surface-800 px-6 py-4 space-y-3">
      <a v-for="l in links" :key="l.href" :href="l.href" @click="mobileOpen = false"
        class="block text-sm text-surface-600 dark:text-surface-400 hover:text-sage-700 dark:hover:text-sage-300 py-2">{{ l.label }}</a>
      <button
        @click="mobileOpen = false; emit('start-onboarding')"
        class="block text-sm font-medium text-copper-600 dark:text-copper-400 py-2"
      >
        Start Free Trial
      </button>
    </div>
  </nav>
</template>
