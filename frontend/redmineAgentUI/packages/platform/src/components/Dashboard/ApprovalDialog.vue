<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { AlertTriangle, Check, X, Edit3 } from "lucide-vue-next";
import { redmineApi, type RedmineOption } from "@redsage/api-client/redmine";

const props = defineProps<{
  token: string;
  interrupt: Record<string, any> | null;
  disabled: boolean;
  inline?: boolean;
}>();

const emit = defineEmits<{
  (e: "approve"): void;
  (e: "reject", message: string): void;
  (e: "edit", payload: { name: string; args: Record<string, any> }): void;
}>();

const rejectMessage = ref("Rejected by user");
const actionName = ref("");
const actionDescription = ref("");
const editableArgs = ref<Record<string, string>>({});
const originalArgs = ref<Record<string, any>>({});
const schemaProperties = ref<Record<string, any>>({});
const redmineBaseUrl = ref("");
const trackers = ref<RedmineOption[]>([]);
const issueStatuses = ref<RedmineOption[]>([]);
const issuePriorities = ref<RedmineOption[]>([]);
const projectVersions = ref<RedmineOption[]>([]);
const projectMembers = ref<RedmineOption[]>([]);
const versionStatuses = ref<RedmineOption[]>([]);
const issueSummary = ref<{
  id: string;
  subject: string;
  assigned_to_name: string;
  assigned_to_id?: string | number | null;
  project_name?: string;
  project_identifier?: string;
} | null>(null);
const metadataLoading = ref(false);
const defaultFieldValues: Record<string, string> = {
  status_id: "1",
  priority_id: "4",
  status: "open",
};

const actionFieldOrders: Record<string, string[]> = {
  create_issue: [
    "tracker_id",
    "subject",
    "description",
    "status_id",
    "priority_id",
    "assigned_to_id",
    "project_id",
    "version_id",
    "start_date",
    "due_date",
  ],
  update_issue_status: ["issue_id", "status_id", "notes"],
  reassign_issue: ["issue_id", "assigned_to_id", "notes"],
  add_comment_to_issue: ["issue_id", "comment"],
  update_issue_dates: ["issue_id", "due_date", "start_date"],
  create_version: ["project_id", "name", "due_date", "description", "status"],
  update_version_dates: ["version_id", "due_date", "name", "status", "description"],
  log_time: ["issue_id", "hours", "activity_id", "comments", "spent_on"],
};

const selectFieldKeys = new Set(["tracker_id", "status_id", "priority_id", "assigned_to_id", "version_id", "status"]);

function normalizeSchemaProperties(schema: Record<string, any> | null | undefined): Record<string, any> {
  const properties = schema?.properties;
  return properties && typeof properties === "object" && !Array.isArray(properties) ? properties : {};
}

function normalizeArgs(args: Record<string, any>) {
  const normalized = { ...args };
  if (normalized.tracker !== undefined && normalized.tracker_id === undefined) normalized.tracker_id = normalized.tracker;
  if (normalized.status !== undefined && normalized.status_id === undefined) normalized.status_id = normalized.status;
  if (normalized.priority !== undefined && normalized.priority_id === undefined) normalized.priority_id = normalized.priority;
  if (normalized.assignee !== undefined && normalized.assigned_to_id === undefined) normalized.assigned_to_id = normalized.assignee;
  return normalized;
}

function hasInterruptPayload(interrupt: Record<string, any> | null) {
  if (!interrupt) return false;
  if (Array.isArray(interrupt)) return interrupt.length > 0;
  return Object.keys(interrupt).length > 0;
}

function extractProjectIdentifier(args: Record<string, any>) {
  const candidate = args.project_id ?? args.project_identifier ?? args.project ?? "";
  return typeof candidate === "string" ? candidate.trim() : "";
}

function extractIssueId(args: Record<string, any>) {
  const candidate = args.issue_id ?? args.id ?? args.issue ?? "";
  return candidate === null || candidate === undefined ? "" : String(candidate).trim();
}

function extractEditableAction(interrupt: Record<string, any> | null) {
  if (!interrupt) return null;

  const actionRequests = Array.isArray(interrupt.action_requests)
    ? interrupt.action_requests
    : [];

  const reviewConfigs = Array.isArray(interrupt.review_configs)
    ? interrupt.review_configs
    : [];

  const firstAction = actionRequests[0] ?? interrupt.action_request ?? interrupt;
  const firstReview = reviewConfigs[0] ?? interrupt.review_config ?? null;

  const name =
    firstAction?.name ??
    firstAction?.action?.name ??
    firstAction?.tool?.name ??
    "";

  const args =
    firstAction?.args ??
    firstAction?.action?.args ??
    firstAction?.tool?.args ??
    firstAction?.action_input ??
    {};
  const description =
    firstAction?.description ??
    firstReview?.description ??
    "";

  const schema = normalizeSchemaProperties(firstReview?.args_schema ?? firstAction?.args_schema ?? null);

  if (!name || typeof name !== "string") return null;

  return {
    name: name.trim(),
    description: typeof description === "string" ? description.trim() : "",
    args: args && typeof args === "object" && !Array.isArray(args) ? normalizeArgs(args) : {},
    schema,
  };
}

