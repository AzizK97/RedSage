<script setup lang="ts">
import { Bell, CircleHelp, Search, UserCircle2, Sun, Moon } from "@lucide/vue";
import { ref, onMounted } from "vue";

const props = defineProps<{
  role: "admin" | "project_manager";
  userId: string;
  fullName?: string;
}>();

const roleLabel = props.role === "admin" ? "Admin" : "Project Manager";
const displayName = props.fullName?.trim() || props.userId || "Unknown user";

const theme = ref<string>((typeof window !== "undefined" && localStorage.getItem("theme")) || "dark");

onMounted(() => {
  try {
    document.documentElement.setAttribute("data-theme", theme.value);
  } catch (e) {
    /* noop in SSR */
  }
});

function toggleTheme() {
  theme.value = theme.value === "light" ? "dark" : "light";
  try {
    document.documentElement.setAttribute("data-theme", theme.value);
    localStorage.setItem("theme", theme.value);
  } catch (e) {
    /* noop */
  }
}
</script>

<template>
  <header class="app-topbar">
    <div class="search-wrap">
      <Search :size="16" class="icon" />
      <input type="search" placeholder="Search projects, tasks, or conversations..." />
    </div>

    <div class="topbar-actions">
      <button type="button" class="icon-btn" aria-label="Notifications">
        <Bell :size="18" />
      </button>
      <button type="button" class="icon-btn" aria-label="Help">
        <CircleHelp :size="18" />
      </button>

      <button
        type="button"
        class="icon-btn"
        aria-label="Toggle theme"
        @click="toggleTheme"
      >
        <Sun v-if="theme === 'light'" :size="16" />
        <Moon v-else :size="16" />
      </button>

      <div class="profile-pill" aria-label="Profile">
        <UserCircle2 :size="18" />
        <div class="profile-meta">
          <span class="user">{{ displayName }}</span>
          <span class="role">{{ roleLabel }}</span>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-topbar {
  height: 64px;
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-primary);
  padding: var(--space-sm) var(--space-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
}

.search-wrap {
  flex: 1;
  max-width: 620px;
  position: relative;
}

.search-wrap .icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
}

.search-wrap input {
  width: 100%;
  border: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: 999px;
  padding: 0.6rem 0.85rem 0.6rem 2.2rem;
  font-size: var(--text-sm);
}

.search-wrap input:focus {
  outline: none;
  border-color: var(--accent-blue);
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.icon-btn,
.support-btn {
  border: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: var(--radius-md);
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.icon-btn svg {
  display: block;
}

.icon-btn {
  width: 36px;
}

.support-btn {
  gap: var(--space-xs);
  padding: 0 var(--space-sm);
  font-size: var(--text-sm);
}

.profile-pill {
  border: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  padding: 0.35rem 0.55rem;
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  color: var(--text-primary);
}

.profile-meta {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.user {
  font-size: var(--text-xs);
}

.role {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

@media (max-width: 980px) {
  .support-btn,
  .profile-meta {
    display: none;
  }

  .profile-pill {
    width: 36px;
    height: 36px;
    justify-content: center;
    padding: 0;
  }
}
</style>
