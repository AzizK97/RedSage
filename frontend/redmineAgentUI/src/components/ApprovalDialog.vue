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
  border: 1px solid #f59e0b;
  background: rgba(120, 53, 15, 0.35);
  color: #fef3c7;
  border-radius: 12px;
  padding: 0.75rem;
}

h3 {
  margin: 0 0 0.5rem;
  font-size: 0.95rem;
}

pre {
  max-height: 200px;
  overflow: auto;
  background: #111827;
  color: #e5e7eb;
  padding: 0.5rem;
  border-radius: 8px;
}

.actions {
  display: flex;
  gap: 0.5rem;
  margin: 0.6rem 0;
}

.actions button {
  padding: 0.5rem 0.85rem;
  border-radius: 8px;
  border: 1px solid transparent;
}

.actions button:first-child {
  background: #2563eb;
  color: #fff;
}

.actions button:nth-child(2) {
  background: #dc2626;
  color: #fff;
}

input,
textarea {
  width: 100%;
  margin-top: 0.5rem;
  padding: 0.55rem;
  border: 1px solid #4b5563;
  background: #1f2937;
  color: #f9fafb;
  border-radius: 8px;
}

.template-editor {
  margin-top: 0.75rem;
}

.template-title {
  margin: 0;
  font-size: 0.85rem;
  color: #fde68a;
}

.template-editor button {
  margin-top: 0.6rem;
  padding: 0.5rem 0.85rem;
  border-radius: 8px;
  border: 1px solid #3b82f6;
  background: #3b82f6;
  color: #fff;
}
</style>