function stringifyArg(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") {
    try {
      return JSON.stringify(value, null, 2);
    } catch {
      return String(value);
    }
  }
  return String(value);
}

function labelize(key: string): string {
  const labels: Record<string, string> = {
    tracker_id: "Tracker",
    status_id: "Status",
    priority_id: "Priority",
    assigned_to_id: "Assignee",
    project_id: "Project",
    version_id: "Version",
    issue_id: "Issue",
    activity_id: "Activity",
    hours: "Hours",
    spent_on: "Spent On",
  };

  if (labels[key]) return labels[key];

  return key
    .replace(/_/g, " ")
    .replace(/\bId\b/g, "")
    .replace(/\b\w/g, (m) => m.toUpperCase());
}

function isStructuredArg(key: string): boolean {
  const value = originalArgs.value[key];
  return Array.isArray(value) || (typeof value === "object" && value !== null);
}

function argPlaceholder(key: string): string {
  const value = originalArgs.value[key];
  if (typeof value === "number") return "Enter a number";
  if (typeof value === "boolean") return "true or false";
  if (isStructuredArg(key)) return "Enter valid JSON";
  return "Enter value";
}

function parseEditedValue(raw: string, original: unknown): unknown {
  const trimmed = raw.trim();
  if (Array.isArray(original) || (typeof original === "object" && original !== null)) {
    return JSON.parse(trimmed || "{}");
  }
  if (typeof original === "number") {
    const parsed = Number(trimmed);
    if (Number.isNaN(parsed)) throw new Error("Invalid number");
    return parsed;
  }
  if (typeof original === "boolean") {
    return ["true", "1", "yes", "on"].includes(trimmed.toLowerCase());
  }
  if (original === null && trimmed === "") {
    return null;
  }
  return raw;
}

function getPreferredFieldOrder(actionName: string): string[] {
  if (Object.keys(schemaProperties.value).length > 0) {
    return Object.keys(schemaProperties.value);
  }

  return actionFieldOrders[actionName] || Object.keys(originalArgs.value);
}

function buildArgOrder(args: Record<string, any>, preferredOrder: string[]): string[] {
  const remaining = Object.keys(args).filter((key) => !preferredOrder.includes(key));
  return [
    ...preferredOrder,
    ...remaining,
  ];
}

function getFieldOptions(key: string): RedmineOption[] {
  if (key === "tracker_id") return trackers.value;
  if (key === "status_id") {
    return actionName.value.startsWith("create_version") || actionName.value.startsWith("update_version")
      ? versionStatuses.value
      : issueStatuses.value;
  }
  if (key === "priority_id") return issuePriorities.value;
  if (key === "version_id") return projectVersions.value;
  if (key === "assigned_to_id") return projectMembers.value;
  if (key === "status") return versionStatuses.value;
  return [];
}

function isSelectField(key: string): boolean {
  return selectFieldKeys.has(key) && getFieldOptions(key).length > 0;
}

function normalizeSelectedValue(key: string, value: unknown): string {
  if (value === null || value === undefined) return "";
  if (isSelectField(key)) return String(value);
  return stringifyArg(value);
}

const visible = computed(() => hasInterruptPayload(props.interrupt));
const preferredFieldOrder = computed(() => getPreferredFieldOrder(actionName.value));
const argOrder = computed(() => buildArgOrder(originalArgs.value, preferredFieldOrder.value));

async function loadMetadata() {
  if (!props.token) return;
  metadataLoading.value = true;
  try {
    const projectIdentifier = extractProjectIdentifier(originalArgs.value);
    const issueId = extractIssueId(originalArgs.value);
    const metadata = await redmineApi.getMetadata(props.token, projectIdentifier || undefined, issueId || undefined);
    redmineBaseUrl.value = metadata.base_url;
    trackers.value = metadata.trackers || [];
    issueStatuses.value = metadata.issue_statuses || [];
    issuePriorities.value = metadata.issue_priorities || [];
    versionStatuses.value = metadata.version_statuses || [];
    projectVersions.value = metadata.project_versions || [];
    projectMembers.value = metadata.project_members || [];
    issueSummary.value = metadata.issue_summary || null;
  } catch {
    trackers.value = [];
    issueStatuses.value = [];
    issuePriorities.value = [];
    versionStatuses.value = [];
    projectVersions.value = [];
    projectMembers.value = [];
    issueSummary.value = null;
  } finally {
    metadataLoading.value = false;
  }
}

