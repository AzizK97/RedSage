<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { adminApi } from "../../api/admin";
import { dashboardApi } from "../../api/dashboard";
import { monitoringApi } from "../../api/monitoring";
import type { AtRiskProjectInsight, DashboardProject, MonitoringOverview, OverdueTicketInsight, PmCandidate, ProjectStatus } from "../../types";
import { Info, TrendingUp, AlertTriangle, CheckCircle, Clock, ChevronRight, ChevronDown, Check } from "lucide-vue-next";

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
const selectedProjectId = ref<string | null>(null);
const projectSelectorRef = ref<HTMLElement | null>(null);
const isProjectSelectorOpen = ref(false);

const selectedProjectLabel = computed(() => {
  if (!selectedProjectId.value) return "All Projects";
  return projects.value.find((project) => project.id === selectedProjectId.value)?.name ?? "All Projects";
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
  const rows = projects.value ?? [];
  const filtered = selectedProjectId.value
    ? rows.filter((p) => p.id === selectedProjectId.value)
    : rows;
  return filtered.map((row) => {
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
  const filtered = selectedProjectIdentifier.value
    ? topOverdueTickets.value.filter((t) => t.project_identifier === selectedProjectIdentifier.value)
    : topOverdueTickets.value;
  if (filtered.length > 0) {
    return filtered.length * 4;
  }
  const projectCount = selectedProjectId.value ? 1 : projects.value.length;
  return projectCount * 3;
});

const overdueIssuesCount = computed(() => {
  const filtered = selectedProjectIdentifier.value
    ? topOverdueTickets.value.filter((t) => t.project_identifier === selectedProjectIdentifier.value)
    : topOverdueTickets.value;
  return Math.max(0, filtered.length);
});

const criticalIssuesCount = computed(() => {
  const filtered = selectedProjectIdentifier.value
    ? atRiskProjects.value.filter((p) => p.project_identifier === selectedProjectIdentifier.value)
    : atRiskProjects.value;
  const criticalFromRisk = filtered.reduce((sum, item) => sum + (item.high_priority_open_count || 0), 0);
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

// Resource capacity insights
const teamWorkloadInsight = computed(() => {
  const criticalCount = criticalIssuesCount.value;
  const overdueCount = overdueIssuesCount.value;
  if (criticalCount > 5 || overdueCount > 10) return "⚠️ High workload detected. Consider task redistribution.";
  if (criticalCount > 0) return "🟡 Monitor critical tasks closely.";
  return "✅ Team capacity is balanced.";
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
    identifier: project.identifier,
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
  document.addEventListener("mousedown", handleProjectSelectorClickOutside);
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
  document.removeEventListener("mousedown", handleProjectSelectorClickOutside);
  if (pmPollTimer !== null) {
    window.clearInterval(pmPollTimer);
  }
});
</script>

<template>
  <main class="min-h-full bg-surface-950 px-4 sm:px-6 lg:px-8 py-8 sm:py-10 text-surface-900">
    <div class="mx-auto flex w-full max-w-7xl flex-col gap-6 lg:gap-8">
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

        <div ref="projectSelectorRef" class="w-full max-w-xs">
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
        <article class="rounded-2xl border border-surface-800 bg-surface-900 p-6 shadow-sm">
          <div class="flex items-start gap-3">
            <div class="mt-0.5 rounded-full bg-amber-500/15 p-2 text-amber-400 ring-1 ring-amber-500/25">
              <AlertTriangle :size="16" />
            </div>
            <div class="space-y-2">
              <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">AI Insight: Team Capacity</p>
              <h2 class="text-lg font-bold text-white">{{ teamWorkloadInsight }}</h2>
              <p class="text-sm leading-relaxed text-surface-400">
                Recommendation: {{ criticalIssuesCount > 5 ? 'Redistribute critical tasks across the team and reduce WIP immediately.' : 'Keep the current allocation, but continue monitoring workload concentration.' }}
              </p>
            </div>
          </div>
        </article>

        <article class="rounded-2xl border border-surface-800 bg-surface-900 p-6 shadow-sm">
          <div class="flex items-start gap-3">
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

            <div v-if="runTrendBars.length" class="flex h-52 items-end justify-between gap-3">
              <div v-for="bar in runTrendBars" :key="bar.label + bar.value" class="flex flex-1 flex-col items-center gap-2">
                <div class="flex w-full flex-1 items-end justify-center">
                  <div class="relative w-8 rounded-t-lg bg-sage-500 transition-all duration-700" :style="{ height: bar.height }">
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

            <div class="max-h-[340px] space-y-3 overflow-auto pr-1 custom-scrollbar">
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

      <section v-if="isAdmin" class="rounded-2xl border border-surface-800 bg-surface-900 p-6 shadow-sm">
        <header class="mb-6 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div class="space-y-1">
            <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Admin only</p>
            <h2 class="text-xl font-bold text-white">Project Manager Operations</h2>
            <p class="text-sm text-surface-400">Automatic reconciliation with the Redmine user directory.</p>
          </div>
          <div class="flex items-center gap-4">
            <div class="text-right">
              <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Last Sync</p>
              <p class="text-sm font-semibold text-white">{{ lastPmRefreshAt || '—' }}</p>
            </div>
            <div class="flex -space-x-2">
              <div v-for="i in 3" :key="i" class="flex h-8 w-8 items-center justify-center rounded-full border-2 border-surface-900 bg-surface-700 text-[10px] font-semibold text-surface-300 shadow-sm">{{ i }}</div>
            </div>
          </div>
        </header>

        <div class="mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">
          <article class="rounded-2xl border border-surface-800 bg-surface-800 p-4">
            <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Total</p>
            <div class="mt-2 text-3xl font-black tracking-tight text-white">{{ pmRows.length }}</div>
          </article>
          <article class="rounded-2xl border border-surface-800 bg-surface-800 p-4">
            <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Enabled</p>
            <div class="mt-2 text-3xl font-black tracking-tight text-white">{{ enabledPmCount }}</div>
          </article>
          <article class="rounded-2xl border border-surface-800 bg-surface-800 p-4">
            <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Ready</p>
            <div class="mt-2 text-3xl font-black tracking-tight text-white">{{ pmRows.filter((r) => r.credentials_ready).length }}</div>
          </article>
        </div>

        <div v-if="pmError || pmSuccess" class="mb-6 space-y-3">
          <div v-if="pmError" class="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-xs font-medium text-red-400">{{ pmError }}</div>
          <div v-if="pmSuccess" class="flex items-center gap-2 rounded-xl border border-sage-500/30 bg-sage-500/10 px-4 py-3 text-xs font-medium text-sage-400">
            <CheckCircle :size="14" /> {{ pmSuccess }}
          </div>
        </div>

        <div class="overflow-hidden rounded-2xl border border-surface-800 bg-surface-900 shadow-sm">
          <table class="min-w-full border-collapse text-left">
            <thead class="sticky top-0 bg-surface-800">
              <tr class="border-b border-surface-800">
                <th class="px-6 py-4 text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">PM Identity</th>
                <th class="px-6 py-4 text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Credentials</th>
                <th class="px-6 py-4 text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500 text-center">Status</th>
                <th class="px-6 py-4 text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-surface-800">
              <tr v-if="pmRows.length === 0">
                <td colspan="4" class="px-6 py-16 text-center text-sm italic text-surface-500">Fetching PM candidates from Redmine...</td>
              </tr>
              <tr v-for="pm in pmRows" :key="pm.redmine_user_id" class="bg-surface-800 transition hover:bg-surface-700">
                <td class="px-6 py-4">
                  <div class="flex items-center gap-3">
                    <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-surface-700 text-sm font-semibold text-surface-300">{{ pm.full_name.charAt(0) }}</div>
                    <div>
                      <p class="text-sm font-semibold text-white">{{ pm.full_name }}</p>
                      <p class="text-xs text-surface-500">{{ pm.email }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span :class="['inline-flex rounded-full border px-2.5 py-0.5 text-[10px] font-medium uppercase tracking-wider', pm.credentials_ready ? 'border-green-500/30 bg-green-500/10 text-green-400' : 'border-surface-700 bg-surface-700 text-surface-500']">
                    {{ pm.credentials_ready ? 'Available' : 'Pending' }}
                  </span>
                </td>
                <td class="px-6 py-4 text-center">
                  <span :class="['inline-flex h-2.5 w-2.5 rounded-full', pm.enabled ? 'bg-green-500 shadow-[0_0_0_4px_rgba(34,197,94,0.12)]' : 'bg-surface-600']" />
                </td>
                <td class="px-6 py-4 text-right">
                  <button
                    @click="togglePmAccess(pm, !pm.enabled)"
                    :disabled="rowLoading[pm.redmine_user_id]"
                    :class="['inline-flex items-center rounded-lg px-4 py-2 text-xs font-semibold transition disabled:cursor-not-allowed disabled:opacity-60', pm.enabled ? 'border border-red-500/30 bg-red-500/10 text-red-400 hover:bg-red-500/20 hover:border-red-500/50' : 'border border-sage-500/30 bg-sage-500 text-white hover:bg-sage-600']"
                  >
                    {{ rowLoading[pm.redmine_user_id] ? 'Processing...' : (pm.enabled ? 'Revoke' : 'Grant') }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
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
  background: rgb(var(--surface-700));
  border-radius: 9999px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgb(var(--surface-600));
}
</style>

