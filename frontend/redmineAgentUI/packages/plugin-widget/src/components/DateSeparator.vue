<script setup lang="ts">
defineProps<{
  label?: string;
}>();
</script>

<template>
  <div class="rds-date-separator">
    <div class="rds-ds-line rds-ds-line-left"></div>
    <div class="rds-ds-label">{{ label || 'TODAY' }}</div>
    <div class="rds-ds-line rds-ds-line-right"></div>
  </div>
</template>

<style scoped>
@import "../styles/index.css";

.rds-date-separator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--rds-space-4);
  margin: 16px 0;
}

.rds-ds-line {
  flex: 1;
  height: 1px;
}

.rds-ds-line-left {
  background: linear-gradient(to right, transparent, #ff7a18, #ff944d);
}

.rds-ds-line-right {
  background: linear-gradient(to left, transparent, #ff7a18, #ff944d);
}

.rds-ds-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  color: rgba(0,0,0,0.45);
  letter-spacing: 0.5px;
  white-space: nowrap;
}

</style>
