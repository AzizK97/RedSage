<script setup lang="ts">
import { Bell, Search, UserCircle2, Sun, Moon, AlertCircle, CheckCircle2, Info } from "@lucide/vue";
import { ref, onBeforeUnmount, onMounted } from "vue";
import { monitoringApi } from "../api/monitoring";
import type { MonitoringNotification } from "../types";
import { debounce } from "../utils";
import { search } from "../api/search";

const props = defineProps<{
  role: "admin" | "project_manager";
  userId: string;
  fullName?: string;
  token: string;
}>();

const roleLabel = props.role === "admin" ? "Admin" : "Project Manager";
const displayName = props.fullName?.trim() || props.userId || "Unknown user";

const theme = ref<string>((typeof window !== "undefined" && localStorage.getItem("theme")) || "dark");
const notifications = ref<MonitoringNotification[]>([]);
const notificationsOpen = ref(false);
const notificationsError = ref("");
const notificationsTimer = ref<number | null>(null);
const unreadCount = ref(0);
let lastSeenCreatedAt = "";

// Search state
const query = ref("");
const showResults = ref(false);
const results = ref<any[]>([]);
const loading = ref(false);
const error = ref("");
const activeTab = ref<'messages'|'threads'>('messages');

const tokenVal = props.token || '';

const debouncedDoSearch = debounce(async (q: string, tab: 'messages'|'threads') => {
  if (!q || q.trim().length < 2) {
    results.value = [];
    loading.value = false;
    showResults.value = false;
    return;
  }

  loading.value = true;
  error.value = '';
  try {
    const resp = await search(q.trim(), tab, tokenVal, 10, 0);
    results.value = resp.items || [];
    showResults.value = true;
  } catch (err: any) {
    error.value = err instanceof Error ? err.message : String(err);
    results.value = [];
    showResults.value = true;
  } finally {
    loading.value = false;
  }
}, 300);

function onInput() {
  debouncedDoSearch(query.value, activeTab.value);
}

onMounted(() => {
  try {
    document.documentElement.setAttribute("data-theme", theme.value);
  } catch (e) {
    /* noop in SSR */
  }
  void loadNotifications();
  notificationsTimer.value = window.setInterval(() => {
    void loadNotifications();
  }, 20_000);
});

onBeforeUnmount(() => {
  if (notificationsTimer.value !== null) {
    window.clearInterval(notificationsTimer.value);
  }
});

const emit = defineEmits<{
  (event: "navigate", view: "profile"): void;
  (event: "navigate", view: "thread", threadId: string): void;
}>();

function toggleTheme() {
  theme.value = theme.value === "light" ? "dark" : "light";
  try {
    document.documentElement.setAttribute("data-theme", theme.value);
    localStorage.setItem("theme", theme.value);
  } catch (e) {
    /* noop */
  }
}

async function loadNotifications() {
  const token = props.token.trim();
  if (!token) {
    notificationsError.value = "Missing token.";
    return;
  }
  try {
    notificationsError.value = "";
    const response = await monitoringApi.listNotifications(token);
    notifications.value = response.items;
    const latest = response.items[0]?.created_at || "";
    if (!lastSeenCreatedAt && latest) {
      lastSeenCreatedAt = latest;
    }
    if (latest && latest !== lastSeenCreatedAt) {
      unreadCount.value = response.items.findIndex((n) => n.created_at === lastSeenCreatedAt);
      if (unreadCount.value < 0) unreadCount.value = response.items.length;
    }
  } catch (error) {
    notificationsError.value = error instanceof Error ? error.message : "Failed to load notifications.";
  }
}

function toggleNotificationsPanel() {
  notificationsOpen.value = !notificationsOpen.value;
  if (notificationsOpen.value) {
    unreadCount.value = 0;
    lastSeenCreatedAt = notifications.value[0]?.created_at || lastSeenCreatedAt;
  }
}

