<script setup lang="ts">
const props = defineProps<{
  role: "admin" | "project_manager";
  userId: string;
}>();

const roleLabel = props.role === "admin" ? "Administrator" : "Project Manager";
</script>

<template>
  <main class="profile-shell">
    <section class="profile-card">
      <h1>Profile</h1>
      <p class="subtitle">Your account details and access level.</p>

      <div class="field-list">
        <article class="field-row">
          <span class="label">Role</span>
          <strong>{{ roleLabel }}</strong>
        </article>
        <article class="field-row">
          <span class="label">User ID</span>
          <strong>{{ userId || "Unknown" }}</strong>
        </article>
      </div>
    </section>
  </main>
</template>

<style scoped>
.profile-shell {
  min-height: 100%;
  padding: var(--space-xl);
  background: var(--bg-primary);
}

.profile-card {
  max-width: 760px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
}

h1 {
  margin: 0;
  color: var(--text-primary);
}

.subtitle {
  margin: var(--space-xs) 0 var(--space-lg);
  color: var(--text-secondary);
}

.field-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.field-row {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  background: var(--bg-tertiary);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

strong {
  color: var(--text-primary);
  font-size: var(--text-sm);
}
</style>
