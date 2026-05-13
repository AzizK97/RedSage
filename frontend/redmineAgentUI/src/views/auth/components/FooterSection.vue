<script setup lang="ts">
import { Leaf } from 'lucide-vue-next';
import { computed } from 'vue';
import { useTheme } from '../../../composables/useTheme';

const { isDark } = useTheme();

const borderClass = computed(() =>
  isDark.value
    ? 'border-surface-800'
    : 'border-sage-200/40'
);

const brandTextClass = computed(() =>
  isDark.value
    ? 'text-white'
    : 'text-sage-900'
);

const productLinks = [
  { label: 'Features', href: '#features' },
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'Safety', href: '#safety' },
  { label: 'Pricing', href: '#pricing' },
];

const companyLinks = [
  { label: 'About', href: '#' },
  { label: 'Blog', href: '#' },
  { label: 'Careers', href: '#' },
  { label: 'Contact', href: '#' },
];

const legalLinks = [
  { label: 'Privacy', href: '#' },
  { label: 'Terms', href: '#' },
  { label: 'Security', href: '#' },
];
</script>

<template>
  <footer :class="['border-t py-12', borderClass]">
    <div class="max-w-7xl mx-auto px-6">
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-10 mb-12">
        
        <div class="space-y-4">
          <div class="flex items-center gap-2.5">
            <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-sage-400 to-copper-500 flex items-center justify-center">
              <Leaf :size="14" class="text-white" />
            </div>
            <span :class="['font-bold', brandTextClass]">Red<span class="gradient-text-copper">Sage</span></span>
          </div>
          <p class="text-sm text-surface-500 dark:text-surface-500 leading-relaxed">
            AI-powered project management for Redmine. Manage your projects through natural language.
          </p>
        </div>

        <div>
          <h4 class="text-sm font-semibold text-sage-900 dark:text-white mb-4">Product</h4>
          <ul class="space-y-2.5">
            <li v-for="link in productLinks" :key="link.label">
              <a :href="link.href" class="text-sm text-surface-500 dark:text-surface-500 hover:text-sage-700 dark:hover:text-sage-300 transition-colors">{{ link.label }}</a>
            </li>
          </ul>
        </div>
        
        <div>
          <h4 class="text-sm font-semibold text-sage-900 dark:text-white mb-4">Company</h4>
          <ul class="space-y-2.5">
            <li v-for="link in companyLinks" :key="link.label">
              <a :href="link.href" class="text-sm text-surface-500 dark:text-surface-500 hover:text-sage-700 dark:hover:text-sage-300 transition-colors">{{ link.label }}</a>
            </li>
          </ul>
        </div>

        <div>
          <h4 class="text-sm font-semibold text-sage-900 dark:text-white mb-4">Legal</h4>
          <ul class="space-y-2.5">
            <li v-for="link in legalLinks" :key="link.label">
              <a :href="link.href" class="text-sm text-surface-500 dark:text-surface-500 hover:text-sage-700 dark:hover:text-sage-300 transition-colors">{{ link.label }}</a>
            </li>
          </ul>
        </div>
      </div>

      <div class="pt-8 border-t border-sage-100 dark:border-surface-800 flex flex-col sm:flex-row items-center justify-between gap-4">
        <p class="text-xs text-surface-400 dark:text-surface-600">&copy; 2026 RedSage. All rights reserved.</p>
        <p class="text-xs text-surface-400 dark:text-surface-600">Powered by LangGraph, FastAPI, and Docker</p>
      </div>

    </div>
  </footer>
</template>
