<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import type { PmCandidate } from '@redsage/ui-core/types';
import { adminApi } from "@redsage/api-client/admin";
import { CheckCircle } from 'lucide-vue-next';

const props = defineProps<{
  role: "admin" | "project_manager";
  token: string;
}>();

const isAdmin = computed(() => props.role === "admin");
const rowLoading = ref<Record<number, boolean>>({});
const lastPmRefreshAt = ref<string>("");
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
        ? { ...row, enabled, projects_name: result.projects_name }
        : row,
    );

    if (enabled && !pm.in_platform) {
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
  <main class="min-h-screen bg-surface-950 px-6 py-8">
    <section v-if="isAdmin" class="mx-auto max-w-7xl space-y-6">
    <section class="rounded-2xl border border-surface-800 bg-surface-900 p-6 shadow-sm">
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
          <!-- <article class="rounded-2xl border border-surface-800 bg-surface-800 p-4">
            <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Ready</p>
            <div class="mt-2 text-3xl font-black tracking-tight text-white">{{ pmRows.filter((r) => r.credentials_ready).length }}</div>
          </article> -->
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
                <th class="px-6 py-4 text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Project Manager</th>
                <th class="px-6 py-4 text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500">Project</th>
                <th class="px-6 py-4 text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500 text-center">Status</th>
                <th class="px-6 py-4 text-[10px] font-semibold uppercase tracking-[0.24em] text-surface-500 text-right">Action</th>
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
                  <div v-if="pm.projects_name && pm.projects_name.length" class="flex flex-wrap gap-2">
                    <span
                      v-for="(proj, idx) in pm.projects_name"
                      :key="`${pm.redmine_user_id}-proj-${idx}`"
                      class="inline-flex rounded-full border px-2.5 py-0.5 text-sm font-medium uppercase tracking-wider border-copper-500/30 bg-copper-500/10 text-copper-400 max-w-[220px] truncate"
                      :title="proj"
                    >
                      {{ typeof proj === 'string' && proj.length > 28 ? proj.slice(0, 25) + '…' : proj }}
                    </span>
                  </div>
                  <div v-else class="text-surface-500">—</div>
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
    </section>
    <section v-else class="mx-auto max-w-7xl rounded-2xl border border-surface-800 bg-surface-900 p-8 text-center">
      <p class="text-sm text-surface-400">You do not have permission to access this page.</p>
    </section>
  </main>
</template>