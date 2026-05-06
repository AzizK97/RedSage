<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { AlertTriangle, Check, X, Edit3, Terminal } from "lucide-vue-next";

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
  <section v-if="visible" class="m-6 p-6 rounded-3xl bg-surface-900 border border-copper-500/20 shadow-2xl animate-in zoom-in-95 duration-300">
    <div class="flex items-center gap-3 mb-6">
      <div class="w-10 h-10 rounded-xl bg-copper-500/20 flex items-center justify-center text-copper-500">
        <AlertTriangle :size="20" />
      </div>
      <div>
        <h3 class="text-sm font-black text-white uppercase tracking-widest">Approval Required</h3>
        <p class="text-xs text-surface-500 font-bold">The agent is requesting permission to execute an action.</p>
      </div>
    </div>

    <div class="space-y-6">
      <div class="relative group">
        <div class="absolute top-3 left-3 text-surface-700">
          <Terminal :size="14" />
        </div>
        <pre class="w-full max-h-48 overflow-auto bg-black/40 border border-surface-800 p-8 rounded-2xl text-[10px] sm:text-xs font-mono text-surface-400 custom-scrollbar leading-relaxed">{{ interrupt }}</pre>
      </div>

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
        <div class="flex items-center gap-2 mb-4 text-surface-500">
          <Edit3 :size="14" />
          <span class="text-[10px] font-black uppercase tracking-widest">Fine-tune parameters</span>
        </div>
        
        <div class="grid gap-3">
          <input 
            v-model="editName" 
            placeholder="Tool name (e.g. create_issue)" 
            class="w-full bg-surface-800 border border-surface-700 p-4 rounded-xl text-xs font-bold text-surface-100 placeholder:text-surface-600 focus:border-sage-500/40 focus:ring-4 focus:ring-sage-500/5 transition-all outline-none"
          />
          <textarea 
            v-model="editArgsJson" 
            rows="5" 
            placeholder='{"project_id":"...", "subject":"..."}' 
            class="w-full bg-surface-800 border border-surface-700 p-4 rounded-xl text-xs font-mono text-surface-300 placeholder:text-surface-600 focus:border-sage-500/40 focus:ring-4 focus:ring-sage-500/5 transition-all outline-none resize-none custom-scrollbar"
          />
          <button 
            :disabled="disabled || !editName.trim()" 
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