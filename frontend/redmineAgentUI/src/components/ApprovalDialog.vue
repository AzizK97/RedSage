<script setup lang="ts">
import { computed, ref, watch } from "vue";

const props = defineProps<{
  interrupt: Record<string, any> | null;
  disabled: boolean;
}>();

const emit = defineEmits<{
  (e: "approve"): void;
  (e: "reject", message: string): void;
  (e: "edit", payload: { name: string; args: Record<string, any> }): void;
}>();

const rejectMessage = ref("Rejected by user");
const editName = ref("");
const editableArgs = ref<Record<string, any>>({});
const editingField = ref<string | null>(null);
const editingName = ref(false);
const fieldDraft = ref("");
const nameDraft = ref("");

function hasInterruptPayload(interrupt: Record<string, any> | null) {
  if (!interrupt) return false;
  if (Array.isArray(interrupt)) return interrupt.length > 0;
  return Object.keys(interrupt).length > 0;
}

function extractEditableAction(interrupt: Record<string, any> | null) {
  if (!interrupt) return null;

  const actionRequests = Array.isArray(interrupt.action_requests)
    ? interrupt.action_requests
    : [];

  const firstAction = actionRequests[0] ?? interrupt.action_request ?? interrupt;

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

  if (!name || typeof name !== "string") return null;

  return {
    name: name.trim(),
    args: args && typeof args === "object" && !Array.isArray(args) ? args : {},
  };
}

const visible = computed(() => hasInterruptPayload(props.interrupt));
const argEntries = computed(() => Object.entries(editableArgs.value));

watch(
  () => props.interrupt,
  (nextInterrupt) => {
    const extracted = extractEditableAction(nextInterrupt);
    if (!extracted) {
      editName.value = "";
      editableArgs.value = {};
      editingField.value = null;
      fieldDraft.value = "";
      editingName.value = false;
      nameDraft.value = "";
      return;
    }

    editName.value = extracted.name;
    editableArgs.value = JSON.parse(JSON.stringify(extracted.args ?? {}));
    editingField.value = null;
    fieldDraft.value = "";
    editingName.value = false;
    nameDraft.value = extracted.name;
  },
  { immediate: true },
);

function fieldValueToText(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

function parseEditedValue(raw: string): unknown {
  const text = raw.trim();
  if (!text) return "";

  try {
    return JSON.parse(text);
  } catch {
    return raw;
  }
}

function beginEditName() {
  nameDraft.value = editName.value;
  editingName.value = true;
}

function cancelEditName() {
  editingName.value = false;
  nameDraft.value = editName.value;
}

function saveEditName() {
  const next = nameDraft.value.trim();
  if (!next) return;
  editName.value = next;
  editingName.value = false;
}

function beginEditField(key: string) {
  editingField.value = key;
  fieldDraft.value = fieldValueToText(editableArgs.value[key]);
}

function cancelEditField() {
  editingField.value = null;
  fieldDraft.value = "";
}

function saveEditField(key: string) {
  editableArgs.value = {
    ...editableArgs.value,
    [key]: parseEditedValue(fieldDraft.value),
  };
  cancelEditField();
}

function isComplexValue(value: unknown) {
  return typeof value === "object" && value !== null;
}

function approve() {
  emit("approve");
}

function reject() {
  emit("reject", rejectMessage.value || "Rejected by user");
}

function edit() {
  emit("edit", { name: editName.value.trim(), args: editableArgs.value });
}
</script>

<template>
  <section v-if="visible" class="approval-card" aria-live="polite">
    <div class="approval-header">
      <div>
        <p class="approval-kicker">Human approval required</p>
        <h3>Review the proposed action</h3>
      </div>
      <span class="approval-badge">Paused</span>
    </div>

    <p class="approval-copy">
      The assistant is waiting for your confirmation before it continues with the next step.
    </p>

    <div class="approval-grid">
      <div class="panel">
        <p class="panel-title">Incoming payload</p>

        <!-- <div class="field-row">
          <div class="field-meta">
            <span class="field-label">Tool name</span>
          </div>

          <div class="field-value">
            <input
              v-if="editingName"
              v-model="nameDraft"
              :disabled="disabled"
              placeholder="Tool name"
            />
            <input v-else :value="editName" readonly />
          </div>

          <div class="field-actions">
            <button
              v-if="!editingName"
              class="btn btn-inline"
              :disabled="disabled"
              @click="beginEditName"
            >
              Edit
            </button>
            <template v-else>
              <button class="btn btn-inline" :disabled="disabled || !nameDraft.trim()" @click="saveEditName">
                Save
              </button>
              <button class="btn btn-inline btn-ghost" :disabled="disabled" @click="cancelEditName">
                Cancel
              </button>
            </template>
          </div>
        </div> -->

        <div v-if="argEntries.length" class="field-list">
          <div v-for="([key, value]) in argEntries" :key="key" class="field-row">
            <div class="field-meta">
              <span class="field-label">{{ key }}</span>
            </div>

            <div class="field-value">
              <textarea
                v-if="editingField === key && isComplexValue(value)"
                v-model="fieldDraft"
                rows="3"
                :disabled="disabled"
              />
              <input
                v-else-if="editingField === key"
                v-model="fieldDraft"
                :disabled="disabled"
              />
              <textarea
                v-else-if="isComplexValue(value)"
                :value="fieldValueToText(value)"
                rows="3"
                readonly
              />
              <input v-else :value="fieldValueToText(value)" readonly />
            </div>

            <div class="field-actions">
              <button
                v-if="editingField !== key"
                class="btn btn-inline"
                :disabled="disabled || !!editingField"
                @click="beginEditField(key)"
              >
                Edit
              </button>
              <template v-else>
                <button class="btn btn-inline" :disabled="disabled" @click="saveEditField(key)">
                  Save
                </button>
                <button class="btn btn-inline btn-ghost" :disabled="disabled" @click="cancelEditField">
                  Cancel
                </button>
              </template>
            </div>
          </div>
        </div>

        <p v-else class="muted">No editable arguments were provided for this action.</p>
      </div>

      <div class="panel">
        <p class="panel-title">Decision controls</p>
        <label class="field">
          <span>Reject message</span>
          <input v-model="rejectMessage" placeholder="Rejected by user" />
        </label>

        <div class="actions">
          <button class="btn btn-ghost" :disabled="disabled" @click="reject">Reject</button>
          <button class="btn btn-success" :disabled="disabled" @click="approve">Approve</button>
        </div>
      </div>
    </div>

    <div class="editor-actions">
      <button class="btn btn-primary" :disabled="disabled || !editName.trim()" @click="edit">
        Submit edit
      </button>
    </div>
  </section>
</template>

<style scoped>
.approval-card {
  width: 100%;
  margin: 0;
  padding: var(--space-lg);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  background: linear-gradient(180deg, rgba(37, 37, 37, 0.98), rgba(26, 26, 26, 0.98));
  color: var(--text-primary);
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.28);
}

