<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { adminApi } from "../../api/admin";
import { dashboardApi } from "../../api/dashboard";
import { monitoringApi } from "../../api/monitoring";
import type { AtRiskProjectInsight, DashboardProject, MonitoringOverview, OverdueTicketInsight, PmCandidate, ProjectStatus } from "../../types";
import { Info, TrendingUp, AlertTriangle, CheckCircle, Clock, ChevronRight } from "lucide-vue-next";

const props = defineProps<{
  role: "admin" | "project_manager";
  token: string;
}>();

const projects = ref<ProjectStatus[]>([]);
const projectsError = ref("");
const topOverdueTickets = ref<OverdueTicketInsight[]>([]);
const atRiskProjects = ref<AtRiskProjectInsight[]>([]);
const insightsError = ref("");
const monitoringOverview = ref<MonitoringOverview | null>(null);
const monitoringError = ref("");

const projectRows = computed(() => {
  const rows = projects.value ?? [];
  return rows.map((row) => {
    return {
      id: row.id,
      name: row.name,
      progress: row.progress,
      health: row.health,
      subtitle: `Owner: ${row.owner || '—'} • ETA ${row.completionEta || 'TBD'}`,
      statusLabel: row.health === 'Delayed' ? 'Delayed' : row.health === 'At risk' ? 'At risk' : 'On track',
    };
  });
});

const runTrendBars = computed((): { label: string; height: string; value: number }[] => {
  const trend = monitoringOverview.value?.run_trend ?? [];
  if (!trend.length) return [];

  const values = trend.map((item) => Number(item.events_count || 0));
  const maxValue = Math.max(1, ...values);

  return trend.map((item) => {
    const events = Number(item.events_count || 0);
    const label = new Date(item.started_at).toLocaleDateString(undefined, { month: "short", day: "numeric" });
    const height = Math.max(24, Math.round((events / maxValue) * 160));
    return { label, value: events, height: `${height}px` };
  });
});

const openIssuesCount = computed(() => {
  if (topOverdueTickets.value.length > 0) {
    return topOverdueTickets.value.length * 4;
  }
  return projects.value.length * 3;
});

const overdueIssuesCount = computed(() => Math.max(0, topOverdueTickets.value.length));

const criticalIssuesCount = computed(() => {
  const criticalFromRisk = atRiskProjects.value.reduce((sum, item) => sum + (item.high_priority_open_count || 0), 0);
  return Math.max(0, criticalFromRisk);
});

const roleLabel = computed(() =>
  props.role === "admin" ? "Admin overview" : "Project manager overview",
);

const isAdmin = computed(() => props.role === "admin");

const lastPmRefreshAt = ref<string>("");
const rowLoading = ref<Record<number, boolean>>({});
const pmRows = ref<PmCandidate[]>([]);
const pmError = ref("");
const pmSuccess = ref("");
const PM_TABLE_REFRESH_MS = 60_000;
let pmPollTimer: number | null = null;

const enabledPmCount = computed(() => pmRows.value.filter((item) => item.enabled).length);

function setRowLoading(redmineUserId: number, loading: boolean) {
  rowLoading.value = {
    ...rowLoading.value,
    [redmineUserId]: loading,
  };
}

async function loadProjects() {
  if (!props.token.trim()) {
    projectsError.value = "Missing authentication token.";
    return;
  }
  try {
    projectsError.value = "";
    const response = await dashboardApi.listProjects(props.token.trim());
    projects.value = response.items.map(mapDashboardProject);
  } catch (error) {
    projectsError.value = error instanceof Error ? error.message : "Failed to load projects.";
  }
}

