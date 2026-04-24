<script setup lang="ts">
import { ref } from "vue";
import ChatInterface from "./components/ChatInterface.vue";
import LoginView from "./views/auth/LoginView.vue";
import DashboardView from "./views/dashboard/DashboardView.vue";
import { useSession, type PlatformRole } from "./composables/useSession";

const { token, role, userId, isAuthenticated, setSession, clearSession } = useSession();
const currentView = ref<"dashboard" | "chat">("dashboard");

function handleLogin(payload: { token: string; role: PlatformRole }) {
  setSession(payload.token, payload.role);
  currentView.value = "dashboard";
}

function handleLogout() {
  clearSession();
  currentView.value = "dashboard";
}

function navLabel(view: "dashboard" | "chat") {
  if (view === "dashboard") return "Dashboard";
  return "Chatbot";
}
</script>

<template>
  <main v-if="!isAuthenticated" class="app-shell">
    <LoginView @login="handleLogin" />
  </main>
  <main v-else class="app-shell">
    <section class="top-nav">
      <button
        class="nav-btn"
        :class="{ active: currentView === 'dashboard' }"
        type="button"
        @click="currentView = 'dashboard'"
      >
        {{ navLabel("dashboard") }}
      </button>
      <button
        class="nav-btn"
        :class="{ active: currentView === 'chat' }"
        type="button"
        @click="currentView = 'chat'"
      >
        {{ navLabel("chat") }}
      </button>
    </section>

    <DashboardView
      v-if="currentView === 'dashboard'"
      :role="role === 'admin' ? 'admin' : 'project_manager'"
      :token="token"
    />

    <ChatInterface
      v-else
      :key="userId"
      :token="token"
      :user-id="userId"
      :role="role === 'admin' ? 'admin' : 'project_manager'"
      @logout="handleLogout"
    />
  </main>
</template>

<style scoped>
.app-shell {
  height: 100vh;
  box-sizing: border-box;
}

.top-nav {
  display: flex;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-primary);
}

.nav-btn {
  border: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: var(--radius-md);
  padding: 0.45rem 0.7rem;
  cursor: pointer;
}

.nav-btn.active {
  border-color: var(--accent-blue);
  color: var(--accent-blue);
}
</style>