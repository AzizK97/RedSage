<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, provide, ref, watch } from "vue";
import { dashboardApi } from "@redsage/api-client/dashboard";
import { monitoringApi } from "@redsage/api-client/monitoring";
import type { AtRiskProjectInsight, DashboardProject, MonitoringOverview, OverdueTicketInsight, ProjectStatus, TaskDistributionItem } from "@redsage/ui-core/types";
import { Info, TrendingUp, AlertTriangle, Clock, ChevronRight, ChevronDown, Check, Printer } from "lucide-vue-next";
import DashboardPdfPreview from "../components/Dashboard/DashboardPdfPreview.vue";

const props = defineProps<{
  role: "admin" | "project_manager";
  token: string;
}>();

const projects = ref<ProjectStatus[]>([]);
const projectsError = ref("");
const topOverdueTickets = ref<OverdueTicketInsight[]>([]);
const atRiskProjects = ref<AtRiskProjectInsight[]>([]);
const taskDistribution = ref<TaskDistributionItem[]>([]);
const insightsError = ref("");
const monitoringOverview = ref<MonitoringOverview | null>(null);
const monitoringError = ref("");
const lastDashboardRefreshAt = ref("");
const selectedProjectId = ref<string | null>(null);
const projectSelectorRef = ref<HTMLElement | null>(null);
const isProjectSelectorOpen = ref(false);

const selectedProjectLabel = computed(() => {
  if (!selectedProjectId.value) return "All Projects";
  return (projects.value as ProjectStatus[]).find((project) => project.id === selectedProjectId.value)?.name ?? "All Projects";
});

function toggleProjectSelector() {
  isProjectSelectorOpen.value = !isProjectSelectorOpen.value;
}

function closeProjectSelector() {
  isProjectSelectorOpen.value = false;
}

function selectProjectScope(projectId: string | null) {
  selectedProjectId.value = projectId;
  closeProjectSelector();
}

function handleProjectSelectorClickOutside(event: MouseEvent) {
  if (!projectSelectorRef.value) return;
  const target = event.target as Node | null;
  if (target && !projectSelectorRef.value.contains(target)) {
    closeProjectSelector();
  }
}

const selectedProjectIdentifier = computed(() => {
  if (!selectedProjectId.value) return null;
  return projects.value.find((project) => String(project.id) === selectedProjectId.value)?.identifier ?? selectedProjectId.value;
});

const projectRows = computed(() => {
  const rows = projects.value as ProjectStatus[];
  const filtered = selectedProjectId.value
    ? rows.filter((p) => p.id === selectedProjectId.value)
    : rows;
  return filtered.map((row) => {
    return {
      id: row.id,
      name: row.name,
      progress: row.progress ?? 0,
      health: row.health,
      subtitle: `Owner: ${row.owner || '—'} • ETA ${row.completionEta || 'TBD'}`,
      statusLabel: row.health === 'Delayed' ? 'Delayed' : row.health === 'At risk' ? 'At risk' : 'On track',
    };
  });
});

const showPdfPreview = ref(false);

const runTrendBars = computed((): { id: string; label: string; fullDate: string; height: string; value: number; toneClass: string }[] => {
  const trend = (monitoringOverview.value?.run_trend ?? []) as Array<{ started_at: string; events_count?: number | string }>;
  if (!trend.length) return [];

  const values = trend.map((item) => Number(item.events_count || 0));
  const maxValue = Math.max(1, ...values);

  return trend.map((item, index) => {
    const events = Number(item.events_count || 0);
    const startedAt = new Date(item.started_at);
    const label = startedAt.toLocaleDateString(undefined, { month: "short", day: "numeric" });
    const fullDate = startedAt.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric", year: "numeric" });
    const ratio = events / maxValue;
    const height = Math.max(24, Math.round((events / maxValue) * 160));
    const toneClass = ratio >= 0.75
      ? "bg-sage-400"
      : ratio >= 0.4
        ? "bg-sage-500"
        : "bg-sage-600";
    return { id: `${item.started_at}-${index}`, label, fullDate, value: events, height: `${height}px`, toneClass };
  });
});

const monitoringTrendSummary = computed(() => {
  if (!runTrendBars.value.length) {
    return {
      runCount: 0,
      totalEvents: 0,
      averageEvents: 0,
      latestEvents: 0,
      trendLabel: "No trend",
      trendPercent: 0,
      trendToneClass: "text-surface-400",
      peakLabel: "—",
      peakValue: 0,
    };
  }

  const totalEvents = runTrendBars.value.reduce((sum, bar) => sum + bar.value, 0);
  const runCount = runTrendBars.value.length;
  const averageEvents = Math.round(totalEvents / runCount);
  const peak = runTrendBars.value.reduce((best, current) => (current.value > best.value ? current : best), runTrendBars.value[0]);

  const latestEvents = runTrendBars.value[runCount - 1]?.value ?? 0;
  const previousEvents = runTrendBars.value[runCount - 2]?.value ?? latestEvents;
  const delta = latestEvents - previousEvents;

  let trendLabel = "Stable";
  let trendPercent = 0;
  let trendToneClass = "text-surface-300";

  if (delta > 0) {
    trendLabel = "Increasing";
    trendPercent = previousEvents > 0 ? Math.round((delta / previousEvents) * 100) : 100;
    trendToneClass = "text-sage-400";
  } else if (delta < 0) {
    trendLabel = "Decreasing";
    trendPercent = previousEvents > 0 ? Math.round((Math.abs(delta) / previousEvents) * 100) : 0;
    trendToneClass = "text-amber-400";
  }

  return {
    runCount,
    totalEvents,
    averageEvents,
    latestEvents,
    trendLabel,
    trendPercent,
    trendToneClass,
    peakLabel: peak.label,
    peakValue: peak.value,
  };
});

