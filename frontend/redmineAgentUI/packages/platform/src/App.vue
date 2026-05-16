<script setup lang="ts">
import { computed, watch } from "vue";
import AppSidebar from "./components/Dashboard/AppSidebar.vue";
import AppTopBar from "./components/Dashboard/AppTopBar.vue";
import ChatInterface from "./components/Dashboard/ChatInterface.vue";
import RedmineCallback from "./views/auth/RedmineCallback.vue";
import DashboardView from "./views/DashboardView.vue";
import ProfileView from "./components/Dashboard/ProfileView.vue";
import { useSession, type PlatformRole } from "@redsage/ui-core/composables/useSession";
import { useRoute, useRouter } from "vue-router";

const { token, role, fullName, email, userId, isAuthenticated, setSession, clearSession } = useSession();
const router = useRouter();
const route = useRoute();

const currentView = computed<"dashboard" | "chat" | "profile">(() => {
  if (route.name === "chat") return "chat";
  if (route.name === "profile") return "profile";
  return "dashboard";
});

const selectedThreadId = computed(() => {
  const threadId = route.query.threadId;
  return typeof threadId === "string" && threadId.trim() ? threadId.trim() : null;
});

const isOAuthCallback = computed(() => route.name === "oauth-callback");

const isLanding = computed(() => route.name === "landing");
const isLogin = computed(() => route.name === "login");
const isSignup = computed(() => route.name === "signup");
const isPublicRoute = computed(() => isLanding.value || isLogin.value || isSignup.value);

watch(isAuthenticated, (authenticated) => {
  if (authenticated && (route.name === "landing" || route.name === "login" || route.name === "signup")) {
    void router.replace({ name: "dashboard" });
  }
}, { immediate: true });

function handleLogin(payload: { token: string; role: PlatformRole; fullName: string }) {
  setSession(payload.token, payload.role, payload.fullName);
  const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "";
  void router.replace(redirect || { name: "dashboard" });
}

function handleLogout() {
  clearSession();
  void router.replace({ name: "login" });
}

function startLogin() {
  void router.push({ name: "login" });
}

function handleNavigate(view: "dashboard" | "chat" | "profile" | "thread", threadId?: string) {
  if (view === 'thread') {
    void router.push({ name: 'chat', query: threadId ? { threadId } : undefined });
    return;
  }
  void router.push({ name: view as "dashboard" | "chat" | "profile" });
}
</script>

<template>
  <RedmineCallback v-if="isOAuthCallback" />
  <main v-else-if="!isAuthenticated" class="app-shell">
    <RouterView v-if="isPublicRoute" v-slot="{ Component }">
      <component
        :is="Component"
        v-if="Component"
        @start-login="startLogin"
        @login="handleLogin"
        @back="void router.push({ name: 'landing' })"
      />
    </RouterView>
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
        :full-name="fullName"
        :token="token"
        @navigate="handleNavigate"
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
          :open-thread-id="selectedThreadId"
        />

        <ProfileView
          v-else
          :role="role === 'admin' ? 'admin' : 'project_manager'"
          :user-id="userId"
          :full-name="fullName"
          :email="email"
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