<script setup lang="ts">
import { computed, ref } from "vue";
import AdminDashboard from "./views/admin/AdminDashboard.vue";
import ChatInterface from "./components/ChatInterface.vue";
import LoginView from "./views/auth/LoginView.vue";

type PlatformRole = "admin" | "project_manager";

const authToken = ref(localStorage.getItem("redsage.authToken") ?? "");
const role = ref<PlatformRole | null>((localStorage.getItem("redsage.role") as PlatformRole | null) ?? null);
const adminView = ref<"dashboard" | "chat">(
  (localStorage.getItem("redsage.adminView") as "dashboard" | "chat" | null) ?? "dashboard",
);

function decodeJwtPayload(token: string): { sub?: string; redmine_user_id?: number } | null {
  try {
    const payloadPart = token.split(".")[1];
    if (!payloadPart) return null;

    const base64 = payloadPart.replace(/-/g, "+").replace(/_/g, "/");
    const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), "=");
    return JSON.parse(atob(padded)) as { sub?: string; redmine_user_id?: number };
  } catch {
    return null;
  }
}

const isAuthenticated = computed(() => authToken.value.trim() !== "" && role.value !== null);
const sessionScope = computed(() => {
  const payload = authToken.value ? decodeJwtPayload(authToken.value) : null;
  return payload?.sub ? `user-${payload.sub}` : payload?.redmine_user_id ? `redmine-${payload.redmine_user_id}` : "anonymous";
});

function onLogin(payload: { token: string; role: PlatformRole }) {
  authToken.value = payload.token;
  role.value = payload.role;
  localStorage.setItem("redsage.authToken", payload.token);
  localStorage.setItem("redsage.role", payload.role);
}

function onLogout() {
  authToken.value = "";
  role.value = null;
  adminView.value = "dashboard";
  localStorage.removeItem("redsage.authToken");
  localStorage.removeItem("redsage.role");
  localStorage.removeItem("redsage.adminView");
}

function setAdminView(view: "dashboard" | "chat") {
  adminView.value = view;
  localStorage.setItem("redsage.adminView", view);
}
</script>

<template>
  <LoginView v-if="!isAuthenticated" @login="onLogin" />
  <template v-else-if="role === 'admin'">
    <div class="admin-switch">
      <button
        type="button"
        :class="['switch-btn', { active: adminView === 'dashboard' }]"
        @click="setAdminView('dashboard')"
      >
        Admin Panel
      </button>
      <button
        type="button"
        :class="['switch-btn', { active: adminView === 'chat' }]"
        @click="setAdminView('chat')"
      >
        Chatbot
      </button>
    </div>

    <AdminDashboard
      v-if="adminView === 'dashboard'"
      :token="authToken"
      @logout="onLogout"
    />
    <ChatInterface
      v-else
      :token="authToken"
        :storage-scope="sessionScope"
      role="admin"
      @logout="onLogout"
    />
  </template>
  <ChatInterface
    v-else
    :token="authToken"
      :storage-scope="sessionScope"
    :role="role ?? 'project_manager'"
    @logout="onLogout"
  />
</template>

<style scoped>
.admin-switch {
  position: fixed;
  top: 0.8rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 20;
  display: flex;
  gap: 0.4rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 0.3rem;
}

.switch-btn {
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-secondary);
  border-radius: var(--radius-md);
  padding: 0.35rem 0.7rem;
  font-size: var(--text-sm);
  cursor: pointer;
}

.switch-btn.active {
  border-color: var(--accent-blue);
  color: var(--text-primary);
  background: rgba(59, 130, 246, 0.18);
}
</style>