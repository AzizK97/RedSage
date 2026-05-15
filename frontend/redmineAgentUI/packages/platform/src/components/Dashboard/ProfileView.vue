<script setup lang="ts">
import { computed, ref } from "vue";

const props = defineProps<{
  role: "admin" | "project_manager";
  userId: string;
  fullName: string;
  email: string;
}>();

const passwordForm = ref({
  currentPassword: "",
  newPassword: "",
  confirmPassword: "",
});

const statusMessage = ref("");
const statusType = ref<"success" | "error" | "">("");
const isSaving = ref(false);

const roleLabel = computed(() => (props.role === "admin" ? "Administrator" : "Project Manager"));
const initials = computed(() => {
  const source = props.fullName.trim() || props.email.trim() || "U";
  return source
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("")
    .slice(0, 2) || "U";
});

function resetStatus() {
  statusMessage.value = "";
  statusType.value = "";
}

async function savePassword() {
  resetStatus();

  if (!passwordForm.value.currentPassword || !passwordForm.value.newPassword || !passwordForm.value.confirmPassword) {
    statusType.value = "error";
    statusMessage.value = "Please fill in all password fields.";
    return;
  }

  if (passwordForm.value.newPassword.length < 8) {
    statusType.value = "error";
    statusMessage.value = "New password must be at least 8 characters.";
    return;
  }

  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    statusType.value = "error";
    statusMessage.value = "New password and confirmation do not match.";
    return;
  }

  isSaving.value = true;
  try {
    // UI placeholder: wire this to a backend password-change endpoint later.
    await new Promise((resolve) => setTimeout(resolve, 600));
    statusType.value = "success";
    statusMessage.value = "Password updated successfully.";
    passwordForm.value.currentPassword = "";
    passwordForm.value.newPassword = "";
    passwordForm.value.confirmPassword = "";
  } catch {
    statusType.value = "error";
    statusMessage.value = "Unable to update password right now.";
  } finally {
    isSaving.value = false;
  }
}
</script>

<template>
  <main class="min-h-screen bg-surface-950 p-6 md:p-8">
    <section class="max-w-4xl mx-auto glass-card p-8 space-y-8">
      <!-- Header -->
      <div class="flex flex-col md:flex-row gap-6 md:gap-8">
        <div class="w-22 h-22 rounded-2xl border border-sage-600/30 bg-gradient-to-br from-sage-600/20 to-sage-900/40 flex items-center justify-center flex-shrink-0">
          <span class="text-2xl font-bold text-sage-400">{{ initials }}</span>
        </div>
        <div class="flex flex-col justify-center">
          <p class="text-xs font-semibold uppercase tracking-widest text-sage-500 mb-1">PROFILE</p>
          <h1 class="text-3xl font-bold text-surface-100 mb-2">{{ fullName || "Unknown user" }}</h1>
          <p class="text-surface-400">Manage your account information and password settings.</p>
        </div>
      </div>

      <div class="h-px bg-surface-700/50"></div>

      <!-- Info Grid -->
      <section class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <article class="p-4 border border-surface-700/50 rounded-lg bg-surface-900/30">
          <span class="text-xs font-medium text-surface-400">Full name</span>
          <p class="text-surface-100 font-semibold mt-1">{{ fullName || "Unknown" }}</p>
        </article>
        <article class="p-4 border border-surface-700/50 rounded-lg bg-surface-900/30">
          <span class="text-xs font-medium text-surface-400">Email</span>
          <p class="text-surface-100 font-semibold mt-1">{{ email || "Unknown" }}</p>
        </article>
        <article class="p-4 border border-surface-700/50 rounded-lg bg-surface-900/30">
          <span class="text-xs font-medium text-surface-400">Role</span>
          <p class="text-surface-100 font-semibold mt-1">{{ roleLabel }}</p>
        </article>
        <article class="p-4 border border-surface-700/50 rounded-lg bg-surface-900/30">
          <span class="text-xs font-medium text-surface-400">User ID</span>
          <p class="text-surface-100 font-semibold mt-1 font-mono text-sm">{{ userId || "Unknown" }}</p>
        </article>
      </section>

      <!-- Password Section -->
      <section class="border border-surface-700/50 rounded-lg bg-surface-900/30 p-6 space-y-6">
        <div>
          <h2 class="text-xl font-bold text-surface-100 mb-1">Change password</h2>
          <p class="text-surface-400 text-sm">Update your password using your current credentials.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <label class="block space-y-2">
            <span class="text-sm font-medium text-surface-300">Current password</span>
            <input 
              v-model="passwordForm.currentPassword" 
              type="password" 
              placeholder="Enter current password"
              class="w-full px-3 py-2 bg-surface-800/50 border border-surface-700 rounded-lg text-surface-100 placeholder-surface-500 focus:outline-none focus:border-sage-600 focus:ring-1 focus:ring-sage-600/30 transition-colors"
            />
          </label>
          <label class="block space-y-2">
            <span class="text-sm font-medium text-surface-300">New password</span>
            <input 
              v-model="passwordForm.newPassword" 
              type="password" 
              placeholder="Enter new password"
              class="w-full px-3 py-2 bg-surface-800/50 border border-surface-700 rounded-lg text-surface-100 placeholder-surface-500 focus:outline-none focus:border-sage-600 focus:ring-1 focus:ring-sage-600/30 transition-colors"
            />
          </label>
          <label class="block space-y-2">
            <span class="text-sm font-medium text-surface-300">Confirm new password</span>
            <input 
              v-model="passwordForm.confirmPassword" 
              type="password" 
              placeholder="Repeat new password"
              class="w-full px-3 py-2 bg-surface-800/50 border border-surface-700 rounded-lg text-surface-100 placeholder-surface-500 focus:outline-none focus:border-sage-600 focus:ring-1 focus:ring-sage-600/30 transition-colors"
            />
          </label>
        </div>

        <p 
          v-if="statusMessage" 
          :class="[
            'p-3 rounded-lg text-sm font-medium',
            statusType === 'success' 
              ? 'bg-sage-950/30 border border-sage-700/50 text-sage-300'
              : 'bg-rose-950/30 border border-rose-700/50 text-rose-300'
          ]"
        >
          {{ statusMessage }}
        </p>

        <div class="flex justify-end">
          <button 
            type="button" 
            :disabled="isSaving" 
            @click="savePassword"
            class="px-6 py-2.5 bg-sage-600 hover:bg-sage-700 disabled:bg-surface-700 disabled:cursor-not-allowed text-surface-50 font-semibold rounded-lg transition-colors"
          >
            {{ isSaving ? "Saving..." : "Update password" }}
          </button>
        </div>
      </section>
    </section>
  </main>
</template>