function timeAgo(isoDate: string): string {
  const ts = new Date(isoDate).getTime();
  if (!Number.isFinite(ts)) return "just now";
  const diff = Math.max(0, Date.now() - ts);
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} h ago`;
  const days = Math.floor(hours / 24);
  return `${days} d ago`;
}

function openThread(id: string) {
  showResults.value = false;
  query.value = '';
  emit('navigate', 'thread', id);
}
</script>

<template>
  <header class="app-topbar">
    <div class="search-wrap">
      <Search :size="16" class="icon" />
      <input v-model="query" @input="onInput" type="search" placeholder="Search projects, tasks, or conversations..." />
      <div v-if="showResults" class="search-results-popover">
        <div class="tabs">
          <button :class="{active: activeTab==='messages'}" @click="activeTab='messages'">Messages</button>
          <button :class="{active: activeTab==='threads'}" @click="activeTab='threads'">Conversations</button>
        </div>
        <div class="results">
          <p v-if="loading">Searching…</p>
          <p v-else-if="error">{{ error }}</p>
          <ul v-else>
            <li
              v-for="item in results"
              :key="item.id || item.thread_id"
              class="result-item clickable"
              @click="openThread(item.thread_id || item.id)"
              role="button"
              tabindex="0"
            >
              <div class="result-meta">
                <strong>{{ item.title || 'Conversation' }}</strong>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <div class="topbar-actions">
      <button type="button" class="icon-btn bell-btn" aria-label="Notifications" @click="toggleNotificationsPanel">
        <Bell :size="18" />
        <span v-if="unreadCount > 0" class="notif-badge">{{ unreadCount > 9 ? "9+" : unreadCount }}</span>
      </button>
      <div v-if="notificationsOpen" class="notifications-popover">
        <div class="popover-header">
          <p class="popover-title">Notifications</p>
          <button type="button" class="popover-close" @click="notificationsOpen = false">×</button>
        </div>
        <p v-if="notificationsError" class="popover-error">{{ notificationsError }}</p>
        <ul v-else-if="notifications.length" class="popover-list">
          <li v-for="item in notifications.slice(0, 6)" :key="item.id" class="popover-item">
            <div class="notif-icon-wrap" :class="`sev-${item.severity}`">
              <AlertCircle v-if="item.severity === 'critical' || item.severity === 'warning'" :size="14" />
              <CheckCircle2 v-else-if="item.severity === 'success'" :size="14" />
              <Info v-else :size="14" />
            </div>
            <div class="popover-item-content">
              <div class="popover-row">
                <p class="popover-item-title">{{ item.title }}</p>
                <span class="popover-time">{{ timeAgo(item.created_at) }}</span>
              </div>
              <p class="popover-subtitle">{{ item.subtitle }}</p>
            </div>
          </li>
        </ul>
        <p v-else class="popover-empty">No notifications yet.</p>
        <a class="popover-footer" href="#">View all notifications</a>
      </div>

      <button
        type="button"
        class="icon-btn"
        aria-label="Toggle theme"
        @click="toggleTheme"
      >
        <Sun v-if="theme === 'light'" :size="16" />
        <Moon v-else :size="16" />
      </button>

      <div class="profile-pill" aria-label="Profile" @click="emit('navigate', 'profile')">
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

.search-results-popover {
  position: absolute;
  top: 46px;
  left: 0;
  width: 620px;
  max-height: 60vh;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  box-shadow: 0 12px 28px rgba(0,0,0,0.12);
  z-index: 40;
  padding: 10px;
}

.search-results-popover .tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}
.search-results-popover .tabs button {
  border: none;
  background: transparent;
  padding: 6px 10px;
  border-radius: 8px;
  cursor: pointer;
}
.search-results-popover .tabs button.active {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
}
.search-results-popover .results { max-height: 48vh; overflow: auto; }
.result-item { padding: 8px; border-bottom: 1px solid var(--border-subtle); }
.result-item.clickable { cursor: pointer; }
.result-item.clickable:hover { background: var(--bg-tertiary); }
.result-meta { display:flex; gap:8px; align-items:baseline; }
.result-meta .ts { color: var(--text-secondary); font-size: 12px; margin-left:auto }
.snippet { margin: 4px 0 0; color: var(--text-secondary); font-size: 13px }

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
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.bell-btn {
  position: relative;
}

.notif-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  min-width: 16px;
  height: 16px;
  border-radius: 999px;
  background: var(--accent-red);
  color: white;
  font-size: 10px;
  line-height: 16px;
  text-align: center;
  padding: 0 4px;
}

.notifications-popover {
  position: absolute;
  top: 44px;
  right: 118px;
  width: min(460px, 75vw);
  max-height: 360px;
  overflow: auto;
  border: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  padding: 10px;
  z-index: 20;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.18);
}

.popover-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.popover-title {
  margin: 0;
  font-size: var(--text-sm);
  font-weight: 600;
}

.popover-close {
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
}

.popover-error {
  margin: 0;
  color: var(--accent-red);
  font-size: var(--text-xs);
}

.popover-empty {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-xs);
}

.popover-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.popover-item {
  display: flex;
  gap: 10px;
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  background: var(--bg-tertiary);
  padding: 10px;
}

.notif-icon-wrap {
  width: 26px;
  height: 26px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notif-icon-wrap.sev-critical,
.notif-icon-wrap.sev-warning {
  color: #dc2626;
  background: rgba(220, 38, 38, 0.1);
}

.notif-icon-wrap.sev-success {
  color: #16a34a;
  background: rgba(22, 163, 74, 0.1);
}

.notif-icon-wrap.sev-info {
  color: #4f46e5;
  background: rgba(79, 70, 229, 0.1);
}

.popover-item-content {
  min-width: 0;
  width: 100%;
}

.popover-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
}

.popover-item-title {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
}

.popover-subtitle {
  margin: 2px 0 0;
  color: var(--text-secondary);
  font-size: 12px;
}

.popover-time {
  color: var(--text-secondary);
  font-size: 11px;
  white-space: nowrap;
}

.popover-footer {
  display: block;
  margin-top: 8px;
  text-align: center;
  color: #4f46e5;
  font-size: 13px;
  text-decoration: none;
  font-weight: 600;
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

.profile-pill:hover {
  background: var(--bg-tertiary);
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
