<script setup lang="ts">
import { ref } from "vue";
import { ChevronsLeft, LayoutDashboard, Bot, User, LogOut } from "@lucide/vue";

const props = defineProps<{
  role: "admin" | "project_manager";
  currentView: "dashboard" | "chat" | "profile";
}>();

const emit = defineEmits<{
  (event: "navigate", view: "dashboard" | "chat" | "profile"): void;
  (event: "logout"): void;
}>();

const isCollapsed = ref(false);

function roleLabel() {
  return props.role === "admin" ? "Admin" : "Project Manager";
}
</script>

<template>
  <aside :class="{ 'app-sidebar': true, collapsed: isCollapsed }">
    <div class="brand">
      <div v-show="!isCollapsed">
        <h1>Redmine Assist</h1>
        <p>{{ roleLabel() }}</p>
      </div>
      <button class="collapse-btn" type="button" @click="isCollapsed = !isCollapsed" aria-label="Toggle sidebar">
        <ChevronsLeft :class="{ rotated: isCollapsed }" />
      </button>
    </div>

    <nav class="nav-links">
      <button
        class="nav-btn"
        :class="{ active: currentView === 'dashboard' }"
        type="button"
        @click="emit('navigate', 'dashboard')"
      >
        <span v-show="!isCollapsed"><LayoutDashboard />Dashboard</span>
        <span v-show="isCollapsed"><LayoutDashboard /></span>
      </button>
      <button
        class="nav-btn"
        :class="{ active: currentView === 'chat' }"
        type="button"
        @click="emit('navigate', 'chat')"
      >
        <span v-show="!isCollapsed"><Bot />Chatbot</span>
        <span v-show="isCollapsed"><Bot /></span>
      </button>
      <button
        class="nav-btn"
        :class="{ active: currentView === 'profile' }"
        type="button"
        @click="emit('navigate', 'profile')"
      >
        <span v-show="!isCollapsed"><User />Profile</span>
        <span v-show="isCollapsed"><User /></span>
      </button>
    </nav>

    <div class="sidebar-footer">
      <button class="logout-btn" type="button" @click="emit('logout')">
        <span v-show="!isCollapsed"><LogOut />Log out</span>
        <span v-show="isCollapsed"><LogOut /></span>
      </button>
    </div>
  </aside>
</template>

<style scoped>
.app-sidebar {
  width: 230px;
  min-width: 230px;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  padding: var(--space-md);
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-subtle);
  transition: width 220ms ease, min-width 220ms ease;
}

.app-sidebar.collapsed {
  width: 78px;
  min-width: 78px;
}

.brand h1 {
  margin: 0;
  font-size: var(--text-lg);
  color: var(--text-primary);
}

.brand p {
  margin: var(--space-xs) 0 0;
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.brand {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-sm);
}

.collapse-btn {
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-secondary);
  border-radius: var(--radius-md);
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.collapse-btn:hover {
  color: var(--text-primary);
}

.collapse-btn svg {
  transition: transform 220ms ease;
}

.collapse-btn .rotated {
  transform: rotate(180deg);
}

.nav-links {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.nav-btn,
.logout-btn {
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-primary);
  border-radius: var(--radius-md);
  padding: 0.55rem 0.75rem;
  text-align: center;
  font-size: var(--text-sm);
  cursor: pointer;
}

.app-sidebar:not(.collapsed) .nav-btn,
.app-sidebar:not(.collapsed) .logout-btn {
  text-align: left;
}

.nav-btn.active {
  background: var(--bg-tertiary);
}

.sidebar-footer {
  margin-top: auto;
}

.logout-btn {
  width: 100%;
}
</style>