const runTrendLinePoints = computed(() => {
  if (!runTrendBars.value.length) return "";
  const width = 100;
  const height = 36;
  const maxValue = Math.max(1, ...runTrendBars.value.map((bar) => bar.value));

  return runTrendBars.value
    .map((bar, index) => {
      const x = runTrendBars.value.length === 1 ? width / 2 : (index / (runTrendBars.value.length - 1)) * width;
      const y = height - (bar.value / maxValue) * (height - 4);
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");
});

const openIssuesCount = computed(() => {
  const scopedProjects = selectedProjectId.value
    ? projects.value.filter((project) => String(project.id) === selectedProjectId.value)
    : projects.value;

  return scopedProjects.reduce((sum, project) => sum + (project.open_issues ?? 0), 0);
});

const overdueIssuesCount = computed(() => {
  const filtered = selectedProjectIdentifier.value
    ? topOverdueTickets.value.filter((t) => t.project_identifier === selectedProjectIdentifier.value)
    : topOverdueTickets.value;
  return Math.max(0, filtered.length);
});

const criticalIssuesCount = computed(() => {
  const filtered = selectedProjectIdentifier.value
    ? (atRiskProjects.value as AtRiskProjectInsight[]).filter((p) => p.project_identifier === selectedProjectIdentifier.value)
    : (atRiskProjects.value as AtRiskProjectInsight[]);
  const criticalFromRisk = filtered.reduce((sum: number, item: AtRiskProjectInsight) => sum + (item.high_priority_open_count || 0), 0);
  return Math.max(0, criticalFromRisk);
});

const roleLabel = computed(() =>
  props.role === "admin" ? "Admin overview" : "Project manager overview",
);

const isAdmin = computed(() => props.role === "admin");

const filteredOverdueTickets = computed(() =>
  selectedProjectIdentifier.value
    ? topOverdueTickets.value.filter((t) => t.project_identifier === selectedProjectIdentifier.value)
    : topOverdueTickets.value,
);

const filteredAtRiskProjects = computed(() =>
  selectedProjectIdentifier.value
    ? atRiskProjects.value.filter((p) => p.project_identifier === selectedProjectIdentifier.value)
    : atRiskProjects.value,
);

// Project Health Score calculation (0-100)
const projectHealthScore = computed(() => {
  if (projectRows.value.length === 0) return 100;
  const avgProgress = projectRows.value.reduce((sum, p) => sum + p.progress, 0) / projectRows.value.length;
  const healthCounts = projectRows.value.reduce(
    (acc, p) => {
      if (p.health === "On track") acc.onTrack++;
      else if (p.health === "At risk") acc.atRisk++;
      else acc.delayed++;
      return acc;
    },
    { onTrack: 0, atRisk: 0, delayed: 0 }
  );
  const healthScore = (healthCounts.onTrack / projectRows.value.length) * 60 + (avgProgress / 100) * 40;
  return Math.round(healthScore);
});

const projectHealthStatus = computed(() => {
  const score = projectHealthScore.value;
  if (score >= 75) return { label: "Healthy", color: "text-sage-400", bg: "bg-sage-500/10", border: "border-sage-500/20" };
  if (score >= 50) return { label: "At Risk", color: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/20" };
  return { label: "Critical", color: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/20" };
});

// Milestone slippage calculation
const milestoneSlippage = computed(() => {
  const totalProjects = projectRows.value.length;
  if (totalProjects === 0) return 0;
  const slippedProjects = projectRows.value.filter((p) => p.health !== "On track").length;
  return Math.round((slippedProjects / totalProjects) * 100);
});

const schedulePressureChart = computed(() => {
  const items = filteredAtRiskProjects.value.slice(0, 5) as Array<{
    project_id?: string | number;
    project_identifier?: string;
    project_name?: string;
    name: string;
    overdue_count?: number;
    high_priority_open_count?: number;
    reason?: string;
    recommended_action?: string;
  }>;
  const maxPressure = Math.max(
    1,
    ...items.map((item) => (item.overdue_count || 0) + (item.high_priority_open_count || 0)),
  );

  return items.map((item) => {
    const pressure = (item.overdue_count || 0) + (item.high_priority_open_count || 0);
    return {
      id: String(item.project_id ?? item.project_identifier ?? item.name),
      label: item.project_name || item.name,
      detail: item.reason || item.recommended_action || "Review schedule risk",
      pressure,
      width: `${Math.max(12, Math.round((pressure / maxPressure) * 100))}%`,
    };
  });
});

const scheduleHealthSummary = computed(() => {
  const criticalProjects = filteredAtRiskProjects.value as Array<{
    project_id?: string | number;
    project_identifier?: string;
    project_name?: string;
    name: string;
    overdue_count?: number;
    high_priority_open_count?: number;
    reason?: string;
    recommended_action?: string;
    url?: string;
  }>;
  const overdueTickets = filteredOverdueTickets.value;
  const totalPressure = criticalProjects.reduce(
    (sum, item) => sum + (item.overdue_count || 0) + (item.high_priority_open_count || 0),
    0,
  );

  return {
    criticalProjects: criticalProjects.length,
    overdueTickets: overdueTickets.length,
    totalPressure,
    topProject: criticalProjects[0] || null,
    topTicket: overdueTickets[0] || null,
  };
});

// Resource capacity insights
const teamWorkloadInsight = computed(() => {
  const criticalCount = criticalIssuesCount.value;
  const overdueCount = overdueIssuesCount.value;
  if (criticalCount > 5 || overdueCount > 10) return "⚠️ High workload detected. Consider task redistribution.";
  if (criticalCount > 0) return "🟡 Monitor critical tasks closely.";
  return "✅ Team capacity is balanced.";
});

const taskDistributionSummary = computed(() => {
  const rows = taskDistribution.value;
  const totalOpen = rows.reduce((sum, row) => sum + (row.open_tasks || 0), 0);
  const overloaded = rows.filter((row) => (row.load_score || 0) >= 6).length;
  const unassignedOpen = rows
    .filter((row) => String(row.assignee_name || "").toLowerCase() === "unassigned")
    .reduce((sum, row) => sum + (row.open_tasks || 0), 0);
  return {
    people: rows.length,
    totalOpen,
    unassignedOpen,
    overloaded,
    topLoad: rows[0] || null,
  };
});

const taskDistributionChart = computed(() => {
  const rows = taskDistribution.value.slice(0, 6);
  const maxLoad = Math.max(1, ...rows.map((row) => Number(row.load_score || row.open_tasks || 0)));
  const palette = ["bg-sage-500", "bg-copper-500", "bg-amber-500", "bg-sky-500", "bg-violet-500", "bg-rose-500"];

  return rows.map((row, index) => {
    const load = Number(row.load_score || row.open_tasks || 0);
    const percent = Math.max(8, Math.round((load / maxLoad) * 100));
    return {
      ...row,
      load,
      percent,
      colorClass: palette[index % palette.length],
    };
  });
});

// Velocity trend (simplified - uses project progress as proxy)
const velocityTrend = computed(() => {
  const avgProgress = projectRows.value.length > 0
    ? projectRows.value.reduce((sum, p) => sum + p.progress, 0) / projectRows.value.length
    : 0;
  if (avgProgress > 70) return "Accelerating";
  if (avgProgress > 40) return "Steady";
  return "Behind Schedule";
});

// Risk matrix data (maps at-risk projects to risk level)
const riskMatrixData = computed(() => {
  const high = filteredAtRiskProjects.value.filter((p) => (p.high_priority_open_count || 0) > 5).length;
  const medium = filteredAtRiskProjects.value.filter((p) => (p.high_priority_open_count || 0) >= 2 && (p.high_priority_open_count || 0) <= 5).length;
  const low = filteredAtRiskProjects.value.filter((p) => (p.high_priority_open_count || 0) < 2).length;
  return { high, medium, low };
});

const DASHBOARD_REFRESH_MS = 30_000;
let dashboardPollTimer: number | null = null;

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

provide("dashboardData", {
  projects,
  topOverdueTickets,
  atRiskProjects,
  taskDistribution,
  monitoringOverview,
  selectedProjectId,
  selectedProjectIdentifier,
  openIssuesCount,
  overdueIssuesCount,
  criticalIssuesCount,
  scheduleHealthSummary,
  taskDistributionSummary,
  projectRows,
  schedulePressureChart,
  milestoneSlippage,
  teamWorkloadInsight,
  selectedProjectLabel,
});

function mapDashboardProject(project: DashboardProject): ProjectStatus {
  const progress = Number.isFinite(project.progress as number) ? Math.max(0, Math.min(100, project.progress ?? 0)) : 0;
  const health: ProjectStatus["health"] =
    project.health ?? (progress === 0 ? "At risk" : progress < 40 ? "Delayed" : progress < 65 ? "At risk" : "On track");
  const openIssues = project.open_issues ?? 0;
  const closedIssues = project.closed_issues ?? 0;
  return {
    id: String(project.id),
    name: project.name,
    identifier: project.identifier,
    owner: "Redmine team",
    progress,
    health,
    open_issues: openIssues,
    closed_issues: closedIssues,
    completionEta: project.completion_eta ?? (openIssues === 0 && closedIssues === 0 ? "No issues yet" : `${openIssues} open / ${closedIssues} closed`),
  };
}

async function loadInsights(projectIdentifier?: string | null) {
  if (!props.token.trim()) {
    insightsError.value = "Missing authentication token.";
    return;
  }
  try {
    insightsError.value = "";
    const response = await dashboardApi.getInsights(props.token.trim(), projectIdentifier);
    topOverdueTickets.value = response.top_overdue_tickets;
    atRiskProjects.value = response.at_risk_projects;
    taskDistribution.value = response.task_distribution ?? [];
  } catch (error) {
    insightsError.value = error instanceof Error ? error.message : "Failed to load dashboard insights.";
  }
}

watch(selectedProjectIdentifier, (projectIdentifier) => {
  void loadInsights(projectIdentifier);
});

async function loadMonitoringOverview() {
  if (!props.token.trim()) {
    monitoringError.value = "Missing authentication token.";
    return;
  }

  try {
    monitoringError.value = "";
    monitoringOverview.value = await monitoringApi.getOverview(props.token.trim());
    lastDashboardRefreshAt.value = new Date().toLocaleTimeString();
  } catch (error) {
    monitoringError.value = error instanceof Error ? error.message : "Failed to load monitoring overview.";
    monitoringOverview.value = null;
  }
}

async function refreshDashboardData() {
  await Promise.allSettled([
    loadProjects(),
    loadInsights(selectedProjectIdentifier.value),
    loadMonitoringOverview(),
  ]);
}

function handleVisibilityRefresh() {
  if (document.visibilityState === "visible") {
    void refreshDashboardData();
  }
}

onMounted(async () => {
  document.addEventListener("mousedown", handleProjectSelectorClickOutside);
  document.addEventListener("visibilitychange", handleVisibilityRefresh);
  window.addEventListener("focus", handleVisibilityRefresh);
  await refreshDashboardData();

  dashboardPollTimer = window.setInterval(() => {
    void refreshDashboardData();
  }, DASHBOARD_REFRESH_MS);
});

onBeforeUnmount(() => {
  document.removeEventListener("mousedown", handleProjectSelectorClickOutside);
  document.removeEventListener("visibilitychange", handleVisibilityRefresh);
  window.removeEventListener("focus", handleVisibilityRefresh);
  if (dashboardPollTimer !== null) {
    window.clearInterval(dashboardPollTimer);
  }
});
</script>

<template>
  <main id="dashboard-root" class="min-h-full bg-surface-950 px-4 sm:px-6 lg:px-8 py-8 sm:py-10 text-surface-900">
    <div id="dashboard-print-root" class="mx-auto flex w-full max-w-7xl flex-col gap-6 lg:gap-8">
      <!-- Print header (hidden by default, visible only during print) -->
      <div class="no-print-hide print-only-show" 
           style="display:none"
           id="pdf-report-header">
        <div style="display:flex; justify-content:space-between; align-items:center; 
                    padding-bottom: 12px; border-bottom: 2px solid #c0392b; margin-bottom: 20px">
          <div>
            <span style="font-size:22px; font-weight:800; color:#c0392b">RedSage</span>
            <span style="font-size:15px; font-weight:600; color:#111; margin-left:12px">
              Project Health & Advancement
            </span>
            <div style="font-size:11px; color:#666; margin-top:2px">
              Generated on: {{ new Date().toLocaleString() }}
            </div>
          </div>
          <div style="font-size:12px; color:#666">{{ selectedProjectLabel }}</div>
        </div>
      </div>

      <header class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-2">
          <div class="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.24em] text-sage-400">
            <TrendingUp :size="14" /> {{ roleLabel }}
          </div>
          <div class="space-y-1">
            <h1 class="text-3xl sm:text-4xl font-black tracking-tight text-white">Project Health & Advancement</h1>
            <p class="max-w-2xl text-sm text-surface-400">A concise portfolio view for planning, delivery, risk, and operational access.</p>
            <div class="mt-3 inline-flex items-center gap-2 rounded-full border border-surface-200/70 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.24em] shadow-sm">
              <span :class="projectHealthStatus.color">{{ projectHealthStatus.label }}</span>
              <span class="text-surface-300">•</span>
              <span class="text-surface-500">Velocity {{ velocityTrend }}</span>
            </div>
          </div>
        </div>

        <div ref="projectSelectorRef" class="w-full max-w-xs no-print">
          <label class="mb-2 block text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Project scope</label>
          <div class="relative">
            <button
              type="button"
              class="project-selector-trigger"
              :aria-expanded="isProjectSelectorOpen"
              aria-haspopup="listbox"
              @click="toggleProjectSelector"
            >
              <span class="truncate">{{ selectedProjectLabel }}</span>
              <ChevronDown :size="16" :class="['transition-transform duration-200', isProjectSelectorOpen ? 'rotate-180' : 'rotate-0']" />
            </button>

            <transition name="fade-scale">
              <div v-if="isProjectSelectorOpen" class="project-selector-menu" role="listbox" aria-label="Project scope selector">
                <button
                  type="button"
                  class="project-selector-option"
                  :class="{ 'project-selector-option--active': selectedProjectId === null }"
                  @click="selectProjectScope(null)"
                >
                  <span>All Projects</span>
                  <Check v-if="selectedProjectId === null" :size="16" class="project-selector-check" />
                </button>

                <button
                  v-for="project in projects"
                  :key="project.id"
                  type="button"
                  class="project-selector-option"
                  :class="{ 'project-selector-option--active': selectedProjectId === project.id }"
                  @click="selectProjectScope(project.id)"
                >
                  <span class="truncate">{{ project.name }}</span>
                  <Check v-if="selectedProjectId === project.id" :size="16" class="project-selector-check" />
                </button>
              </div>
            </transition>
          </div>
        </div>
        <div class="flex items-end justify-end mt-3 lg:mt-0">
          <button
            type="button"
            class="inline-flex items-center gap-2 rounded-md border border-surface-700 bg-surface-800 px-3 py-2 text-sm font-semibold text-surface-200 hover:bg-surface-700 no-print"
            @click="showPdfPreview = true"
          >
            <Printer :size="16" />
            <span>Download as PDF</span>
          </button>
        </div>
      </header>

      <section class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <article class="relative overflow-hidden rounded-2xl border border-surface-800 bg-surface-900 p-5 shadow-sm before:absolute before:left-0 before:right-0 before:top-0 before:h-1 before:bg-gradient-to-r before:from-sage-500 before:to-sage-400/65">
          <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Total Projects</p>
          <div class="mt-3 text-4xl font-black tracking-tight text-white">{{ selectedProjectId ? 1 : projects.length }}</div>
          <p class="mt-1 text-sm text-surface-400">Portfolio scope currently in view.</p>
        </article>

        <article class="relative overflow-hidden rounded-2xl border border-surface-800 bg-surface-900 p-5 shadow-sm before:absolute before:left-0 before:right-0 before:top-0 before:h-1 before:bg-gradient-to-r before:from-blue-500 before:to-blue-400/65">
          <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Open Issues</p>
          <div class="mt-3 text-4xl font-black tracking-tight text-white">{{ openIssuesCount }}</div>
          <p class="mt-1 text-sm text-surface-400">Issues still needing delivery attention.</p>
        </article>

        <article class="relative overflow-hidden rounded-2xl border border-surface-800 bg-surface-900 p-5 shadow-sm before:absolute before:left-0 before:right-0 before:top-0 before:h-1 before:bg-gradient-to-r before:from-amber-500 before:to-amber-400/65">
          <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Overdue Issues</p>
          <div class="mt-3 text-4xl font-black tracking-tight text-white">{{ overdueIssuesCount }}</div>
          <p class="mt-1 text-sm text-surface-400">Tickets already slipping past due dates.</p>
        </article>

        <article class="relative overflow-hidden rounded-2xl border border-surface-800 bg-surface-900 p-5 shadow-sm before:absolute before:left-0 before:right-0 before:top-0 before:h-1 before:bg-gradient-to-r before:from-red-500 before:to-red-400/65">
          <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Critical Issues</p>
          <div class="mt-3 text-4xl font-black tracking-tight text-white">{{ criticalIssuesCount }}</div>
          <p class="mt-1 text-sm text-surface-400">High-priority blockers that need escalation.</p>
        </article>
      </section>

      <section class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <article class="overflow-hidden rounded-2xl border border-surface-800 bg-surface-900 p-6 shadow-sm">
          <header class="mb-5 flex items-start justify-between gap-4">
            <div class="space-y-1">
              <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Team Capacity</p>
              <h2 class="text-xl font-bold text-white">Task distribution by developer</h2>
              <p class="text-sm text-surface-400">Open tasks, overdue items, and weighted load per assignee.</p>
            </div>
            <div class="rounded-xl border border-surface-700 bg-surface-800 px-3 py-2 text-right">
              <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-surface-500">Overloaded</p>
              <p class="text-lg font-black text-amber-400">{{ taskDistributionSummary.overloaded }}</p>
            </div>
          </header>

          <div class="mb-5 grid grid-cols-3 gap-3">
            <div class="rounded-xl border border-surface-800 bg-surface-800 p-3">
              <p class="text-[10px] uppercase tracking-[0.2em] text-surface-500">Developers</p>
              <p class="mt-1 text-2xl font-black text-white">{{ taskDistributionSummary.people }}</p>
            </div>
            <div class="rounded-xl border border-surface-800 bg-surface-800 p-3">
              <p class="text-[10px] uppercase tracking-[0.2em] text-surface-500">Unassigned work</p>
              <p class="mt-1 text-2xl font-black text-white">{{ taskDistributionSummary.unassignedOpen }}</p>
            </div>
            <div class="rounded-xl border border-surface-800 bg-surface-800 p-3">
              <p class="text-[10px] uppercase tracking-[0.2em] text-surface-500">Top load</p>
              <p class="mt-1 text-2xl font-black text-white">{{ taskDistributionSummary.topLoad ? taskDistributionSummary.topLoad.assignee_name : '—' }}</p>
            </div>
          </div>

          <div v-if="taskDistributionChart.length" class="mb-5 overflow-hidden rounded-2xl border border-surface-800 bg-surface-800 p-4">
            <div class="mb-3 flex items-center justify-between text-[10px] uppercase tracking-[0.2em] text-surface-500">
              <span>Load intensity chart</span>
              <span>Highest load at {{ taskDistributionChart[0].assignee_name }}</span>
            </div>
            <div class="space-y-3">
              <div v-for="item in taskDistributionChart" :key="String(item.assignee_id ?? item.assignee_name)" class="space-y-1.5">
                <div class="flex items-center justify-between gap-3 text-xs">
                  <div class="min-w-0">
                    <p class="truncate font-semibold text-white">{{ item.assignee_name }}</p>
                    <p class="text-surface-500">{{ item.open_tasks }} open • {{ item.overdue_tasks }} overdue</p>
                  </div>
                  <div class="shrink-0 text-right">
                    <p class="font-semibold text-white">{{ item.load }}</p>
                    <p class="text-surface-500">load</p>
                  </div>
                </div>
                <div class="h-2 overflow-hidden rounded-full bg-surface-700">
                  <div class="h-2 rounded-full transition-all duration-700" :class="item.colorClass" :style="{ width: `${item.percent}%` }" />
                </div>
              </div>
            </div>
          </div>

          <div v-else class="mb-5 rounded-2xl border border-dashed border-surface-800 bg-surface-800 px-4 py-8 text-center text-sm text-surface-500">
            No task distribution data yet.
          </div>

          <div class="grid gap-3 md:grid-cols-2">
            <div class="rounded-xl border border-surface-800 bg-surface-800 p-4">
              <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-surface-500">Insight</p>
              <h3 class="mt-2 text-base font-bold text-white">{{ teamWorkloadInsight }}</h3>
            </div>
            <div class="rounded-xl border border-surface-800 bg-surface-800 p-4">
              <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-surface-500">Recommendation</p>
              <p class="mt-2 text-sm leading-relaxed text-surface-400">
                {{ criticalIssuesCount > 5 ? 'Redistribute critical tasks across the team and reduce WIP immediately.' : 'Balance remains acceptable, but keep an eye on developers with higher load scores.' }}
              </p>
            </div>
          </div>
        </article>

        <article class="rounded-2xl border border-surface-800 bg-surface-900 p-6 shadow-sm">
          <header class="flex items-start gap-3">
            <div class="mt-0.5 rounded-full bg-red-500/15 p-2 text-red-400 ring-1 ring-red-500/25">
              <Clock :size="16" />
            </div>
            <div class="space-y-2">
              <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">AI Insight: Schedule Health</p>
              <h2 class="text-lg font-bold text-white">
                {{ milestoneSlippage > 30 ? 'Critical schedule drift detected.' : milestoneSlippage > 10 ? 'Schedule drift is emerging.' : 'Schedule adherence is strong.' }}
              </h2>
              <p class="text-sm leading-relaxed text-surface-400">
                Recommendation: {{ milestoneSlippage > 30 ? 'Replan milestones, reassign owners, and protect critical path work now.' : 'Maintain current execution rhythm and review any slipping projects weekly.' }}
              </p>
            </div>
          </header>

          <div class="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div class="rounded-xl border border-red-500/20 bg-red-500/10 p-4">
              <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-red-300">Critical projects</p>
              <div class="mt-2 text-3xl font-black text-red-200">{{ scheduleHealthSummary.criticalProjects }}</div>
              <p class="mt-1 text-xs text-red-300">Projects with overdue or high-priority work.</p>
            </div>
            <div class="rounded-xl border border-amber-500/20 bg-amber-500/10 p-4">
              <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-amber-300">Overdue items</p>
              <div class="mt-2 text-3xl font-black text-amber-200">{{ scheduleHealthSummary.overdueTickets }}</div>
              <p class="mt-1 text-xs text-amber-300">Open issues past due date.</p>
            </div>
            <div class="rounded-xl border border-blue-500/20 bg-blue-500/10 p-4">
              <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-blue-300">Pressure score</p>
              <div class="mt-2 text-3xl font-black text-blue-200">{{ scheduleHealthSummary.totalPressure }}</div>
              <p class="mt-1 text-xs text-blue-300">Combined schedule load across risky projects.</p>
            </div>
          </div>

          <div class="mt-5 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
            <div class="rounded-xl border border-surface-800 bg-surface-800 p-4">
              <div class="flex items-center justify-between gap-3">
                <div>
                  <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-surface-500">Critical path</p>
                  <h3 class="mt-1 text-sm font-semibold text-white">Most pressured projects</h3>
                </div>
                <span class="rounded-full border border-red-500/20 bg-red-500/10 px-3 py-1 text-[11px] font-semibold text-red-300">
                  {{ schedulePressureChart.length }} shown
                </span>
              </div>

              <div v-if="schedulePressureChart.length" class="mt-4 space-y-4">
                <div v-for="item in schedulePressureChart" :key="item.id" class="space-y-2">
                  <div class="flex items-center justify-between gap-3 text-xs">
                    <div>
                      <div class="font-medium text-surface-200">{{ item.label }}</div>
                      <div class="text-surface-500">{{ item.detail }}</div>
                    </div>
                    <div class="font-semibold text-red-300">{{ item.pressure }}</div>
                  </div>
                  <div class="h-2 rounded-full bg-surface-700">
                    <div class="h-2 rounded-full bg-gradient-to-r from-red-500 to-amber-400" :style="{ width: item.width }" />
                  </div>
                </div>
              </div>

              <div v-else class="mt-4 rounded-xl border border-dashed border-surface-700 bg-surface-900/50 px-4 py-5 text-sm text-surface-500">
                No risky projects are currently driving schedule pressure.
              </div>
            </div>

            <div class="rounded-xl border border-surface-800 bg-surface-800 p-4">
              <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-surface-500">What is critical</p>
              <div class="mt-3 space-y-3">
                <div v-if="scheduleHealthSummary.topProject" class="rounded-xl border border-red-500/20 bg-red-500/10 p-3">
                  <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-red-300">Top project</p>
                  <div class="mt-1 text-sm font-semibold text-white">{{ scheduleHealthSummary.topProject.project_name || scheduleHealthSummary.topProject.project_identifier }}</div>
                  <p class="mt-1 text-xs leading-relaxed text-red-200/90">{{ scheduleHealthSummary.topProject.recommended_action }}</p>
                </div>

                <div v-if="scheduleHealthSummary.topTicket" class="rounded-xl border border-amber-500/20 bg-amber-500/10 p-3">
                  <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-amber-300">Top overdue issue</p>
                  <div class="mt-1 text-sm font-semibold text-white">{{ scheduleHealthSummary.topTicket.subject }}</div>
                  <p class="mt-1 text-xs text-amber-200/90">
                    Due {{ scheduleHealthSummary.topTicket.due_date }} • {{ scheduleHealthSummary.topTicket.project_name || scheduleHealthSummary.topTicket.project_identifier }}
                  </p>
                </div>

                <div v-if="!scheduleHealthSummary.topProject && !scheduleHealthSummary.topTicket" class="rounded-xl border border-surface-700 bg-surface-900/50 p-3 text-sm text-surface-500">
                  No critical schedule items found.
                </div>

                <div class="rounded-xl border border-surface-700 bg-surface-900/50 p-3">
                  <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-surface-500">Recommendation</p>
                  <p class="mt-2 text-sm leading-relaxed text-surface-300">
                    {{ milestoneSlippage > 30 ? 'Re-plan milestone dates, surface the blocked items first, and move capacity to the critical path.' : 'Keep reviewing the slipping projects and clear overdue items before they stack up.' }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </article>
      </section>

      <section class="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <article class="rounded-2xl border border-surface-800 bg-surface-900 p-6 shadow-sm xl:col-span-1">
          <header class="mb-5 space-y-1">
            <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Risk Landscape</p>
            <h2 class="text-xl font-bold text-white">Risk distribution</h2>
          </header>

          <div class="grid grid-cols-3 gap-3">
            <div class="rounded-xl border border-red-500/30 bg-red-500/10 p-4">
              <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-red-400">Critical</p>
              <div class="mt-2 text-3xl font-black text-red-300">{{ riskMatrixData.high }}</div>
              <p class="mt-1 text-xs text-red-400">{{ riskMatrixData.high > 0 ? 'Escalate immediately.' : 'No critical concentration.' }}</p>
            </div>
            <div class="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4">
              <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-amber-400">Medium</p>
              <div class="mt-2 text-3xl font-black text-amber-300">{{ riskMatrixData.medium }}</div>
              <p class="mt-1 text-xs text-amber-400">Monitor closely.</p>
            </div>
            <div class="rounded-xl border border-blue-500/30 bg-blue-500/10 p-4">
              <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-blue-400">Low</p>
              <div class="mt-2 text-3xl font-black text-blue-300">{{ riskMatrixData.low }}</div>
              <p class="mt-1 text-xs text-blue-400">Within threshold.</p>
            </div>
          </div>

          <div class="mt-5 border-t border-surface-800 pt-4">
            <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Recommendation</p>
            <p class="mt-2 text-sm leading-relaxed text-surface-400">
              {{ riskMatrixData.high > 0 ? `Focus immediately on ${riskMatrixData.high} high-risk project(s) and escalate the mitigation plan.` : 'Risk posture looks healthy. Keep the current controls and review weekly.' }}
            </p>
          </div>
        </article>

          <article class="rounded-2xl border border-surface-800 bg-surface-900 p-6 shadow-sm xl:col-span-2">
            <header class="mb-6 space-y-1">
              <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Throughput & Quality</p>
              <h2 class="text-xl font-bold text-white">Delivery efficiency</h2>
            </header>

            <div class="space-y-6">
              <div>
                <div class="mb-2 flex items-center justify-between">
                  <span class="text-sm font-medium text-surface-300">Completion Rate</span>
                  <span class="text-sm font-semibold text-sage-400">
                  {{ projects.length > 0 ? Math.round((projectRows.filter((p) => p.progress >= 90).length / projects.length) * 100) : 0 }}%
                </span>
              </div>
              <div class="h-2 rounded-full bg-surface-700">
                <div
                  class="h-2 rounded-full bg-sage-500 transition-all duration-700"
                  :style="{ width: (projects.length > 0 ? Math.round((projectRows.filter((p) => p.progress >= 90).length / projects.length) * 100) : 0) + '%' }"
                />
              </div>
              <p class="mt-2 text-xs text-surface-500">Projects already at 90%+ completion.</p>
            </div>

            <div>
              <div class="mb-2 flex items-center justify-between">
                <span class="text-sm font-medium text-surface-300">Quality Index</span>
                <span class="text-sm font-semibold" :class="overdueIssuesCount === 0 ? 'text-sage-400' : overdueIssuesCount < 5 ? 'text-amber-400' : 'text-red-400'">
                  {{ Math.max(0, 100 - (overdueIssuesCount * 5)) }}/100
                </span>
              </div>
              <div class="h-2 rounded-full bg-surface-700">
                <div
                  class="h-2 rounded-full bg-blue-500 transition-all duration-700"
                  :style="{ width: `${Math.max(0, 100 - (overdueIssuesCount * 5))}%` }"
                />
              </div>
              <p class="mt-2 text-xs text-surface-500">Measured against overdue ticket pressure.</p>
            </div>

            <div>
              <div class="mb-2 flex items-center justify-between">
                <span class="text-sm font-medium text-surface-300">Milestone Health</span>
                <span class="text-sm font-semibold text-amber-400">{{ 100 - milestoneSlippage }}%</span>
              </div>
              <div class="h-2 rounded-full bg-surface-700">
                <div
                  class="h-2 rounded-full bg-amber-500 transition-all duration-700"
                  :style="{ width: `${100 - milestoneSlippage}%` }"
                />
              </div>
              <p class="mt-2 text-xs text-surface-500">Share of projects still on schedule.</p>
            </div>
          </div>
        </article>
      </section>

      <section>
        <div class="mb-4 flex items-center justify-between">
          <div>
            <h2 class="text-xl font-bold text-white">Execution Tracking</h2>
            <p class="text-sm text-surface-400">Monitoring trend and stream progress.</p>
          </div>
        </div>

        <div class="grid grid-cols-1 gap-6 xl:grid-cols-3">
          <article class="relative overflow-hidden rounded-2xl border border-surface-800 bg-surface-900 p-6 shadow-sm xl:col-span-1">
            <div class="absolute right-0 top-0 h-28 w-28 -translate-y-8 translate-x-8 rounded-full bg-sage-500/5 blur-3xl" />
            <header class="mb-5 flex items-start justify-between gap-4">
              <div class="space-y-1">
                <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Monitoring Run Trend</p>
                <h2 class="text-lg font-bold text-white">Recent monitoring runs</h2>
                <p class="text-[10px] font-medium uppercase tracking-[0.18em] text-surface-500">Live refresh: {{ lastDashboardRefreshAt || 'Waiting for first sync' }}</p>
              </div>
              <div class="group relative">
                <button type="button" class="rounded-full p-2 text-surface-500 transition hover:bg-surface-800 hover:text-surface-300" aria-label="Monitoring run info">
                  <Info :size="16" />
                </button>
                <div class="pointer-events-none absolute right-0 top-12 z-10 w-72 rounded-2xl border border-surface-800 bg-surface-900 p-4 text-xs leading-relaxed text-surface-400 opacity-0 shadow-lg transition group-hover:opacity-100">
                  <p class="mb-2 font-semibold text-white">What this card shows</p>
                  <p>Bars reflect actual run events from the monitoring API. Taller bars mean more observed activity in that run.</p>
                </div>
              </div>
            </header>

            <div v-if="monitoringError" class="mb-4 rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2 text-xs font-medium text-red-400">{{ monitoringError }}</div>

            <div v-if="runTrendBars.length" class="mb-4 grid grid-cols-2 gap-2">
              <div class="rounded-xl border border-surface-800 bg-surface-800 px-3 py-2">
                <p class="text-[10px] uppercase tracking-[0.2em] text-surface-500">Total events</p>
                <p class="mt-1 text-base font-bold text-white">{{ monitoringTrendSummary.totalEvents }}</p>
              </div>
              <div class="rounded-xl border border-surface-800 bg-surface-800 px-3 py-2">
                <p class="text-[10px] uppercase tracking-[0.2em] text-surface-500">Avg / run</p>
                <p class="mt-1 text-base font-bold text-white">{{ monitoringTrendSummary.averageEvents }}</p>
              </div>
              <div class="rounded-xl border border-surface-800 bg-surface-800 px-3 py-2">
                <p class="text-[10px] uppercase tracking-[0.2em] text-surface-500">Latest run</p>
                <p class="mt-1 text-base font-bold text-white">{{ monitoringTrendSummary.latestEvents }}</p>
              </div>
              <div class="rounded-xl border border-surface-800 bg-surface-800 px-3 py-2">
                <p class="text-[10px] uppercase tracking-[0.2em] text-surface-500">Trend</p>
                <p class="mt-1 text-base font-bold" :class="monitoringTrendSummary.trendToneClass">
                  {{ monitoringTrendSummary.trendLabel }}
                  <span v-if="monitoringTrendSummary.trendLabel !== 'Stable' && monitoringTrendSummary.trendLabel !== 'No trend'" class="text-xs font-semibold">
                    ({{ monitoringTrendSummary.trendPercent }}%)
                  </span>
                </p>
              </div>
            </div>

            <div v-if="runTrendBars.length" class="mb-4 rounded-xl border border-surface-800 bg-surface-800/70 p-3">
              <div class="mb-2 flex items-center justify-between text-[10px] uppercase tracking-[0.2em] text-surface-500">
                <span>Event intensity curve</span>
                <span>Peak {{ monitoringTrendSummary.peakLabel }} • {{ monitoringTrendSummary.peakValue }}</span>
              </div>
              <svg viewBox="0 0 100 36" preserveAspectRatio="none" class="h-14 w-full">
                <polyline
                  :points="runTrendLinePoints"
                  fill="none"
                  stroke="rgb(94 234 212)"
                  stroke-width="1.8"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </div>

            <div v-if="runTrendBars.length" class="flex h-44 items-end justify-between gap-2">
              <div v-for="bar in runTrendBars" :key="bar.id" class="group flex flex-1 flex-col items-center gap-2" :title="`${bar.fullDate}: ${bar.value} events`">
                <div class="flex w-full flex-1 items-end justify-center">
                  <div class="relative w-8 rounded-t-lg transition-all duration-700 group-hover:opacity-90" :class="bar.toneClass" :style="{ height: bar.height }">
                    <span class="absolute -top-6 left-1/2 -translate-x-1/2 text-[10px] font-semibold text-surface-300">{{ bar.value }}</span>
                  </div>
                </div>
                <span class="text-[10px] font-semibold uppercase tracking-[0.2em] text-surface-500">{{ bar.label }}</span>
              </div>
            </div>

            <div v-else class="flex h-52 items-center justify-center rounded-xl border border-dashed border-surface-800 bg-surface-800 text-sm text-surface-500">No monitoring runs yet.</div>
          </article>

          <article class="rounded-2xl border border-surface-800 bg-surface-900 p-6 shadow-sm xl:col-span-2">
            <header class="mb-5 flex items-center justify-between gap-4">
              <div class="space-y-1">
                <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Project Streams</p>
                <h2 class="text-lg font-bold text-white">Live progress tracking</h2>
              </div>
              <div v-if="projectsError" class="rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2 text-xs font-medium text-red-400">{{ projectsError }}</div>
            </header>

            <div class="space-y-3 overflow-auto pr-1 custom-scrollbar">
              <div v-for="project in projectRows" :key="project.id" class="rounded-2xl border border-surface-700 bg-surface-800 p-4 transition hover:border-surface-600 hover:bg-surface-700">
                <div class="mb-3 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                  <div class="space-y-1">
                    <div class="flex flex-wrap items-center gap-2">
                      <h3 class="text-sm font-semibold text-white">{{ project.name }}</h3>
                      <span
                        :class="[
                          'rounded-full px-2.5 py-0.5 text-[10px] font-medium uppercase tracking-wider border',
                          project.health === 'On track' ? 'bg-green-500/15 text-green-400 border-green-500/30' : project.health === 'Delayed' ? 'bg-amber-500/15 text-amber-400 border-amber-500/30' : 'bg-red-500/15 text-red-400 border-red-500/30'
                        ]"
                      >
                        {{ project.statusLabel }}
                      </span>
                    </div>
                    <p class="text-xs text-surface-500">{{ project.subtitle }}</p>
                  </div>
                  <div class="text-right">
                    <div class="text-2xl font-black tracking-tight text-white">{{ project.progress }}%</div>
                    <p class="text-[10px] uppercase tracking-[0.2em] text-surface-500">Progress</p>
                  </div>
                </div>
                <div class="mb-2 h-2 rounded-full bg-surface-700">
                  <div class="h-2 rounded-full bg-sage-500 transition-all duration-700" :style="{ width: `${project.progress}%` }" />
                </div>
                <div class="flex items-center justify-between text-xs text-surface-500">
                  <span>{{ project.subtitle }}</span>
                  <span>{{ project.health }}</span>
                </div>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section>
        <h2 class="mb-4 text-xl font-bold text-white">Tactical Insights</h2>
        <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <article class="rounded-2xl border border-surface-800 bg-surface-900 p-6 shadow-sm">
            <header class="mb-5 flex items-center gap-3">
              <Clock :size="18" class="text-red-400" />
              <div>
                <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Overdue Tickets</p>
                <h2 class="text-lg font-bold text-white">Action required</h2>
              </div>
            </header>

            <div class="space-y-3">
              <div v-if="filteredOverdueTickets.length === 0" class="rounded-xl border border-dashed border-surface-800 bg-surface-800 px-4 py-10 text-center text-sm italic text-surface-500">No overdue tickets detected.</div>
              <div v-for="ticket in filteredOverdueTickets.slice(0, 5)" :key="ticket.issue_id" class="flex items-start justify-between gap-4 rounded-xl border-l-4 border-red-500 bg-surface-800 px-4 py-4 shadow-sm transition hover:bg-surface-700">
                <div class="min-w-0 flex-1">
                  <div class="mb-1 flex items-center gap-2">
                    <span class="font-mono text-sm font-semibold text-white">#{{ ticket.issue_id }}</span>
                    <span class="text-sm font-medium text-surface-200">{{ ticket.subject }}</span>
                  </div>
                  <div class="flex flex-wrap items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-surface-500">
                    <span class="text-sage-400">{{ ticket.project_name }}</span>
                    <span>•</span>
                    <span class="text-red-400">Due {{ ticket.due_date }}</span>
                  </div>
                </div>
                <a :href="ticket.url" target="_blank" class="mt-0.5 inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-surface-700 bg-surface-800 text-surface-400 transition hover:border-surface-600 hover:text-surface-200">
                  <ChevronRight :size="16" />
                </a>
              </div>
            </div>
          </article>

          <article class="rounded-2xl border border-surface-800 bg-surface-900 p-6 shadow-sm">
            <header class="mb-5 flex items-center gap-3">
              <AlertTriangle :size="18" class="text-red-400" />
              <div>
                <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Project Risks</p>
                <h2 class="text-lg font-bold text-white">Recommended mitigation</h2>
              </div>
            </header>

            <div class="space-y-3">
              <div v-if="filteredAtRiskProjects.length === 0" class="rounded-xl border border-dashed border-surface-800 bg-surface-800 px-4 py-10 text-center text-sm italic text-surface-500">All projects within safe parameters.</div>
              <div v-for="project in filteredAtRiskProjects.slice(0, 5)" :key="project.project_id" class="rounded-xl border border-red-500/30 bg-red-500/10 p-4 shadow-sm transition hover:bg-red-500/15">
                <div class="flex items-start justify-between gap-4">
                  <div class="min-w-0 flex-1">
                    <h3 class="text-sm font-semibold text-white">{{ project.project_name }}</h3>
                    <p class="mt-1 text-sm leading-relaxed text-red-300">{{ project.reason }}</p>
                    <span class="mt-3 inline-flex rounded-full border border-red-500/40 bg-red-500/10 px-2.5 py-0.5 text-[10px] font-medium uppercase tracking-wider text-red-400">Action: {{ project.recommended_action }}</span>
                  </div>
                  <a :href="project.url" target="_blank" class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-red-500/30 bg-red-500/10 text-red-400 transition hover:border-red-500/50 hover:bg-red-500/20">
                    <ChevronRight :size="16" />
                  </a>
                </div>
              </div>
            </div>
          </article>
        </div>
      </section>
    </div>
  </main>
  <DashboardPdfPreview v-if="showPdfPreview" @close="showPdfPreview = false" />
</template>

<style>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgb(var(--surface-700));
  border-radius: 9999px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgb(var(--surface-600));
}
</style>

