<script setup lang="ts">
import { computed, ref } from "vue";

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

const visible = computed(() => !!props.interrupt);

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

    <details>
      <summary>Edit action (optional)</summary>
      <input v-model="editName" placeholder="Tool name (e.g. create_issue)" />
      <textarea v-model="editArgsJson" rows="4" placeholder='{"project_id":"...", "subject":"..."}' />
      <button :disabled="disabled || !editName.trim()" @click="edit">Submit Edit</button>
    </details>
  </section>
</template>

<style scoped>
.hitl {
  border: 1px solid #f59e0b;
  background: #fffbeb;
  border-radius: 10px;
  padding: 0.75rem;
}
pre {
  max-height: 200px;
  overflow: auto;
  background: #fff;
  padding: 0.5rem;
  border-radius: 8px;
}
.actions {
  display: flex;
  gap: 0.5rem;
  margin: 0.6rem 0;
}
input,
textarea {
  width: 100%;
  margin-top: 0.5rem;
  padding: 0.55rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
}
</style>