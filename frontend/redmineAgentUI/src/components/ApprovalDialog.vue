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
const editArgsJson = ref("{}");

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

watch(
  () => props.interrupt,
  (nextInterrupt) => {
    const extracted = extractEditableAction(nextInterrupt);
    if (!extracted) {
      editName.value = "";
      editArgsJson.value = "{}";
      return;
    }

    editName.value = extracted.name;
    editArgsJson.value = JSON.stringify(extracted.args, null, 2);
  },
  { immediate: true },
);

function approve() {
  emit("approve");
}

function reject() {
  emit("reject", rejectMessage.value || "Rejected by user");
}

function edit() {
  try {
    const parsed = JSON.parse(editArgsJson.value || "{}");
    emit("edit", { name: editName.value.trim(), args: parsed });
  } catch {
    alert("Invalid JSON in edit args");
  }
}
</script>

<template>
  <section v-if="visible" class="hitl">
    <h3>Human Approval Required</h3>
    <pre>{{ interrupt }}</pre>

    <div class="actions">
      <button :disabled="disabled" @click="approve">Approve</button>
      <button :disabled="disabled" @click="reject">Reject</button>
    </div>

    <div class="template-editor">
      <p class="template-title">Edit action template (optional)</p>
      <input v-model="editName" placeholder="Tool name (e.g. create_issue)" />
      <textarea v-model="editArgsJson" rows="6" placeholder='{"project_id":"...", "subject":"..."}' />
      <button :disabled="disabled || !editName.trim()" @click="edit">Submit Edit</button>
    </div>
  </section>
</template>

<style scoped>
.hitl {
  border: 1px solid var(--border-subtle);
  background: rgba(245, 158, 11, 0.1);
  color: var(--text-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-md) var(--space-lg);
  margin: var(--space-md);
  max-width: 900px;
}

h3 {
  margin: 0 0 var(--space-md);
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--accent-amber);
}

pre {
  max-height: 200px;
  overflow: auto;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  font-size: var(--text-xs);
  line-height: 1.4;
}

.actions {
  display: flex;
  gap: var(--space-md);
  margin: var(--space-lg) 0;
}

.actions button {
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-lg);
  border: none;
  font-weight: 500;
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.actions button:first-child {
  background: var(--accent-green);
  color: white;
}

.actions button:first-child:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.actions button:nth-child(2) {
  background: var(--accent-red);
  color: white;
}

.actions button:nth-child(2):hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

input,
textarea {
  width: 100%;
  margin-top: var(--space-md);
  padding: var(--space-md);
  border: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: var(--radius-md);
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: var(--text-sm);
}

input:focus,
textarea:focus {
  outline: none;
  border-color: var(--accent-blue);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.template-editor {
  margin-top: var(--space-lg);
}

.template-title {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--accent-amber);
  font-weight: 500;
}

.template-editor button {
  margin-top: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-lg);
  border: none;
  background: var(--accent-blue);
  color: white;
  font-weight: 500;
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.template-editor button:hover:not(:disabled) {
  background: var(--accent-blue-hover);
  transform: translateY(-1px);
}

.template-editor button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>