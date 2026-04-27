<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { adminApi } from "../../api/admin";
import type { PmCandidate } from "../../types";

const props = defineProps<{
  role: "admin" | "project_manager";
  token: string;
}>();

interface ProjectStatus {
  id: string;
  name: string;
  owner: string;
  progress: number;
  health: "On track" | "At risk" | "Delayed";
  completionEta: string;
}

const projects = ref<ProjectStatus[]>([
  {
    id: "proj-01",
    name: "E-commerce Revamp",
    owner: "Nadia F.",
    progress: 72,
    health: "On track",
    completionEta: "May 10",
  },
  {
    id: "proj-02",
    name: "Customer Portal",
    owner: "Amine B.",
    progress: 54,
    health: "At risk",
    completionEta: "May 28",
  },
  {
    id: "proj-03",
    name: "Billing Automation",
    owner: "Sara M.",
    progress: 88,
    health: "On track",
    completionEta: "Apr 30",
  },
  {
    id: "proj-04",
    name: "Search Optimization",
    owner: "Yassine H.",
    progress: 31,
    health: "Delayed",
    completionEta: "Jun 15",
  },
]);

const totalProjects = computed(() => projects.value.length);
const avgProgress = computed(() => {
  if (!projects.value.length) return 0;
  const sum = projects.value.reduce((acc, item) => acc + item.progress, 0);
  return Math.round(sum / projects.value.length);
});
const atRiskCount = computed(() =>
  projects.value.filter((item) => item.health === "At risk" || item.health === "Delayed").length,
);
const completedSoon = computed(() => projects.value.filter((item) => item.progress >= 80).length);

const weeklyVelocity = [18, 22, 19, 27, 24, 29, 31];
const velocityBars = computed(() => {
  const max = Math.max(...weeklyVelocity, 1);
  return weeklyVelocity.map((value, index) => ({
    label: `W${index + 1}`,
    value,
    height: `${Math.max(16, Math.round((value / max) * 100))}%`,
  }));
});

const roleLabel = computed(() =>
  props.role === "admin" ? "Admin overview" : "Project manager overview",
);

const isAdmin = computed(() => props.role === "admin");

const syncedCount = ref<number | null>(null);
const isRefreshingPm = ref(false);
const rowLoading = ref<Record<number, boolean>>({});
const pmRows = ref<PmCandidate[]>([]);
const pmError = ref("");
const pmSuccess = ref("");

const enabledPmCount = computed(() => pmRows.value.filter((item) => item.enabled).length);

function setRowLoading(redmineUserId: number, loading: boolean) {
  rowLoading.value = {
    ...rowLoading.value,
    [redmineUserId]: loading,
  };
}

async function loadPmRows() {
  if (!isAdmin.value) return;
  if (!props.token.trim()) {
    pmError.value = "Missing authentication token.";
    return;
  }

  const response = await adminApi.listPmCandidates(props.token.trim());
  pmRows.value = response.items;
}

async function refreshPmFromRedmine() {
  if (!isAdmin.value) return;
  if (!props.token.trim()) {
    pmError.value = "Missing authentication token.";
    return;
  }

  pmError.value = "";
  pmSuccess.value = "";
  isRefreshingPm.value = true;

  try {
    const sync = await adminApi.syncProjectManagers(props.token.trim());
    syncedCount.value = sync.synced_count;
    await loadPmRows();
    pmSuccess.value = `Synced ${sync.synced_count} PM(s) from Redmine.`;
  } catch (error) {
    pmError.value = error instanceof Error ? error.message : "Failed to refresh PM list.";
  } finally {
    isRefreshingPm.value = false;
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
  if (!isAdmin.value) return;
  await refreshPmFromRedmine();
});

function healthClass(health: ProjectStatus["health"]) {
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
      <article class="card stat-card">
        <p class="label">Total projects</p>
        <strong>{{ totalProjects }}</strong>
      </article>
      <article class="card stat-card">
        <p class="label">Average progress</p>
        <strong>{{ avgProgress }}%</strong>
      </article>
      <article class="card stat-card">
        <p class="label">At risk / delayed</p>
        <strong>{{ atRiskCount }}</strong>
      </article>
      <article class="card stat-card">
        <p class="label">Near completion</p>
        <strong>{{ completedSoon }}</strong>
      </article>
    </section>

    <section class="content-grid">
      <article class="card chart-card">
        <header class="card-head">
          <h2>Weekly delivery velocity</h2>
          <span class="caption">Story points completed</span>
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

        <ul class="project-list">
          <li v-for="project in projects" :key="project.id" class="project-row">
            <div class="project-meta">
              <p class="project-name">{{ project.name }}</p>
              <p class="project-sub">Owner: {{ project.owner }} • ETA: {{ project.completionEta }}</p>
            </div>
            <div class="project-progress">
              <span class="health-pill" :class="healthClass(project.health)">{{ project.health }}</span>
              <span class="progress-label">{{ project.progress }}%</span>
            </div>
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: `${project.progress}%` }" />
            </div>
          </li>
        </ul>
      </article>
    </section>

    <section v-if="isAdmin" class="admin-access card">
      <header class="card-head">
        <h2>Project manager access</h2>
        <button class="secondary-btn" type="button" :disabled="isRefreshingPm" @click="refreshPmFromRedmine">
          {{ isRefreshingPm ? "Refreshing..." : "Refresh from Redmine" }}
        </button>
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
          <strong>{{ syncedCount ?? "—" }}</strong>
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
              <th>Projects</th>
              <th>Credentials</th>
              <th>Access status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="pmRows.length === 0">
              <td colspan="7" class="empty-cell">No PM found yet. Click “Refresh from Redmine”.</td>
            </tr>
            <tr v-for="pm in pmRows" :key="pm.redmine_user_id">
              <td>{{ pm.redmine_user_id }}</td>
              <td>{{ pm.full_name }}</td>
              <td>{{ pm.email }}</td>
              <td>
                <span v-if="pm.managed_projects && pm.managed_projects.length > 0">
                  {{ pm.managed_projects.join(", ") }}
                </span>
                <span v-else class="empty-cell">—</span>
              </td>
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

.stat-card strong {
  display: block;
  margin-top: var(--space-sm);
  font-size: var(--text-2xl);
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

.health-pill {
  font-size: var(--text-xs);
  padding: 0.2rem 0.45rem;
  border-radius: 999px;
  border: 1px solid var(--border-subtle);
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
