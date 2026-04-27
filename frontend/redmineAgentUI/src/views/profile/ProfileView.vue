<script setup lang="ts">
import { computed, ref } from "vue";

const props = defineProps<{
  role: "admin" | "project_manager";
  userId: string;
  fullName: string;
  email: string;
}>();

const passwordForm = ref({
  currentPassword: "",
  newPassword: "",
  confirmPassword: "",
});

const statusMessage = ref("");
const statusType = ref<"success" | "error" | "">("");
const isSaving = ref(false);

const roleLabel = computed(() => (props.role === "admin" ? "Administrator" : "Project Manager"));
const initials = computed(() => {
  const source = props.fullName.trim() || props.email.trim() || "U";
  return source
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("")
    .slice(0, 2) || "U";
});

function resetStatus() {
  statusMessage.value = "";
  statusType.value = "";
}

async function savePassword() {
  resetStatus();

  if (!passwordForm.value.currentPassword || !passwordForm.value.newPassword || !passwordForm.value.confirmPassword) {
    statusType.value = "error";
    statusMessage.value = "Please fill in all password fields.";
    return;
  }

  if (passwordForm.value.newPassword.length < 8) {
    statusType.value = "error";
    statusMessage.value = "New password must be at least 8 characters.";
    return;
  }

  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    statusType.value = "error";
    statusMessage.value = "New password and confirmation do not match.";
    return;
  }

  isSaving.value = true;
  try {
    // UI placeholder: wire this to a backend password-change endpoint later.
    await new Promise((resolve) => setTimeout(resolve, 600));
    statusType.value = "success";
    statusMessage.value = "Password updated successfully.";
    passwordForm.value.currentPassword = "";
    passwordForm.value.newPassword = "";
    passwordForm.value.confirmPassword = "";
  } catch {
    statusType.value = "error";
    statusMessage.value = "Unable to update password right now.";
  } finally {
    isSaving.value = false;
  }
}
</script>

<template>
  <main class="profile-shell">
    <section class="profile-card">
      <div class="profile-header">
        <div class="avatar" aria-hidden="true">{{ initials }}</div>
        <div class="heading-copy">
          <p class="kicker">Profile</p>
          <h1>{{ fullName || "Unknown user" }}</h1>
          <p class="subtitle">Manage your account information and password settings.</p>
        </div>
      </div>

      <section class="info-grid">
        <article class="info-card">
          <span class="info-label">Full name</span>
          <strong>{{ fullName || "Unknown" }}</strong>
        </article>
        <article class="info-card">
          <span class="info-label">Email</span>
          <strong>{{ email || "Unknown" }}</strong>
        </article>
        <article class="info-card">
          <span class="info-label">Role</span>
          <strong>{{ roleLabel }}</strong>
        </article>
        <article class="info-card">
          <span class="info-label">User ID</span>
          <strong>{{ userId || "Unknown" }}</strong>
        </article>
      </section>

      <section class="password-section">
        <div class="section-head">
          <div>
            <h2>Change password</h2>
            <p>Update your password using your current credentials.</p>
          </div>
        </div>

        <div class="password-grid">
          <label class="field">
            <span>Current password</span>
            <input v-model="passwordForm.currentPassword" type="password" placeholder="Enter current password" />
          </label>
          <label class="field">
            <span>New password</span>
            <input v-model="passwordForm.newPassword" type="password" placeholder="Enter new password" />
          </label>
          <label class="field">
            <span>Confirm new password</span>
            <input v-model="passwordForm.confirmPassword" type="password" placeholder="Repeat new password" />
          </label>
        </div>

        <p v-if="statusMessage" class="status" :class="statusType">{{ statusMessage }}</p>

        <div class="actions">
          <button class="primary-btn" type="button" :disabled="isSaving" @click="savePassword">
            {{ isSaving ? "Saving..." : "Update password" }}
          </button>
        </div>
      </section>
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
  max-width: 980px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
  border-radius: var(--radius-xl);
  padding: var(--space-xl);
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
}

.avatar {
  width: 88px;
  height: 88px;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.18), rgba(255, 255, 255, 0.05));
  color: var(--text-primary);
  display: grid;
  place-items: center;
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  flex-shrink: 0;
}

.heading-copy h1 {
  margin: var(--space-xs) 0;
  color: var(--text-primary);
  font-size: clamp(1.5rem, 2.2vw, 2rem);
}

.kicker {
  margin: 0;
  color: var(--accent-blue);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: var(--text-xs);
  font-weight: 600;
}

.subtitle {
  margin: 0;
  color: var(--text-secondary);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-md);
}

.info-card {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  background: var(--bg-tertiary);
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.info-label {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.info-card strong {
  color: var(--text-primary);
  font-size: var(--text-base);
}

.password-section {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-primary);
  padding: var(--space-lg);
}

.section-head h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: var(--text-lg);
}

.section-head p {
  margin: var(--space-xs) 0 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.password-grid {
  margin-top: var(--space-lg);
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-md);
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.field span {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.field input {
  border: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: var(--radius-md);
  padding: 0.7rem 0.8rem;
}

.field input:focus {
  outline: none;
  border-color: var(--accent-blue);
}

.status {
  margin: var(--space-md) 0 0;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
}

.status.success {
  color: var(--accent-green);
  border: 1px solid rgba(16, 185, 129, 0.3);
  background: rgba(16, 185, 129, 0.08);
}

.status.error {
  color: var(--accent-red);
  border: 1px solid rgba(239, 68, 68, 0.3);
  background: rgba(239, 68, 68, 0.08);
}

.actions {
  margin-top: var(--space-lg);
  display: flex;
  justify-content: flex-end;
}

.primary-btn {
  border: 1px solid var(--accent-blue);
  background: var(--accent-blue);
  color: white;
  border-radius: var(--radius-md);
  padding: 0.75rem 1rem;
  font-weight: 600;
  cursor: pointer;
}

.primary-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@media (max-width: 900px) {
  .info-grid,
  .password-grid {
    grid-template-columns: 1fr;
  }

  .profile-header {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