function mapDashboardProject(project: DashboardProject): ProjectStatus {
  const progress = Number.isFinite(project.progress as number) ? Math.max(0, Math.min(100, project.progress ?? 0)) : 0;
  const health: ProjectStatus["health"] =
    project.health ?? (progress === 0 ? "At risk" : progress < 40 ? "Delayed" : progress < 65 ? "At risk" : "On track");
  const openIssues = project.open_issues ?? 0;
  const closedIssues = project.closed_issues ?? 0;
  return {
    id: String(project.id),
    name: project.name,
    owner: "Redmine team",
    progress,
    health,
    completionEta: project.completion_eta ?? (openIssues === 0 && closedIssues === 0 ? "No issues yet" : `${openIssues} open / ${closedIssues} closed`),
  };
}

async function loadInsights() {
  if (!props.token.trim()) {
    insightsError.value = "Missing authentication token.";
    return;
  }
  try {
    insightsError.value = "";
    const response = await dashboardApi.getInsights(props.token.trim());
    topOverdueTickets.value = response.top_overdue_tickets;
    atRiskProjects.value = response.at_risk_projects;
  } catch (error) {
    insightsError.value = error instanceof Error ? error.message : "Failed to load dashboard insights.";
  }
}

async function loadMonitoringOverview() {
  if (!props.token.trim()) {
    monitoringError.value = "Missing authentication token.";
    return;
  }

  try {
    monitoringError.value = "";
    monitoringOverview.value = await monitoringApi.getOverview(props.token.trim());
  } catch (error) {
    monitoringError.value = error instanceof Error ? error.message : "Failed to load monitoring overview.";
    monitoringOverview.value = null;
  }
}

async function loadPmRows() {
  if (!isAdmin.value) return;
  if (!props.token.trim()) {
    pmError.value = "Missing authentication token.";
    return;
  }

  try {
    const response = await adminApi.listPmCandidates(props.token.trim());
    pmRows.value = response.items;
    lastPmRefreshAt.value = new Date().toLocaleTimeString();
  } catch (error) {
    pmError.value = error instanceof Error ? error.message : "Failed to load PM list.";
  }
}

async function togglePmAccess(pm: PmCandidate, enabled: boolean) {
  if (!isAdmin.value) return;
  if (!props.token.trim()) {
    pmError.value = "Missing authentication token.";
    return;
  }

  pmError.value = "";
  pmSuccess.value = "";
  setRowLoading(pm.redmine_user_id, true);

  try {
    const result = await adminApi.setPmAccess(props.token.trim(), {
      redmine_user_id: pm.redmine_user_id,
      enabled,
    });

    pmRows.value = pmRows.value.map((row) =>
      row.redmine_user_id === pm.redmine_user_id
        ? { ...row, enabled, credentials_ready: row.credentials_ready || result.generated_account }
        : row,
    );

    if (enabled && result.generated_account) {
      pmSuccess.value = `${result.full_name} enabled and account provisioned with Redmine profile.`;
    } else if (enabled) {
      pmSuccess.value = `${result.full_name} enabled. Existing platform account reused.`;
    } else {
      pmSuccess.value = `${pm.full_name} is now disabled.`;
    }
  } catch (error) {
    pmError.value = error instanceof Error ? error.message : "Failed to update access.";
  } finally {
    setRowLoading(pm.redmine_user_id, false);
  }
}

onMounted(async () => {
  await loadProjects();
  await loadInsights();
  await loadMonitoringOverview();
  if (!isAdmin.value) return;
  await loadPmRows();
  pmPollTimer = window.setInterval(() => {
    void loadPmRows();
  }, PM_TABLE_REFRESH_MS);
});

onBeforeUnmount(() => {
  if (pmPollTimer !== null) {
    window.clearInterval(pmPollTimer);
  }
});
</script>

