<script setup lang="ts">
const actions = [
  { id: 'summarize', icon: '📊', label: 'Summarize Issues', prompt: 'Can you summarize the current issues and their status?' },
  { id: 'approvals', icon: '✓', label: 'Show Approvals', prompt: 'What approvals are pending?' },
  { id: 'updates', icon: '🔄', label: 'Recent Updates', prompt: 'Show me recent updates and changes.' },
];

const emit = defineEmits<{
  (event: 'select', payload: { id: string; prompt: string }): void;
}>();

function handleClick(action: typeof actions[0]) {
  emit('select', { id: action.id, prompt: action.prompt });
}
</script>

<template>
  <div class="rds-quick-actions rds-animate-fade-in">
    <div class="rds-qa-title">Quick Actions</div>

    <div class="rds-qa-grid">
      <button
        v-for="action in actions"
        :key="action.id"
        class="rds-qa-btn rds-transition-fast"
        @click="handleClick(action)"
      >
        <div class="rds-qa-icon">{{ action.icon }}</div>
        <div class="rds-qa-label rds-text-12 rds-font-600">{{ action.label }}</div>
      </button>
    </div>
  </div>
</template>

<style scoped>
@import "../styles/index.css";

.rds-quick-actions {
  padding: var(--rds-space-4) var(--rds-space-3);
}

.rds-qa-title {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: rgba(0,0,0,0.45);
  margin-bottom: var(--rds-space-4);
  font-weight: 600;
}

.rds-qa-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: var(--rds-space-3);
}

.rds-qa-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--rds-space-2);
  padding: var(--rds-space-4) var(--rds-space-3);
  border: 2px solid #ff7a18;
  border-radius: 8px;
  background: rgba(255,122,24,0.06);
  cursor: pointer;
  transition: background-color var(--rds-duration-fast) ease, transform var(--rds-duration-fast) ease;
}

.rds-qa-btn:hover {
  background: rgba(255,122,24,0.15);
  transform: translateX(4px);
}

.rds-qa-btn:active {
  transform: translateX(2px);
}

.rds-qa-icon {
  font-size: 20px;
  line-height: 1;
}

.rds-qa-label {
  color: rgba(0,0,0,0.75);
  text-align: center;
  line-height: 1.3;
}

</style>
