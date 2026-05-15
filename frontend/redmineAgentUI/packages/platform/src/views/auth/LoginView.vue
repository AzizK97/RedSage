<script setup lang="ts">
import { ref } from "vue";
import { authApi } from "@redsage/api-client/auth";
import type { PlatformRole } from "@redsage/ui-core/composables/useSession";

const emit = defineEmits<{
  (event: "login", payload: { token: string; role: PlatformRole; fullName: string }): void;
  (event: "back"): void;
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
    const result = await authApi.login(email.value.trim(), password.value);
    const role = decodeRoleFromToken(result.access_token);
    emit("login", { token: result.access_token, role, fullName: result.full_name });
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Login failed";
  } finally {
    isSubmitting.value = false;
  }
}

</script>

<template>
  <main class="min-h-screen bg-surface-950 text-surface-200 flex items-center justify-center p-4">
    <section class="w-full max-w-md glass-card p-8 space-y-6">
      <div>
        <h1 class="text-3xl font-bold text-surface-100 mb-2">RedSage Login</h1>
        <p class="text-surface-400">Use your Redmine username/email and password. You will be routed by role.</p>
      </div>

      <form @submit.prevent="submitLogin" class="space-y-4">
        <label class="block space-y-2">
          <span class="text-sm font-medium text-surface-300">Email or username</span>
          <input
            v-model="email"
            type="text"
            autocomplete="username"
            placeholder="you@company.com or your Redmine login"
            class="w-full px-4 py-2 bg-surface-900/50 border border-surface-700 rounded-lg text-surface-100 placeholder-surface-500 focus:outline-none focus:border-sage-600 focus:ring-1 focus:ring-sage-600/30 transition-colors"
            @keydown.enter="submitLogin"
          />
        </label>

        <label class="block space-y-2">
          <span class="text-sm font-medium text-surface-300">Password</span>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="••••••••"
            class="w-full px-4 py-2 bg-surface-900/50 border border-surface-700 rounded-lg text-surface-100 placeholder-surface-500 focus:outline-none focus:border-sage-600 focus:ring-1 focus:ring-sage-600/30 transition-colors"
            @keydown.enter="submitLogin"
          />
        </label>

        <p v-if="error" class="p-3 bg-rose-950/30 border border-rose-700/50 rounded-lg text-rose-300 text-sm">{{ error }}</p>

        <button type="submit" :disabled="isSubmitting" class="w-full px-4 py-2.5 bg-sage-600 hover:bg-sage-700 disabled:bg-surface-700 disabled:cursor-not-allowed text-surface-50 font-semibold rounded-lg transition-colors">
          {{ isSubmitting ? "Signing in..." : "Sign in" }}
        </button>
        <button type="button" @click="emit('back')" class="w-full px-4 py-2.5 bg-surface-800/50 hover:bg-surface-800 text-surface-300 hover:text-surface-200 font-semibold rounded-lg transition-colors border border-surface-700">
          Back to landing
        </button>
      </form>
      <!-- <button class="secondary-btn" type="button" @click="signInWithRedmine">
        Sign in with Redmine
      </button> -->
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