.approval-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-md);
  margin-bottom: var(--space-sm);
}

.approval-kicker {
  margin: 0 0 var(--space-xs);
  color: var(--accent-amber);
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.approval-card h3 {
  margin: 0;
  font-size: var(--text-xl);
  font-weight: 600;
  letter-spacing: -0.02em;
}

.approval-badge {
  display: inline-flex;
  align-items: center;
  height: 2rem;
  padding: 0 var(--space-md);
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.12);
  color: var(--accent-amber);
  border: 1px solid rgba(245, 158, 11, 0.2);
  font-size: var(--text-xs);
  font-weight: 600;
  white-space: nowrap;
}

.approval-copy {
  margin: 0 0 var(--space-lg);
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.approval-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
  gap: var(--space-md);
}

.panel {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: rgba(15, 15, 15, 0.42);
  padding: var(--space-md);
}

.panel-title {
  margin: 0 0 var(--space-sm);
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-weight: 600;
}

.optional {
  color: var(--text-secondary);
  font-weight: 400;
}

.field-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.field-row {
  display: grid;
  grid-template-columns: 140px minmax(0, 1fr) auto;
  gap: var(--space-sm);
  align-items: start;
  padding: var(--space-sm);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  background: rgba(15, 15, 15, 0.5);
}

.field-meta {
  display: flex;
  align-items: center;
  min-height: 2.5rem;
}

.field-label {
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-weight: 600;
  word-break: break-word;
}

.field-value {
  min-width: 0;
}

.field-actions {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.field + .field {
  margin-top: var(--space-md);
}

.field span {
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-weight: 500;
}

input,
textarea {
  width: 100%;
  border: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: var(--radius-md);
  padding: 0.75rem 0.85rem;
  font-family: inherit;
  font-size: var(--text-sm);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast), background-color var(--transition-fast);
}

textarea {
  resize: vertical;
  min-height: 140px;
  font-family: "Monaco", "Courier New", monospace;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: var(--accent-blue);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.14);
}

.actions,
.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-sm);
  margin-top: var(--space-lg);
}

.btn {
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  padding: 0.7rem 1rem;
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  transition: transform var(--transition-fast), background-color var(--transition-fast), border-color var(--transition-fast), opacity var(--transition-fast);
}

.btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  transform: none;
}

.btn-ghost {
  background: transparent;
  border-color: var(--border-subtle);
  color: var(--text-secondary);
}

.btn-ghost:hover:not(:disabled) {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.btn-success {
  background: var(--accent-green);
  color: white;
}

.btn-success:hover:not(:disabled) {
  opacity: 0.92;
}

.btn-primary {
  background: var(--accent-blue);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent-blue-hover);
}

.btn-inline {
  padding: 0.45rem 0.7rem;
  font-size: var(--text-xs);
  font-weight: 600;
  background: var(--bg-secondary);
  border-color: var(--border-subtle);
  color: var(--text-secondary);
}

.btn-inline:hover:not(:disabled) {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.muted {
  margin: var(--space-sm) 0 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

@media (max-width: 760px) {
  .approval-card {
    padding: var(--space-md);
  }

  .approval-header,
  .approval-grid {
    grid-template-columns: 1fr;
  }

  .field-row {
    grid-template-columns: 1fr;
  }

  .approval-header {
    display: flex;
    flex-direction: column;
  }

  .actions,
  .editor-actions {
    justify-content: stretch;
  }

  .actions .btn,
  .editor-actions .btn {
    flex: 1;
  }
}
</style>