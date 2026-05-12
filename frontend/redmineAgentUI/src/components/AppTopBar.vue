<script setup lang="ts">
import { Bell, Search, UserCircle2, Sun, Moon, AlertCircle, CheckCircle2, Info, X } from "lucide-vue-next";
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
  <header class="h-16 border-b border-surface-800 bg-surface-950 px-6 flex items-center justify-between gap-4 sticky top-0 z-30">
    <div class="flex-1 max-w-2xl relative">
      <div class="relative group">
        <Search :size="16" class="absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-500 group-focus-within:text-sage-400 transition-colors" />
        <input 
          v-model="query" 
          @input="onInput" 
          type="search" 
          placeholder="Search projects, tasks, or conversations..." 
          class="w-full bg-surface-900 border border-surface-800 text-surface-200 text-sm rounded-xl py-2 pl-10 pr-4 outline-none focus:border-sage-500/40 focus:ring-4 focus:ring-sage-500/5 transition-all shadow-inner"
        />
      </div>

      <div v-if="showResults" class="absolute top-[calc(100%+12px)] left-0 w-full max-h-[60vh] bg-surface-900 border border-surface-800 rounded-2xl shadow-2xl shadow-black/50 z-50 overflow-hidden flex flex-col backdrop-blur-xl">
        <div class="flex gap-2 p-3 border-b border-surface-800 bg-surface-950/50">
          <button 
            v-for="tab in ['messages', 'threads']" :key="tab"
            @click="activeTab = tab as any"
            :class="[
              'px-4 py-1.5 rounded-lg text-xs font-semibold capitalize transition-all border',
              activeTab === tab 
                ? 'bg-sage-600/10 text-sage-300 border-sage-500/20' 
                : 'text-surface-400 border-transparent hover:bg-surface-800'
            ]"
          >
            {{ tab }}
          </button>
        </div>
        
        <div class="flex-1 overflow-auto p-2">
          <div v-if="loading" class="p-8 flex flex-col items-center gap-3 text-surface-500">
            <div class="w-5 h-5 border-2 border-sage-500/30 border-t-sage-500 rounded-full animate-spin"></div>
            <p class="text-xs font-medium">Searching...</p>
          </div>
          <p v-else-if="error" class="p-8 text-center text-xs text-red-400 bg-red-400/5 rounded-xl border border-red-400/10">{{ error }}</p>
          <ul v-else-if="results.length" class="space-y-1">
            <li
              v-for="item in results"
              :key="item.id || item.thread_id"
              @click="openThread(item.thread_id || item.id)"
              class="group p-3 rounded-xl hover:bg-surface-800 transition-all cursor-pointer border border-transparent hover:border-surface-700"
            >
              <div class="flex flex-col gap-1.5">
                <div class="flex items-center gap-3">
                  <strong class="text-sm text-surface-200 group-hover:text-sage-300 transition-colors">{{ item.title || 'Conversation' }}</strong>
                  <div class="flex gap-2 ml-auto">
                    <span v-if="item.project_name" class="px-2 py-0.5 rounded-md bg-surface-950 text-[10px] font-bold text-surface-400 border border-surface-800 uppercase tracking-wider">
                      {{ item.project_name }}
                    </span>
                    <span v-if="item.issue_id" class="px-2 py-0.5 rounded-md bg-copper-500/10 text-[10px] font-bold text-copper-400 border border-copper-500/20">
                      #{{ item.issue_id }}
                    </span>
                  </div>
                </div>
                <div class="flex items-center gap-2 text-[11px] text-surface-500">
                  <span class="font-medium text-surface-400">{{ item.author_name || 'Unknown' }}</span>
                  <span class="opacity-30">•</span>
                  <span>{{ item.created_at ? timeAgo(item.created_at) : '' }}</span>
                </div>
              </div>
            </li>
          </ul>
          <div v-else class="p-12 text-center">
            <p class="text-sm text-surface-500 font-medium">No results found for "{{ query }}"</p>
          </div>
        </div>
      </div>
    </div>

    <div class="flex items-center gap-3">
      <!-- Notifications -->
      <div class="relative">
        <button 
          @click="toggleNotificationsPanel"
          class="relative w-10 h-10 flex items-center justify-center rounded-xl border border-surface-800 text-surface-400 hover:text-white hover:bg-surface-800 transition-all"
        >
          <Bell :size="18" />
          <span v-if="unreadCount > 0" class="absolute -top-1 -right-1 min-w-[18px] h-[18px] bg-red-600 !text-white text-[10px] font-extrabold rounded-full flex items-center justify-center border-2 border-surface-950 px-1 shadow-lg shadow-red-900/40">
            {{ unreadCount > 9 ? "9+" : unreadCount }}
          </span>
        </button>

        <div v-if="notificationsOpen" class="absolute top-[calc(100%+12px)] right-0 w-[420px] max-h-[80vh] bg-surface-900 border border-surface-800 rounded-2xl shadow-2xl shadow-black/50 overflow-hidden flex flex-col z-50 backdrop-blur-xl animate-scale-in origin-top-right">
          <div class="flex items-center justify-between p-4 border-b border-surface-800 bg-surface-950/50">
            <p class="text-sm font-bold text-surface-200">Notifications</p>
            <button @click="notificationsOpen = false" class="text-surface-500 hover:text-white transition-colors">
              <X :size="16" />
            </button>
          </div>
          
          <div class="flex-1 overflow-auto p-3 space-y-2">
            <p v-if="notificationsError" class="p-4 text-xs text-red-400 font-medium text-center bg-red-400/5 rounded-xl">{{ notificationsError }}</p>
            <ul v-else-if="notifications.length" class="space-y-2">
              <li v-for="item in notifications.slice(0, 8)" :key="item.id" class="p-3 bg-surface-950/40 rounded-xl border border-surface-800 hover:border-surface-700 transition-all group">
                <div class="flex gap-3">
                  <div 
                    :class="[
                      'w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border transition-all shadow-sm',
                      item.severity === 'critical' ? 'bg-red-500/10 text-red-400 border-red-500/20 shadow-red-500/5' :
                      item.severity === 'warning' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20 shadow-amber-500/5' :
                      item.severity === 'success' ? 'bg-sage-600/10 text-sage-400 border-sage-500/20 shadow-sage-900/5' :
                      'bg-surface-800 text-surface-400 border-surface-700 text-surface-300'
                    ]"
                  >
                    <AlertCircle v-if="item.severity === 'critical' || item.severity === 'warning'" :size="16" />
                    <CheckCircle2 v-else-if="item.severity === 'success'" :size="16" />
                    <Info v-else :size="16" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-start justify-between gap-2 mb-1">
                      <p class="text-[13px] font-bold text-surface-200 leading-snug">{{ item.title }}</p>
                      <span class="text-[10px] font-bold text-surface-500 whitespace-nowrap uppercase tracking-wider">{{ timeAgo(item.created_at) }}</span>
                    </div>
                    <p class="text-xs text-surface-400 leading-relaxed truncate">{{ item.subtitle }}</p>
                  </div>
                </div>
              </li>
            </ul>
            <div v-else class="p-12 text-center text-surface-500">
              <Bell :size="32" class="mx-auto mb-3 opacity-20" />
              <p class="text-sm font-medium">No notifications yet.</p>
            </div>
          </div>
          <a href="#" class="p-3 text-center text-xs font-bold text-sage-400 hover:text-sage-300 hover:bg-surface-800 transition-all border-t border-surface-800 uppercase tracking-widest bg-surface-950/20">View all notifications</a>
        </div>
      </div>

      <!-- Theme Toggle -->
      <button 
        @click="toggleTheme"
        class="w-10 h-10 flex items-center justify-center rounded-xl border border-surface-800 text-surface-400 hover:text-white hover:bg-surface-800 transition-all"
        title="Toggle Theme"
      >
        <Sun v-if="theme === 'light'" :size="18" />
        <Moon v-else :size="18" />
      </button>

      <!-- Profile -->
      <button 
        @click="emit('navigate', 'profile')"
        class="flex items-center gap-3 px-3 py-1.5 h-10 rounded-xl border border-surface-800 bg-surface-900 hover:bg-surface-800 hover:border-surface-700 transition-all group"
      >
        <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-sage-500/20 to-copper-500/20 flex items-center justify-center text-surface-300 border border-surface-800 group-hover:border-sage-500/30">
          <UserCircle2 :size="18" class="group-hover:text-white transition-colors" />
        </div>
        <div class="flex flex-col text-left lg:block hidden">
          <p class="text-[11px] font-bold text-surface-200 leading-none mb-0.5">{{ displayName }}</p>
          <p class="text-[9px] font-bold text-surface-500 uppercase tracking-widest leading-none">{{ roleLabel }}</p>
        </div>
      </button>
    </div>
  </header>
</template>

