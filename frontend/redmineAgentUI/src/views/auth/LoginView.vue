<script setup lang="ts">
import { ref } from "vue";
import { login } from "../../api/auth";

type PlatformRole = "admin" | "project_manager";

const emit = defineEmits<{
  (event: "login", payload: { token: string; role: PlatformRole }): void;
}>();

const email = ref("");
const password = ref("");
const isSubmitting = ref(false);
const error = ref("");

function decodeRoleFromToken(token: string): PlatformRole {
  const segments = token.split(".");
  if (segments.length < 2) {
    throw new Error("Invalid token format");
  }

  const payloadSegment = segments[1]
    .replace(/-/g, "+")
    .replace(/_/g, "/");

  const paddedPayload = payloadSegment.padEnd(payloadSegment.length + ((4 - (payloadSegment.length % 4)) % 4), "=");
  const decoded = JSON.parse(atob(paddedPayload)) as { role?: string };

  if (decoded.role !== "admin" && decoded.role !== "project_manager") {
    throw new Error("Unsupported role in token");
  }

  return decoded.role;
}

async function submitLogin() {
  error.value = "";

  if (!email.value.trim() || !password.value) {
    error.value = "Email and password are required.";
    return;
  }

  isSubmitting.value = true;
  try {
    const result = await login(email.value.trim(), password.value);
    const role = decodeRoleFromToken(result.access_token);
    emit("login", { token: result.access_token, role });
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Login failed";
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <main class="login-shell">
    <section class="login-card">
      <h1>RedSage Login</h1>
      <p class="subtitle">Use your platform credentials. You will be routed by your role.</p>

      <label class="field">
        <span>Email</span>
        <input v-model="email" type="email" autocomplete="username" placeholder="you@company.com" />
      </label>

      <label class="field">
        <span>Password</span>
        <input v-model="password" type="password" autocomplete="current-password" placeholder="••••••••" />
      </label>

      <p v-if="error" class="error">{{ error }}</p>

      <button class="primary-btn" type="button" :disabled="isSubmitting" @click="submitLogin">
        {{ isSubmitting ? "Signing in..." : "Sign in" }}
      </button>
    </section>
  </main>
</template>

<style scoped>
.login-shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: var(--bg-primary);
  padding: var(--space-lg);
}

.login-card {
  width: min(440px, 100%);
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: var(--space-xl);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: var(--text-2xl);
}

.subtitle {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
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
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border-radius: var(--radius-md);
  padding: 0.65rem 0.75rem;
}

.error {
  margin: 0;
  color: var(--accent-red);
  font-size: var(--text-sm);
}

.primary-btn {
  border: 1px solid var(--accent-blue);
  background: var(--accent-blue);
  color: var(--text-primary);
  border-radius: var(--radius-md);
  padding: 0.7rem 0.9rem;
  font-weight: 600;
  cursor: pointer;
}

.primary-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
