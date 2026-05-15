<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { adminApi } from "@redsage/api-client/admin";
import type { PmCandidate } from "../../../../ui-core/src/types/index.ts";

const props = defineProps<{
  token: string;
}>();

const emit = defineEmits<{
  (event: "logout"): void;
}>();

const backendName = ref("RedSage API");
const backendVersion = ref("1.0.0");
const syncedCount = ref<number | null>(null);

const isPinging = ref(false);
const isRefreshing = ref(false);
const rowLoading = ref<Record<number, boolean>>({});

const rows = ref<PmCandidate[]>([]);
const errorMessage = ref("");
const successMessage = ref("");

const enabledCount = computed(() => rows.value.filter((item) => item.enabled).length);

function logout() {
  emit("logout");
}

function setRowLoading(redmineUserId: number, loading: boolean) {
  rowLoading.value = {
    ...rowLoading.value,
    [redmineUserId]: loading,
  };
}

async function checkBackend() {
  isPinging.value = true;
  try {
    const info = await adminApi.pingApi();
    backendName.value = info.name;
    backendVersion.value = info.version;
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "Failed to reach backend.";
  } finally {
    isPinging.value = false;
  }
}

async function loadPmRows() {
  if (!props.token.trim()) {
    errorMessage.value = "Missing authentication token.";
    return;
  }

  const response = await adminApi.listPmCandidates(props.token.trim());
  rows.value = response.items;
}

async function refreshFromRedmine() {
  if (!props.token.trim()) {
    errorMessage.value = "Missing authentication token.";
    return;
  }

  errorMessage.value = "";
  successMessage.value = "";
  isRefreshing.value = true;

  try {
    const sync = await adminApi.syncProjectManagers(props.token.trim());
    syncedCount.value = sync.synced_count;
    await loadPmRows();
    successMessage.value = `Synced ${sync.synced_count} PM(s) from Redmine.`;
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "Failed to refresh PM list.";
  } finally {
    isRefreshing.value = false;
  }
}

async function toggleAccess(pm: PmCandidate, enabled: boolean) {
  if (!props.token.trim()) {
    errorMessage.value = "Missing authentication token.";
    return;
  }

  errorMessage.value = "";
  successMessage.value = "";
  setRowLoading(pm.redmine_user_id, true);

  try {
    const result = await adminApi.setPmAccess(props.token.trim(), {
      redmine_user_id: pm.redmine_user_id,
      enabled,
    });

    rows.value = rows.value.map((row) =>
      row.redmine_user_id === pm.redmine_user_id
        ? { ...row, enabled, credentials_ready: row.credentials_ready || result.generated_account }
        : row,
    );

    if (enabled && result.generated_account) {
      successMessage.value = `${result.full_name} enabled and account provisioned with Redmine profile.`;
    } else if (enabled) {
      successMessage.value = `${result.full_name} enabled. Existing platform account reused.`;
    } else {
      successMessage.value = `${pm.full_name} is now disabled.`;
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "Failed to update access.";
  } finally {
    setRowLoading(pm.redmine_user_id, false);
  }
}

onMounted(async () => {
  await checkBackend();
  await refreshFromRedmine();
});
</script>

<template>
  <main class="admin-shell">
    <section class="admin-header">
      <div>
        <p class="kicker">Admin</p>
        <h1>Project manager access</h1>
        <p class="subtitle">View all PMs synced from Redmine and grant or revoke platform access.</p>
      </div>

      <div class="header-actions">
        <button class="ghost-btn" type="button" :disabled="isPinging" @click="checkBackend">
          {{ isPinging ? "Checking..." : `${backendName} ${backendVersion}` }}
        </button>
        <button class="secondary-btn" type="button" :disabled="isRefreshing" @click="refreshFromRedmine">
          {{ isRefreshing ? "Refreshing..." : "Refresh from Redmine" }}
        </button>
        <button class="ghost-btn" type="button" @click="logout">Log out</button>
      </div>
    </section>

    <section class="summary-row">
      <article class="summary-card">
        <span class="label">Total PMs</span>
        <strong>{{ rows.length }}</strong>
      </article>
      <article class="summary-card">
        <span class="label">Enabled</span>
        <strong>{{ enabledCount }}</strong>
      </article>
      <article class="summary-card">
        <span class="label">Last sync</span>
        <strong>{{ syncedCount ?? "—" }}</strong>
      </article>
    </section>

    <p v-if="errorMessage" class="banner error">{{ errorMessage }}</p>
    <p v-if="successMessage" class="banner success">{{ successMessage }}</p>

    <section class="table-wrap">
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
          <tr v-if="rows.length === 0">
            <td colspan="6" class="empty-cell">No PM found yet. Click “Refresh from Redmine”.</td>
          </tr>
          <tr v-for="pm in rows" :key="pm.redmine_user_id">
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
                @click="toggleAccess(pm, !pm.enabled)"
              >
                {{ rowLoading[pm.redmine_user_id] ? "Saving..." : (pm.enabled ? "Revoke" : "Grant access") }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </main>
</template>

<style scoped>
.admin-shell {
  min-height: 100vh;
  padding: var(--space-xl);
  background: var(--bg-primary);
  color: var(--text-primary);
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-lg);
  margin-bottom: var(--space-lg);
}

.kicker {
  margin: 0;
  font-size: var(--text-xs);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent-blue);
}

h1 {
  margin: var(--space-xs) 0;
  font-size: var(--text-2xl);
}

.subtitle {
  margin: 0;
  color: var(--text-secondary);
}

.header-actions {
  display: flex;
  gap: var(--space-sm);
  flex-wrap: wrap;
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

.label {
  color: var(--text-secondary);
  font-size: var(--text-sm);
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
.secondary-btn,
.ghost-btn {
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

@media (max-width: 960px) {
  .admin-shell {
    padding: var(--space-md);
  }

  .admin-header {
    flex-direction: column;
  }

  .summary-row {
    grid-template-columns: 1fr;
  }

  .table-wrap {
    overflow-x: auto;
  }
}
</style>
