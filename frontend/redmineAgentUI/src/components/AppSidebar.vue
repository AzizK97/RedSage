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
        <h1>RedSage</h1>
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
        <span class="nav-item" :class="{ collapsed: isCollapsed }">
          <LayoutDashboard class="nav-icon" :size="16" />
          <span v-show="!isCollapsed" class="nav-label">Dashboard</span>
        </span>
      </button>
      <button
        class="nav-btn"
        :class="{ active: currentView === 'chat' }"
        type="button"
        @click="emit('navigate', 'chat')"
      >
        <span class="nav-item" :class="{ collapsed: isCollapsed }">
          <Bot class="nav-icon" :size="16" />
          <span v-show="!isCollapsed" class="nav-label">Chatbot</span>
        </span>
      </button>
      <button
        class="nav-btn"
        :class="{ active: currentView === 'profile' }"
        type="button"
        @click="emit('navigate', 'profile')"
      >
        <span class="nav-item" :class="{ collapsed: isCollapsed }">
          <User class="nav-icon" :size="16" />
          <span v-show="!isCollapsed" class="nav-label">Profile</span>
        </span>
      </button>
    </nav>

    <div class="sidebar-footer">
      <button class="logout-btn" type="button" @click="emit('logout')">
        <span class="nav-item" :class="{ collapsed: isCollapsed }">
          <LogOut class="nav-icon" :size="16" />
          <span v-show="!isCollapsed" class="nav-label">Log out</span>
        </span>
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
  padding: 0.6rem 0.75rem;
  text-align: left;
  font-size: var(--text-sm);
  cursor: pointer;
}

.nav-btn,
.logout-btn,
.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.nav-btn,
.logout-btn {
  width: 100%;
}

.nav-item {
  width: 100%;
  justify-content: flex-start;
}

.nav-item.collapsed {
  justify-content: center;
  gap: 0;
}

.nav-icon {
  flex: 0 0 auto;
  width: 16px;
  height: 16px;
}

.nav-btn:hover,
.logout-btn:hover {
  background: var(--bg-tertiary);
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

.nav-label {
  line-height: 1;
}
</style>
