<script setup lang="ts">
import { Leaf, Github, ExternalLink } from 'lucide-vue-next';
</script>

<template>
  <footer class="border-t border-surface-800 py-12">
    <div class="max-w-7xl mx-auto px-6">
      <div class="flex flex-col sm:flex-row items-center justify-between gap-6">
        <div class="flex items-center gap-2.5">
          <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-sage-400 to-copper-500 flex items-center justify-center">
            <Leaf :size="14" class="text-white" />
          </div>
          <span class="font-bold text-white">Red<span class="gradient-text-copper">Sage</span></span>
        </div>

        <div class="flex items-center gap-6 text-sm text-surface-500">
          <a href="https://github.com/AzizK97/Redmine-Agent" target="_blank" rel="noopener noreferrer"
            class="hover:text-sage-400 transition-colors flex items-center gap-1.5">
            <Github :size="16" /> Repository
          </a>
          <a href="https://github.com/AzizK97/Redmine-Agent/issues" target="_blank" rel="noopener noreferrer"
            class="hover:text-copper-400 transition-colors flex items-center gap-1.5">
            <ExternalLink :size="14" /> Issues
          </a>
        </div>

        <p class="text-xs text-surface-600">Built with LangGraph, FastAPI, and Docker</p>
      </div>
    </div>
  </footer>
</template>