onMounted(() => {
  void loadMetadata();
});

watch(
  () => props.interrupt,
  (nextInterrupt) => {
    const extracted = extractEditableAction(nextInterrupt);
    if (!extracted) {
      actionName.value = "";
      actionDescription.value = "";
      originalArgs.value = {};
      schemaProperties.value = {};
      issueSummary.value = null;
      editableArgs.value = {};
      return;
    }

    actionName.value = extracted.name;
    actionDescription.value = extracted.description;
    originalArgs.value = { ...extracted.args };
    schemaProperties.value = extracted.schema;
    issueSummary.value = null;
    const mapped: Record<string, string> = {};
    preferredFieldOrder.value.forEach((key) => {
      const raw = extracted.args[key];
      mapped[key] = normalizeSelectedValue(key, raw);
      if (!mapped[key] && defaultFieldValues[key]) {
        mapped[key] = defaultFieldValues[key];
      }
    });
    Object.entries(extracted.args).forEach(([key, value]) => {
      if (!(key in mapped)) {
        mapped[key] = normalizeSelectedValue(key, value);
      }
    });
    editableArgs.value = mapped;
  },
  { immediate: true },
);

watch(
  () => [originalArgs.value.project_id, originalArgs.value.issue_id],
  () => {
    void loadMetadata();
  },
);

watch(
  () => props.token,
  () => {
    void loadMetadata();
  },
);

function approve() {
  emit("approve");
}

function reject() {
  emit("reject", rejectMessage.value || "Rejected by user");
}

function getIssueDisplayText() {
  if (issueSummary.value?.subject) {
    return issueSummary.value.subject;
  }
  if (originalArgs.value.issue_id !== undefined && originalArgs.value.issue_id !== null) {
    return `Issue #${originalArgs.value.issue_id}`;
  }
  return "Issue";
}

function getAssigneeDisplayText() {
  if (issueSummary.value?.assigned_to_name) {
    return issueSummary.value.assigned_to_name;
  }
  if (originalArgs.value.assigned_to_id !== undefined && originalArgs.value.assigned_to_id !== null && String(originalArgs.value.assigned_to_id).trim() !== "") {
    return `User #${originalArgs.value.assigned_to_id}`;
  }
  return "Unassigned";
}

function edit() {
  try {
    const parsedArgs: Record<string, any> = {};
    Object.keys(editableArgs.value).forEach((key) => {
      const raw = editableArgs.value[key] ?? "";
      if (!raw.trim() && !(key in originalArgs.value)) {
        return;
      }
      if (!raw.trim() && (key in originalArgs.value) && originalArgs.value[key] === undefined) {
        return;
      }
      if (isSelectField(key)) {
        if (!raw.trim()) {
          return;
        }
        parsedArgs[key] = raw;
        return;
      }
      parsedArgs[key] = parseEditedValue(raw, originalArgs.value[key]);
    });
    emit("edit", { name: actionName.value.trim(), args: parsedArgs });
  } catch {
    alert("Invalid value in edited fields. Please check JSON/number fields.");
  }
}
</script>

