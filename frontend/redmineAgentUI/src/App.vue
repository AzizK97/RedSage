<script setup lang="ts">
import { ref } from "vue";
import AppSidebar from "./components/AppSidebar.vue";
import AppTopBar from "./components/AppTopBar.vue";
import ChatInterface from "./components/ChatInterface.vue";
import LoginView from "./views/auth/LoginView.vue";
import DashboardView from "./views/dashboard/DashboardView.vue";
import ProfileView from "./views/profile/ProfileView.vue";
import { useSession, type PlatformRole } from "./composables/useSession";

const { token, role, userId, isAuthenticated, setSession, clearSession } = useSession();
const currentView = ref<"dashboard" | "chat" | "profile">("dashboard");

function handleLogin(payload: { token: string; role: PlatformRole }) {
  setSession(payload.token, payload.role);
  currentView.value = "dashboard";
}

function handleLogout() {
  clearSession();
  currentView.value = "dashboard";
}

function handleNavigate(view: "dashboard" | "chat" | "profile") {
  currentView.value = view;
}
</script>

<template>
  <main v-if="!isAuthenticated" class="app-shell">
    <LoginView @login="handleLogin" />
  </main>
  <main v-else class="app-shell app-auth-shell">
    <AppSidebar
      :role="role === 'admin' ? 'admin' : 'project_manager'"
      :current-view="currentView"
      @navigate="handleNavigate"
      @logout="handleLogout"
    />

    <section class="app-content">
      <AppTopBar
        :role="role === 'admin' ? 'admin' : 'project_manager'"
        :user-id="userId"
      />

      <section class="app-view">
        <DashboardView
          v-if="currentView === 'dashboard'"
          :role="role === 'admin' ? 'admin' : 'project_manager'"
          :token="token"
        />

        <ChatInterface
          v-else-if="currentView === 'chat'"
          :key="userId"
          :token="token"
          :user-id="userId"
          :role="role === 'admin' ? 'admin' : 'project_manager'"
        />

        <ProfileView
          v-else
          :role="role === 'admin' ? 'admin' : 'project_manager'"
          :user-id="userId"
        />
      </section>
    </section>
  </main>
</template>

<style scoped>
.app-shell {
  height: 100vh;
  box-sizing: border-box;
}

.app-auth-shell {
  display: flex;
  overflow: hidden;
}

.app-content {
  flex: 1;
  min-width: 0;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.app-view {
  flex: 1;
  min-height: 0;
  overflow: auto;
}
</style>