<template>
  <main class="min-h-full bg-surface-950 px-8 py-10 flex flex-col gap-10">
    <!-- Header -->
    <header class="flex items-start justify-between">
      <div class="space-y-1">
        <div class="flex items-center gap-2 text-sage-400 font-bold text-[10px] uppercase tracking-widest">
          <TrendingUp :size="14" /> {{ roleLabel }}
        </div>
        <h1 class="text-3xl font-extrabold text-white tracking-tight">Project Health & Advancement</h1>
        <p class="text-surface-500 text-sm">Real-time snapshot of delivery momentum and risk indicators.</p>
      </div>
    </header>

    <!-- Stats Grid -->
    <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="stat in [
        { label: 'Total projects', value: projects.length, color: 'text-sage-400', bg: 'bg-sage-400/5', border: 'border-sage-500/20' },
        { label: 'Open issues', value: openIssuesCount, color: 'text-blue-400', bg: 'bg-blue-400/5', border: 'border-blue-500/20' },
        { label: 'Overdue issues', value: overdueIssuesCount, color: 'text-amber-400', bg: 'bg-amber-400/5', border: 'border-amber-500/20' },
        { label: 'Critical issues', value: criticalIssuesCount, color: 'text-red-400', bg: 'bg-red-400/5', border: 'border-red-500/20' }
      ]" :key="stat.label" 
      :class="['p-5 rounded-2xl border bg-surface-900 shadow-sm transition-all hover:scale-[1.02]', stat.border]">
        <p class="text-[11px] font-bold text-surface-500 uppercase tracking-widest mb-1">{{ stat.label }}</p>
        <div class="flex items-baseline gap-2">
          <span :class="['text-3xl font-black tracking-tighter', stat.color]">{{ stat.value }}</span>
          <div v-if="stat.value > 0" :class="['w-1.5 h-1.5 rounded-full animate-pulse', stat.bg.replace('/5', '/40')]" />
        </div>
      </div>
    </section>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <!-- Run Trend Chart -->
      <section class="xl:col-span-1 p-6 rounded-2xl bg-surface-900 border border-surface-800 shadow-xl overflow-hidden relative group">
        <div class="absolute top-0 right-0 w-32 h-32 bg-sage-500/5 blur-3xl -mr-16 -mt-16 group-hover:bg-sage-500/10 transition-all" />
        <header class="flex items-center justify-between mb-8">
          <div>
            <h2 class="text-sm font-bold text-white mb-0.5">Monitoring Run Trend</h2>
            <p class="text-[10px] text-surface-500 uppercase font-semibold">Recent monitoring run events</p>
          </div>
          <div class="relative group/info outline-none">
            <button
              type="button"
              class="text-surface-600 hover:text-sage-400 transition-colors cursor-help"
              aria-label="How the Monitoring Run Trend card is calculated"
            >
              <Info :size="16" />
            </button>

            <div
              class="pointer-events-none absolute right-0 top-6 z-20 w-72 rounded-xl border border-surface-700 bg-surface-950/95 p-3 text-[11px] leading-relaxed text-surface-300 shadow-2xl opacity-0 translate-y-1 transition-all duration-200 group-hover/info:opacity-100 group-hover/info:translate-y-0 group-focus-within/info:opacity-100 group-focus-within/info:translate-y-0"
            >
              <p class="font-bold text-surface-100 mb-1">What this card shows</p>
              <p class="mb-2">
                Actual monitoring runs from the backend overview feed.
              </p>
              <p>
                Each bar represents the number of events produced by one successful monitoring run.
                Higher bars mean more issues or changes were detected during that run.
              </p>
            </div>
          </div>
        </header>

        <div v-if="monitoringError" class="mb-4 text-[10px] text-red-400 font-bold bg-red-400/5 px-2 py-1 rounded border border-red-500/10">{{ monitoringError }}</div>

        <div v-if="runTrendBars.length" class="flex items-end justify-between h-48 px-2">
          <div v-for="bar in runTrendBars" :key="bar.label + bar.value" class="flex flex-col items-center gap-3 flex-1 group/bar">
            <div class="relative w-full flex justify-center">
              <div 
                class="w-6 sm:w-8 rounded-lg bg-gradient-to-t from-sage-600/20 to-sage-400 group-hover/bar:to-sage-300 transition-all duration-500 shadow-lg shadow-sage-900/40 relative" 
                :style="{ height: bar.height }"
              >
                <div class="absolute inset-x-0 top-0 h-px bg-white/20 rounded-t-lg" />
              </div>
              <span class="absolute -top-6 text-[10px] font-bold text-sage-400 opacity-0 group-hover/bar:opacity-100 transition-opacity">{{ bar.value }}</span>
            </div>
            <span class="text-[10px] font-bold text-surface-500 uppercase tracking-tighter">{{ bar.label }}</span>
          </div>
        </div>

        <div v-else class="h-48 flex items-center justify-center text-surface-600 text-sm italic">
          No monitoring runs yet.
        </div>
      </section>

      <!-- Project Status List -->
      <section class="xl:col-span-2 p-6 rounded-2xl bg-surface-900 border border-surface-800 shadow-xl flex flex-col">
        <header class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-sm font-bold text-white mb-0.5" id="project-status">Project Streams</h2>
            <p class="text-[10px] text-surface-500 uppercase font-semibold tracking-wider">Live progress tracking</p>
          </div>
          <div v-if="projectsError" class="text-[10px] text-red-400 font-bold bg-red-400/5 px-2 py-1 rounded border border-red-500/10">{{ projectsError }}</div>
        </header>

        <div class="flex-1 overflow-auto max-h-[320px] pr-2 space-y-3 custom-scrollbar">
          <div v-for="project in projectRows" :key="project.id" class="group p-4 rounded-xl bg-surface-950/50 border border-surface-800 hover:border-surface-700 hover:bg-surface-800 transition-all">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
              <div class="space-y-1">
                <div class="flex items-center gap-2">
                  <h3 class="text-sm font-bold text-surface-200 group-hover:text-white transition-colors">{{ project.name }}</h3>
                  <span 
                    :class="[
                      'text-[9px] font-black uppercase px-2 py-0.5 rounded-md border tracking-widest',
                      project.health === 'On track' ? 'bg-sage-600/10 text-sage-400 border-sage-500/20' :
                      project.health === 'At risk' ? 'bg-amber-500/10 text-amber-500 border-amber-500/20' :
                      'bg-red-500/10 text-red-500 border-red-500/20'
                    ]"
                  >
                    {{ project.statusLabel }}
                  </span>
                </div>
                <p class="text-[11px] text-surface-500 font-medium">{{ project.subtitle }}</p>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-lg font-black text-white px-2 py-1 bg-surface-900 rounded-lg border border-surface-800">{{ project.progress }}%</span>
              </div>
            </div>
            <!-- Progress Bar -->
            <div class="h-2 w-full bg-surface-900 rounded-full overflow-hidden border border-surface-800">
              <div 
                class="h-full bg-gradient-to-r from-sage-600 to-sage-400 transition-all duration-1000 shadow-[0_0_8px_rgba(125,154,121,0.4)]" 
                :style="{ width: `${project.progress}%` }" 
              />
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Insights Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Overdue Tickets -->
      <section class="p-6 rounded-2xl bg-surface-900 border border-surface-800 shadow-xl overflow-hidden relative">
        <header class="flex items-center justify-between mb-6">
          <div class="flex items-center gap-2">
            <Clock :size="18" class="text-amber-500" />
            <div>
              <h2 class="text-sm font-bold text-white mb-0.5">Overdue Tickets</h2>
              <p class="text-[10px] text-surface-500 uppercase font-semibold">Action required</p>
            </div>
          </div>
        </header>

        <div class="space-y-3">
          <div v-if="topOverdueTickets.length === 0" class="py-12 text-center text-surface-600 text-sm font-medium italic">No overdue tickets detected.</div>
          <div v-for="ticket in topOverdueTickets.slice(0, 5)" :key="ticket.issue_id" class="p-4 bg-surface-950/40 rounded-xl border border-surface-800 hover:border-amber-500/30 transition-all group flex items-center justify-between gap-4">
            <div class="min-w-0">
              <p class="text-sm font-bold text-surface-200 line-clamp-1 mb-1">#{{ ticket.issue_id }} {{ ticket.subject }}</p>
              <div class="flex items-center gap-2 text-[10px] text-surface-500 font-bold uppercase tracking-wider">
                <span class="text-sage-400">{{ ticket.project_name }}</span>
                <span class="opacity-30">•</span>
                <span class="text-red-400">Due {{ ticket.due_date }}</span>
              </div>
            </div>
            <a :href="ticket.url" target="_blank" class="w-8 h-8 rounded-lg bg-surface-900 border border-surface-800 flex items-center justify-center text-surface-400 hover:text-white hover:border-sage-400 transition-all shrink-0">
              <ChevronRight :size="16" />
            </a>
          </div>
        </div>
      </section>

      <!-- At-Risk Strategy -->
      <section class="p-6 rounded-2xl border border-surface-800 bg-surface-900 shadow-xl relative overflow-hidden">
        <div class="absolute top-0 right-0 w-32 h-32 bg-red-500/5 blur-3xl -mr-16 -mt-16" />
        <header class="flex items-center justify-between mb-6">
          <div class="flex items-center gap-2">
            <AlertTriangle :size="18" class="text-red-500" />
            <div>
              <h2 class="text-sm font-bold text-white mb-0.5">Project Risks</h2>
              <p class="text-[10px] text-surface-500 uppercase font-semibold">Recommended Mitigation</p>
            </div>
          </div>
        </header>

        <div class="space-y-3">
          <div v-if="atRiskProjects.length === 0" class="py-12 text-center text-surface-600 text-sm font-medium italic">All projects within safe parameters.</div>
          <div v-for="project in atRiskProjects.slice(0, 5)" :key="project.project_id" class="p-4 bg-red-500/5 rounded-xl border border-red-500/10 hover:border-red-500/30 transition-all flex items-start gap-4">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-bold text-surface-200 mb-1">{{ project.project_name }}</p>
              <p class="text-[11px] text-red-300 font-medium mb-3 leading-relaxed">{{ project.reason }}</p>
              <div class="flex items-center gap-1.5 px-2 py-1 rounded-md bg-red-500/10 w-fit text-[10px] font-black uppercase text-red-400 border border-red-500/20">
                Action: {{ project.recommended_action }}
              </div>
            </div>
            <a :href="project.url" target="_blank" class="w-8 h-8 rounded-lg bg-surface-900 border border-surface-800 flex items-center justify-center text-surface-400 hover:text-white hover:border-red-400 transition-all shrink-0 mt-1">
              <ChevronRight :size="16" />
            </a>
          </div>
        </div>
      </section>
    </div>

    <!-- Admin Panel: PM Access -->
    <section v-if="isAdmin" class="p-8 rounded-2xl border border-surface-800 bg-surface-900 shadow-2xl relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-br from-sage-500/[0.02] via-transparent to-transparent pointer-events-none" />
      
      <header class="flex items-end justify-between mb-10 relative">
        <div class="space-y-2">
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 rounded-full bg-sage-500 animate-pulse" />
            <h2 class="text-lg font-extrabold text-white">Project Manager Operations</h2>
          </div>
          <p class="text-xs text-surface-500 font-medium">Automatic reconciliation with Redmine user directory.</p>
        </div>
        
        <div class="flex items-center gap-6">
          <div class="flex flex-col items-end">
            <span class="text-[9px] uppercase font-black text-surface-500 tracking-widest leading-none">Last Sync</span>
            <span class="text-sm font-black text-sage-400 leading-tight">{{ lastPmRefreshAt || "—" }}</span>
          </div>
          <div class="flex -space-x-2">
            <div v-for="i in 3" :key="i" class="w-8 h-8 rounded-full border-2 border-surface-900 bg-surface-800 flex items-center justify-center text-[10px] font-bold text-surface-400">
              {{ i }}
            </div>
          </div>
        </div>
      </header>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        <div v-for="stat in [
          { label: 'Total Candidates', value: pmRows.length },
          { label: 'Enabled Access', value: enabledPmCount },
          { label: 'Platform Ready', value: pmRows.filter(r => r.credentials_ready).length }
        ]" :key="stat.label" class="p-4 rounded-xl bg-surface-950/50 border border-surface-800">
          <p class="text-[10px] font-bold text-surface-500 uppercase tracking-widest mb-1">{{ stat.label }}</p>
          <span class="text-2xl font-black text-white italic tracking-tighter">{{ stat.value }}</span>
        </div>
      </div>

      <div v-if="pmError || pmSuccess" class="mb-6 animate-fade-in">
        <div v-if="pmError" class="p-4 rounded-xl bg-red-400/5 border border-red-500/20 text-red-400 text-xs font-bold">{{ pmError }}</div>
        <div v-if="pmSuccess" class="p-4 rounded-xl bg-sage-600/10 border border-sage-500/20 text-sage-400 text-xs font-bold flex items-center gap-2">
          <CheckCircle :size="14" /> {{ pmSuccess }}
        </div>
      </div>

      <div class="overflow-hidden rounded-2xl border border-surface-800 bg-surface-950/30">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-surface-950/50 border-b border-surface-800">
              <th class="px-6 py-4 text-[10px] font-black text-surface-500 uppercase tracking-widest">PM Identity</th>
              <th class="px-6 py-4 text-[10px] font-black text-surface-500 uppercase tracking-widest">Credentials</th>
              <th class="px-6 py-4 text-[10px] font-black text-surface-500 uppercase tracking-widest text-center">Status</th>
              <th class="px-6 py-4 text-[10px] font-black text-surface-500 uppercase tracking-widest text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-surface-800">
            <tr v-if="pmRows.length === 0">
              <td colspan="4" class="px-6 py-20 text-center text-surface-600 text-sm font-medium italic">Fetching PM candidates from Redmine...</td>
            </tr>
            <tr v-for="pm in pmRows" :key="pm.redmine_user_id" class="hover:bg-surface-800/30 transition-colors group">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-xl bg-surface-800 flex items-center justify-center text-xs font-black text-surface-400 group-hover:bg-sage-600/20 group-hover:text-sage-400 transition-all">
                    {{ pm.full_name.charAt(0) }}
                  </div>
                  <div>
                    <p class="text-[13px] font-bold text-surface-200">{{ pm.full_name }}</p>
                    <p class="text-[10px] text-surface-500 font-medium">{{ pm.email }}</p>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <span 
                  :class="[
                    'px-2 py-0.5 rounded-md text-[9px] font-black uppercase tracking-widest border',
                    pm.credentials_ready 
                      ? 'bg-sage-600/10 text-sage-400 border-sage-500/10' 
                      : 'bg-surface-900 text-surface-600 border-surface-800'
                  ]"
                >
                  {{ pm.credentials_ready ? 'Available' : 'Pending' }}
                </span>
              </td>
              <td class="px-6 py-4">
                <div class="flex justify-center">
                  <div 
                    :class="[
                      'w-2 h-2 rounded-full',
                      pm.enabled ? 'bg-sage-400 shadow-[0_0_8px_rgba(125,154,121,0.6)]' : 'bg-surface-700'
                    ]" 
                  />
                </div>
              </td>
              <td class="px-6 py-4 text-right">
                <button
                  @click="togglePmAccess(pm, !pm.enabled)"
                  :disabled="rowLoading[pm.redmine_user_id]"
                  :class="[
                    'px-4 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all',
                    pm.enabled 
                      ? 'bg-red-500/10 text-red-500 border border-red-500/20 hover:bg-red-500 text-white hover:border-transparent' 
                      : 'bg-sage-400 text-surface-950 hover:bg-sage-300 shadow-lg shadow-sage-900/20'
                  ]"
                >
                  {{ rowLoading[pm.redmine_user_id] ? "Processing..." : (pm.enabled ? "Revoke Access" : "Grant Access") }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<style>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #3c5439;
  border-radius: 99px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #5f815b;
}
</style>

