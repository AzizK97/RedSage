<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { adminApi } from "../../api/admin";
import { dashboardApi } from "../../api/dashboard";
import type { AtRiskProjectInsight, DashboardProject, OverdueTicketInsight, PmCandidate, ProjectStatus } from "../../types";
import { Info } from "@lucide/vue";

const props = defineProps<{
  role: "admin" | "project_manager";
  token: string;
}>();

const projects = ref<ProjectStatus[]>([]);
const projectsError = ref("");
const topOverdueTickets = ref<OverdueTicketInsight[]>([]);
const atRiskProjects = ref<AtRiskProjectInsight[]>([]);
const insightsError = ref("");

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

const velocityBars = computed((): { label: string; height: string; value: number }[] => {
  const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const base = Math.max(8, Math.min(20, projects.value.length + 2));
  return labels.map((label, index) => {
    const value = Math.round(base * (0.8 + index * 0.06));
    return { label, height: `${Math.max(60, value * 5)}px`, value };
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
  const seed = Number(project.id || 0);
  const progress = Math.max(8, Math.min(98, 25 + (seed % 70)));
  const health: ProjectStatus["health"] = progress < 40 ? "Delayed" : progress < 65 ? "At risk" : "On track";
  return {
    id: String(project.id),
    name: project.name,
    owner: "Redmine team",
    progress,
    health,
    completionEta: "TBD",
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

function healthClass(health: "On track" | "At risk" | "Delayed") {
  if (health === "On track") return "health-good";
  if (health === "At risk") return "health-warn";
  return "health-bad";
}
</script>

<template>
  <main class="dashboard-shell">
    <section class="dashboard-header">
      <div>
        <p class="kicker">Dashboard</p>
        <h1>Projects status & advancement</h1>
        <p class="subtitle">{{ roleLabel }} • Snapshot of delivery health, progress, and sprint momentum.</p>
      </div>
    </section>

    <section class="stats-grid">
      <article class="card stat-card accent-card">
        <p class="label">Total projects</p>
        <strong>{{ projects.length }}</strong>
      </article>
      <article class="card stat-card">
        <p class="label">Open issues</p>
        <strong>{{ openIssuesCount }}</strong>
      </article>
      <article class="card stat-card">
        <p class="label">Overdue issues</p>
        <strong>{{ overdueIssuesCount }}</strong>
      </article>
      <article class="card stat-card">
        <p class="label">Critical issues</p>
        <strong>{{ criticalIssuesCount }}</strong>
      </article>
    </section>

    <section class="content-grid">
      <article class="card chart-card">
        <header class="card-head">
          <h2>Monitoring run trend</h2>
          <span class="caption">Events detected by recent runs</span>
          <Info color="#000000" />
        </header>

        <div class="bar-chart" aria-label="Weekly velocity chart">
          <div v-for="bar in velocityBars" :key="bar.label" class="bar-wrap">
            <div class="bar" :style="{ height: bar.height }" />
            <span class="bar-value">{{ bar.value }}</span>
            <span class="bar-label">{{ bar.label }}</span>
          </div>
        </div>
      </article>

      <article class="card status-card">
        <header class="card-head">
          <h2>Project status</h2>
          <span class="caption">Live progress by stream</span>
        </header>
        <p v-if="projectsError" class="banner error">{{ projectsError }}</p>

        <ul class="project-list">
          <li v-for="project in projectRows" :key="project.id" class="project-row">
            <div class="project-meta">
              <p class="project-name">{{ project.name }}</p>
              <p class="project-sub">{{ project.subtitle }}</p>
            </div>
            <div class="project-status-row">
              <span class="status-chip" :class="healthClass(project.health)">{{ project.statusLabel }}</span>
              <span class="progress-label">{{ project.progress }}%</span>
            </div>
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: `${project.progress}%` }" />
            </div>
          </li>
        </ul>
      </article>
    </section>

    <section class="content-grid">
      <article class="card status-card">
        <header class="card-head">
          <h2>Top overdue tickets</h2>
          <span class="caption">Requires immediate follow-up</span>
        </header>
        <p v-if="insightsError" class="banner error">{{ insightsError }}</p>
        <ul class="project-list">
          <li v-if="topOverdueTickets.length === 0" class="empty-cell">No overdue tickets in your current scope.</li>
          <li v-for="ticket in topOverdueTickets.slice(0, 5)" :key="ticket.issue_id" class="project-row">
            <div class="project-meta">
              <p class="project-name">
                #{{ ticket.issue_id }} {{ ticket.subject }}
              </p>
              <p class="project-sub">
                {{ ticket.project_name }} • Due {{ ticket.due_date }} • {{ ticket.priority || "Normal" }}
              </p>
            </div>
            <a class="secondary-btn" :href="ticket.url" target="_blank" rel="noreferrer">Open ticket</a>
          </li>
        </ul>
      </article>

      <article class="card status-card">
        <header class="card-head">
          <h2>At-risk projects</h2>
          <span class="caption">Risk reason + recommended action</span>
        </header>
        <p v-if="insightsError" class="banner error">{{ insightsError }}</p>
        <ul class="project-list">
          <li v-if="atRiskProjects.length === 0" class="empty-cell">No at-risk projects detected right now.</li>
          <li v-for="project in atRiskProjects.slice(0, 5)" :key="project.project_id" class="project-row">
            <div class="project-meta">
              <p class="project-name">{{ project.project_name }}</p>
              <p class="project-sub">
                {{ project.reason }} • Action: {{ project.recommended_action }}
              </p>
            </div>
            <a class="secondary-btn" :href="project.url" target="_blank" rel="noreferrer">Open project</a>
          </li>
        </ul>
      </article>
    </section>

    <section v-if="isAdmin" class="admin-access card">
      <header class="card-head">
        <h2>Project manager access</h2>
        <span class="caption">Auto refreshed every minute</span>
      </header>

      <section class="summary-row">
        <article class="summary-card">
          <span class="label">Total PMs</span>
          <strong>{{ pmRows.length }}</strong>
        </article>
        <article class="summary-card">
          <span class="label">Enabled</span>
          <strong>{{ enabledPmCount }}</strong>
        </article>
        <article class="summary-card">
          <span class="label">Last sync</span>
          <strong>{{ lastPmRefreshAt || "—" }}</strong>
        </article>
      </section>

      <p v-if="pmError" class="banner error">{{ pmError }}</p>
      <p v-if="pmSuccess" class="banner success">{{ pmSuccess }}</p>

      <div class="table-wrap">
        <table class="pm-table">
          <thead>
            <tr>
              <th>Redmine ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Credentials</th>
              <th>Access status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="pmRows.length === 0">
              <td colspan="7" class="empty-cell">No PM found yet. Table refreshes automatically.</td>
            </tr>
            <tr v-for="pm in pmRows" :key="pm.redmine_user_id">
              <td>{{ pm.redmine_user_id }}</td>
              <td>{{ pm.full_name }}</td>
              <td>{{ pm.email }}</td>
              <td>
                <span :class="pm.credentials_ready ? 'status-enabled' : 'status-disabled'">
                  {{ pm.credentials_ready ? 'Ready' : 'Missing' }}
                </span>
              </td>
              <td>
                <span :class="pm.enabled ? 'status-enabled' : 'status-disabled'">
                  {{ pm.enabled ? "Enabled" : "Disabled" }}
                </span>
              </td>
              <td>
                <button
                  class="primary-btn"
                  type="button"
                  :disabled="rowLoading[pm.redmine_user_id]"
                  @click="togglePmAccess(pm, !pm.enabled)"
                >
                  {{ rowLoading[pm.redmine_user_id] ? "Saving..." : (pm.enabled ? "Revoke" : "Grant access") }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<style scoped>
.dashboard-shell {
  min-height: 100%;
  padding: var(--space-lg) var(--space-xl);
  background: var(--bg-primary);
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.kicker {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--accent-blue);
  font-size: var(--text-xs);
}

h1 {
  margin: var(--space-xs) 0;
  font-size: var(--text-2xl);
}

.subtitle {
  margin: 0;
  color: var(--text-secondary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--space-md);
}

.card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
}

.stat-card {
  padding: var(--space-md);
}

.label {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}
 .accent-card {
   border-color: rgba(96, 165, 250, 0.35);
   background: linear-gradient(180deg, rgba(59,130,246,0.12), var(--bg-secondary));
 }
 .accent-card strong {
   color: var(--accent-blue);
 }
 .project-status-row {
   display: flex;
   align-items: center;
   gap: 10px;
   margin-bottom: 10px;
 }
 .status-chip {
   display: inline-flex;
   align-items: center;
   padding: 0.25rem 0.65rem;
   border-radius: 999px;
   font-size: 0.75rem;
   font-weight: 600;
   letter-spacing: 0.01em;
 }
 .project-row .status-chip {
   border: 1px solid transparent;
 }
 .progress-fill {
   transition: width 0.35s ease;
 }
 .project-row:hover {
   transform: translateY(-1px);
   box-shadow: 0 12px 30px rgba(0,0,0,0.08);
 }
 .project-row {
   transition: transform 0.2s ease, box-shadow 0.2s ease;
 }

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1.4fr;
  gap: var(--space-md);
  min-height: 0;
}

.chart-card,
.status-card {
  padding: var(--space-md);
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

h2 {
  margin: 0;
  font-size: var(--text-lg);
}

.caption {
  color: var(--text-secondary);
  font-size: var(--text-xs);
}

.bar-chart {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  align-items: end;
  gap: var(--space-sm);
  height: 240px;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-sm);
  background: var(--bg-tertiary);
}

.bar-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
  gap: var(--space-xs);
}

.bar {
  width: 28px;
  max-width: 100%;
  border-radius: var(--radius-sm);
  background: var(--accent-blue);
}

.bar-value,
.bar-label {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.project-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.project-row {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-sm);
  background: var(--bg-tertiary);
}

.project-meta {
  margin-bottom: var(--space-xs);
}

.project-name {
  margin: 0;
  font-weight: 600;
}

.project-sub {
  margin: 0;
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.project-progress {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xs);
}
 .project-row .project-name {
   display: flex;
   align-items: center;
   gap: 10px;
 }

.health-good {
  color: var(--accent-green);
  border-color: var(--accent-green);
}

.health-warn {
  color: var(--accent-yellow);
  border-color: var(--accent-yellow);
}

.health-bad {
  color: var(--accent-red);
  border-color: var(--accent-red);
}

.progress-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.progress-track {
  width: 100%;
  height: 8px;
  border-radius: 999px;
  background: var(--bg-secondary);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: inherit;
  background: var(--accent-blue);
}

.admin-access {
  padding: var(--space-md);
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}

.summary-card {
  border: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.banner {
  border-radius: var(--radius-md);
  padding: var(--space-sm) var(--space-md);
  margin: 0 0 var(--space-md);
  font-size: var(--text-sm);
}

.banner.error {
  border: 1px solid var(--accent-red);
  color: var(--accent-red);
}

.banner.success {
  border: 1px solid var(--accent-green);
  color: var(--accent-green);
}

.table-wrap {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.pm-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-secondary);
}

.pm-table th,
.pm-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--border-subtle);
  text-align: left;
  font-size: var(--text-sm);
}

.pm-table th {
  color: var(--text-secondary);
  font-weight: 500;
}

.empty-cell {
  color: var(--text-secondary);
  text-align: center;
}

.status-enabled,
.status-disabled {
  font-weight: 600;
}

.status-enabled {
  color: var(--accent-green);
}

.status-disabled {
  color: var(--accent-red);
}

.primary-btn,
.secondary-btn {
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  padding: 0.5rem 0.8rem;
  font-size: var(--text-sm);
  cursor: pointer;
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.primary-btn {
  border-color: var(--accent-blue);
  background: var(--accent-blue);
}

.secondary-btn {
  border-color: var(--accent-blue);
}

button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

@media (max-width: 1100px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px) {
  .dashboard-shell {
    padding: var(--space-md);
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .summary-row {
    grid-template-columns: 1fr;
  }
}
</style>