<template>
  <section 
    v-if="visible" 
    :class="[
      'rounded-3xl border shadow-2xl animate-in zoom-in-95 duration-300 overflow-auto custom-scrollbar',
      props.inline
        ? 'w-full p-6 bg-surface-900 border-copper-500/20'
        : 'm-6 p-6 bg-surface-900 border-copper-500/20'
    ]"
  >
    <div class="flex items-center gap-3 mb-6">
      <div class="w-10 h-10 rounded-xl bg-copper-500/20 flex items-center justify-center text-copper-500">
        <AlertTriangle :size="20" />
      </div>
      <div>
        <h3 class="text-sm font-black text-white uppercase tracking-widest">Approval Required</h3>
        <p class="text-xs text-surface-500 font-bold">The agent is requesting permission to execute an action.</p>
        <p v-if="actionDescription" class="mt-2 text-xs text-surface-400 leading-relaxed">
          {{ actionDescription }}
        </p>
      </div>
    </div>

    <div class="space-y-6">
      <!-- <div class="relative group">
        <div class="absolute top-3 left-3 text-surface-700">
          <Terminal :size="14" />
        </div>
        <pre class="w-full max-h-48 overflow-auto bg-black/40 border border-surface-800 p-8 rounded-2xl text-[10px] sm:text-xs font-mono text-surface-400 custom-scrollbar leading-relaxed">{{ interrupt }}</pre>
      </div> -->

      <div class="flex flex-col sm:flex-row gap-3">
        <button 
          :disabled="disabled" 
          @click="approve"
          class="flex-1 h-12 rounded-xl bg-sage-500 hover:bg-sage-400 text-surface-950 font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2 transition-all active:scale-95 disabled:opacity-30"
        >
          <Check :size="16" stroke-width="3" /> Approve Action
        </button>
        <button 
          :disabled="disabled" 
          @click="reject"
          class="flex-1 h-12 rounded-xl bg-surface-800 hover:bg-red-500/10 border border-surface-700 hover:border-red-500/20 text-surface-300 hover:text-red-400 font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2 transition-all active:scale-95 disabled:opacity-30"
        >
          <X :size="16" stroke-width="3" /> Reject
        </button>
      </div>

      <div class="pt-6 border-t border-surface-800/50">
        <div class="flex items-center justify-between gap-2 mb-4 text-surface-500">
          <Edit3 :size="14" />
          <span class="text-[10px] font-black uppercase tracking-widest">Fine-tune parameters</span>
          <span v-if="redmineBaseUrl" class="ml-auto text-[10px] font-medium uppercase tracking-widest text-surface-600 truncate">
            {{ redmineBaseUrl }}
          </span>
        </div>
        
        <div class="grid gap-3">
          <div
            v-for="key in argOrder"
            :key="key"
            class="grid gap-2"
          >
            <label class="text-[10px] font-black uppercase tracking-widest text-surface-500">{{ labelize(key) }}</label>
            <div
              v-if="key === 'issue_id'"
              class="w-full rounded-xl border border-surface-700 bg-surface-800 px-4 py-3"
            >
              <div class="text-xs font-bold text-surface-100 truncate">
                {{ getIssueDisplayText() }}
              </div>
              <div class="mt-1 text-[10px] uppercase tracking-widest text-surface-500">
                ID {{ originalArgs[key] ?? "—" }}
              </div>
            </div>
            <div
              v-else-if="key === 'assigned_to_id' && !isSelectField(key)"
              class="w-full rounded-xl border border-surface-700 bg-surface-800 px-4 py-3"
            >
              <div class="text-xs font-bold text-surface-100 truncate">
                {{ getAssigneeDisplayText() }}
              </div>
              <div class="mt-1 text-[10px] uppercase tracking-widest text-surface-500">
                ID {{ originalArgs[key] ?? "—" }}
              </div>
            </div>
            <select
              v-if="isSelectField(key)"
              v-model="editableArgs[key]"
              class="w-full bg-surface-800 border border-surface-700 p-4 rounded-xl text-xs font-bold text-surface-100 focus:border-sage-500/40 focus:ring-4 focus:ring-sage-500/5 transition-all outline-none"
            >
              <option value="" disabled>{{ metadataLoading ? "Loading Redmine options..." : `Select ${labelize(key)}` }}</option>
              <option
                v-for="option in getFieldOptions(key)"
                :key="option.id"
                :value="option.id"
              >
                {{ option.name }}
              </option>
            </select>
            <textarea
              v-else-if="isStructuredArg(key)"
              v-model="editableArgs[key]"
              rows="5"
              :placeholder="argPlaceholder(key)"
              class="w-full bg-surface-800 border border-surface-700 p-4 rounded-xl text-xs font-mono text-surface-300 placeholder:text-surface-600 focus:border-sage-500/40 focus:ring-4 focus:ring-sage-500/5 transition-all outline-none resize-none custom-scrollbar"
            />
            <input
              v-else
              v-model="editableArgs[key]"
              :placeholder="argPlaceholder(key)"
              class="w-full bg-surface-800 border border-surface-700 p-4 rounded-xl text-xs font-bold text-surface-100 placeholder:text-surface-600 focus:border-sage-500/40 focus:ring-4 focus:ring-sage-500/5 transition-all outline-none"
            />
          </div>
          <button 
            :disabled="disabled || !actionName.trim()" 
            @click="edit"
            class="h-10 rounded-xl bg-surface-800 hover:bg-surface-700 border border-surface-700 text-surface-300 font-black text-[10px] uppercase tracking-widest transition-all active:scale-95 disabled:opacity-30"
          >
            Submit Edited Action
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #2a2d29;
  border-radius: 99px;
}
</style>