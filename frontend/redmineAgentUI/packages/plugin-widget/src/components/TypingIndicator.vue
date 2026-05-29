<script setup lang="ts">
// Simple presentational typing indicator with three animated dots
// No props required; can be placed inside a message bubble
</script>

<template>
  <div class="rds-typing" aria-hidden="true">
    <span class="rds-typing-dot" style="animation-delay:0s"></span>
    <span class="rds-typing-dot" style="animation-delay:0.2s"></span>
    <span class="rds-typing-dot" style="animation-delay:0.4s"></span>
  </div>
</template>

<style scoped>
@import "../styles/index.css";

/* Provide a transition variable alias expected by consumers */
:root { --transition-base: var(--rds-duration-base); }

.rds-typing { display:flex; align-items:flex-end; gap: var(--rds-space-2); }

.rds-typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--rds-scrollbar-thumb, #ff7a18);
  display:inline-block;
  transform: translateY(0);
  animation: typing var(--transition-base, 1.2s) ease-in-out infinite;
}

/* Staggering is provided via inline style animation-delay on each dot */

/* Local typing keyframes that animate dots up/down (staggered by delay)
   This intentionally matches the 'typing' keyframe name from the design system
   but animates translateY for dot motion.
*/
@keyframes typing {
  0% { transform: translateY(0); opacity: 0.6; }
  50% { transform: translateY(-6px); opacity: 1; }
  100% { transform: translateY(0); opacity: 0.6; }
}

</style>
