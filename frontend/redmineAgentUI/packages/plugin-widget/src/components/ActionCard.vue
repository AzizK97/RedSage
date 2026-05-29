<script setup lang="ts">
defineProps<{
  icon?: string;
  title: string;
  description: string;
  details?: { label: string; value: string }[];
}>();

const emit = defineEmits<{
  (event: 'reject'): void;
  (event: 'edit'): void;
  (event: 'approve'): void;
}>();
</script>

<template>
  <div class="rds-action-card">
    <div class="rds-ac-header">
      <div class="rds-ac-header-inner">
        <span v-if="icon" class="rds-ac-icon">{{ icon }}</span>
        <span class="rds-ac-label">REQUIRES APPROVAL</span>
      </div>
    </div>

    <div class="rds-ac-content">
      <h3 class="rds-ac-title rds-text-14 rds-font-600">{{ title }}</h3>
      <p class="rds-ac-desc">{{ description }}</p>

      <div v-if="details?.length" class="rds-ac-details">
        <div v-for="detail in details" :key="detail.label" class="rds-ac-detail-row">
          <span class="rds-ac-detail-label">{{ detail.label }}</span>
          <code class="rds-ac-detail-value">{{ detail.value }}</code>
        </div>
      </div>
    </div>

    <div class="rds-ac-actions">
      <button class="rds-ac-btn rds-ac-btn-reject rds-transition-fast" @click="$emit('reject')">
        Reject
      </button>
      <button class="rds-ac-btn rds-ac-btn-edit rds-transition-fast" @click="$emit('edit')">
        Edit
      </button>
      <button class="rds-ac-btn rds-ac-btn-approve rds-transition-fast" @click="$emit('approve')">
        Approve
      </button>
    </div>
  </div>
</template>

<style scoped>
@import "../styles/index.css";

.rds-action-card {
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(255,122,24,0.08), rgba(255,255,255,0));
  border: 1px solid rgba(255,122,24,0.2);
  border-left: 4px solid #ff7a18;
  overflow: hidden;
  transition: border-color var(--rds-duration-base) ease, box-shadow var(--rds-duration-base) ease;
}

.rds-action-card:hover {
  border-color: #ff7a18;
  box-shadow: var(--rds-shadow-sm);
}

.rds-ac-header {
  background: linear-gradient(135deg, #ff7a18, #ff944d);
  padding: var(--rds-space-3) var(--rds-space-4);
}

.rds-ac-header-inner {
  display: flex;
  align-items: center;
  gap: var(--rds-space-2);
}

.rds-ac-icon {
  font-size: 16px;
  line-height: 1;
}

.rds-ac-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  color: #fff;
  letter-spacing: 0.05em;
}

.rds-ac-content {
  padding: var(--rds-space-4);
}

.rds-ac-title {
  color: rgba(0,0,0,0.9);
  margin-bottom: var(--rds-space-2);
}

.rds-ac-desc {
  color: rgba(0,0,0,0.6);
  font-size: 13px;
  margin-bottom: var(--rds-space-3);
}

.rds-ac-details {
  background: rgba(0,0,0,0.02);
  border-radius: 6px;
  padding: var(--rds-space-3);
  margin-top: var(--rds-space-3);
}

.rds-ac-detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  margin-bottom: 6px;
}

.rds-ac-detail-row:last-child {
  margin-bottom: 0;
}

.rds-ac-detail-label {
  color: rgba(0,0,0,0.5);
  font-weight: 500;
}

.rds-ac-detail-value {
  font-family: 'Monaco', 'Courier New', monospace;
  color: rgba(0,0,0,0.7);
  font-size: 11px;
  background: rgba(0,0,0,0.03);
  padding: 2px 6px;
  border-radius: 3px;
}

.rds-ac-actions {
  display: flex;
  gap: var(--rds-space-2);
  padding: var(--rds-space-3) var(--rds-space-4);
  background: rgba(0,0,0,0.02);
  border-top: 1px solid rgba(0,0,0,0.06);
}

.rds-ac-btn {
  flex: 1;
  padding: var(--rds-space-2) var(--rds-space-3);
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  color: #fff;
}

.rds-ac-btn:hover {
  transform: scale(1.02);
}

.rds-ac-btn:active {
  transform: scale(0.98);
}

.rds-ac-btn-reject {
  background: linear-gradient(135deg, #ef4444, #f87171);
}

.rds-ac-btn-edit {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
}

.rds-ac-btn-approve {
  background: linear-gradient(135deg, #10b981, #34d399);
}
</style>
