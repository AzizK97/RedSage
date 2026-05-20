<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { authApi } from "@redsage/api-client/auth";
import type { PlatformRole } from "@redsage/ui-core/composables/useSession";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  Copy,
  Eye,
  EyeOff,
  KeyRound,
  Loader2,
  Settings,
  ShieldCheck,
} from "lucide-vue-next";

type Step = 0 | 1 | 2 | 3 | 4;

const steps = [
//   { id: 0, label: "Account", icon: UserPlus },
  { id: 0, label: "Enable API", icon: Settings },
  { id: 1, label: "Get Key", icon: KeyRound },
  { id: 2, label: "Connect", icon: ShieldCheck },
] as const;

const router = useRouter();

const step = ref<Step>(0);

const name = ref("");
// const email = ref("");
// const password = ref("");

const redmineUrl = ref("");
const apiKey = ref("");
const showKey = ref(false);
const connecting = ref(false);
const copied = ref(false);
const connectError = ref("");

const emit = defineEmits<{
  (event: "login", payload: { token: string; role: PlatformRole; fullName: string }): void;
  (event: "back"): void;
}>();

// const canContinueAccount = computed(() => {
//   return name.value.trim().length > 0 && /\S+@\S+\.\S+/.test(email.value) && password.value.length >= 8;
// });

const canConnect = computed(() => {
  return /^https?:\/\//i.test(redmineUrl.value.trim()) && apiKey.value.trim().length >= 8;
});

function next() {
  step.value = Math.min(3, step.value + 1) as Step;
}

function prev() {
  step.value = Math.max(0, step.value - 1) as Step;
}

function decodeRoleFromToken(token: string): PlatformRole {
  const segments = token.split(".");
  if (segments.length < 2) {
    throw new Error("Invalid token format");
  }

  const payloadSegment = segments[1]
    .replace(/-/g, "+")
    .replace(/_/g, "/");

  const paddedPayload = payloadSegment.padEnd(payloadSegment.length + ((4 - (payloadSegment.length % 4)) % 4), "=");
  const decoded = JSON.parse(atob(paddedPayload)) as { role?: string };
  if (decoded.role !== "admin" && decoded.role !== "project_manager") {
    throw new Error("Unsupported role in token");
  }
  return decoded.role;
}

async function handleConnect() {
  connectError.value = "";
  connecting.value = true;
  try {
    const result = await authApi.redmineConnect(redmineUrl.value.trim() || undefined, apiKey.value.trim());
    const role = decodeRoleFromToken(result.access_token);
    emit("login", { token: result.access_token, role, fullName: result.full_name });
  } catch (err) {
    connectError.value = err instanceof Error ? err.message : String(err);
  } finally {
    connecting.value = false;
  }
}

async function copyApiKey() {
  if (!apiKey.value.trim()) return;
  await navigator.clipboard?.writeText(apiKey.value.trim());
  copied.value = true;
  window.setTimeout(() => {
    copied.value = false;
  }, 1500);
}

function goToLogin() {
  void router.push({ name: "login" });
}

function goToLanding() {
  void router.push({ name: "landing" });
}
</script>

<template>
  <main class="min-h-screen bg-surface-950 text-surface-200 py-8 px-4 sm:px-6 lg:px-8">
    <section class="mx-auto w-full max-w-4xl space-y-8">
      <div class="flex items-center justify-between gap-4">
        <button
          type="button"
          class="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-200 transition-colors"
          @click="goToLanding"
        >
          <ArrowLeft :size="16" /> Back to landing
        </button>

        <button
          type="button"
          class="inline-flex items-center gap-2 text-sm font-medium text-copper-400 hover:text-copper-300 transition-colors"
          @click="goToLogin"
        >
          Already have an account? Sign in <ArrowRight :size="16" />
        </button>
      </div>

      <div class="space-y-6">
        <div class="text-center space-y-3">
          <p class="text-xs font-semibold uppercase tracking-[0.24em] text-copper-400">Create your account</p>
          <h1 class="text-3xl sm:text-4xl font-bold text-surface-50">Start with a simple Redmine connection flow</h1>
          <p class="mx-auto max-w-2xl text-sm sm:text-base text-surface-400">
            Set up your profile, enable the Redmine API, and connect your instance in a few guided steps.
          </p>
        </div>

        <ol v-if="step < 2" class="flex justify-between pl-20 gap-20">
          <li v-for="(item, index) in steps" :key="item.id" class="flex flex-1 items-center gap-2">
            <div
              :class="[
                'grid h-10 w-10 shrink-0 place-items-center rounded-full border transition-colors',
                step > item.id
                  ? 'border-emerald-500 bg-emerald-500/15 text-emerald-400'
                  : step === item.id
                    ? 'border-copper-500 bg-copper-500/15 text-copper-300'
                    : 'border-surface-700 bg-surface-900 text-surface-500',
              ]"
            >
              <Check v-if="step > item.id" :size="16" />
              <component v-else :is="item.icon" :size="16" />
            </div>
            <span :class="['hidden text-xs font-medium sm:inline', step === item.id ? 'text-surface-50' : 'text-surface-500']">
              {{ item.label }}
            </span>
            <div v-if="index < steps.length - 1" :class="['h-px flex-1', step > item.id ? 'bg-emerald-500/60' : 'bg-surface-800']" />
          </li>
        </ol>

        <div class="rounded-2xl border border-surface-800 bg-surface-900/70 p-6 sm:p-8 shadow-2xl shadow-black/20">
          <!-- <section v-if="step === 0" class="space-y-6">
            <div>
              <h2 class="text-2xl font-bold text-surface-50">Create your account</h2>
              <p class="mt-1 text-sm text-surface-400">Start your free RedSage trial. No credit card required.</p>
            </div>

            <div class="grid gap-4">
              <label class="block space-y-2">
                <span class="text-sm font-medium text-surface-300">Full name</span>
                <input v-model="name" type="text" autocomplete="name" placeholder="Aziz Kanoun" class="w-full px-4 py-2.5 rounded-lg bg-surface-950/60 border border-surface-700 text-surface-100 placeholder-surface-500 focus:outline-none focus:border-copper-500 focus:ring-1 focus:ring-copper-500/30 transition-colors" />
              </label>

              <label class="block space-y-2">
                <span class="text-sm font-medium text-surface-300">Work email</span>
                <input v-model="email" type="email" autocomplete="email" placeholder="you@company.com" class="w-full px-4 py-2.5 rounded-lg bg-surface-950/60 border border-surface-700 text-surface-100 placeholder-surface-500 focus:outline-none focus:border-copper-500 focus:ring-1 focus:ring-copper-500/30 transition-colors" />
              </label>

              <label class="block space-y-2">
                <span class="text-sm font-medium text-surface-300">Password</span>
                <input v-model="password" type="password" autocomplete="new-password" placeholder="••••••••" class="w-full px-4 py-2.5 rounded-lg bg-surface-950/60 border border-surface-700 text-surface-100 placeholder-surface-500 focus:outline-none focus:border-copper-500 focus:ring-1 focus:ring-copper-500/30 transition-colors" />
                <span class="text-xs text-surface-500">At least 8 characters.</span>
              </label>
            </div>

            <div class="flex items-center justify-between gap-3 pt-2">
              <button type="button" class="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-200 transition-colors" @click="goToLanding">
                <ArrowLeft :size="16" /> Cancel
              </button>

              <button type="button" class="inline-flex items-center gap-2 rounded-lg bg-copper-600 px-5 py-2.5 font-semibold text-white transition-colors hover:bg-copper-500 disabled:cursor-not-allowed disabled:opacity-50" :disabled="!canContinueAccount" @click="next">
                Continue <ArrowRight :size="16" />
              </button>
            </div>
          </section> -->

          <section v-if="step === 0" class="space-y-6">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.22em] text-copper-400">Step 1 of 2 · Redmine setup</p>
              <h2 class="mt-2 text-2xl font-bold text-surface-50">Enable the REST API in Redmine</h2>
              <p class="mt-1 text-sm text-surface-400">A Redmine administrator must enable the REST web service before any user can generate an API key.</p>
            </div>

            <ol class="space-y-3">
              <li class="rounded-lg border border-surface-800 bg-surface-950/50 p-4 text-sm text-surface-200">Log in to Redmine as an administrator.</li>
              <li class="rounded-lg border border-surface-800 bg-surface-950/50 p-4 text-sm text-surface-200">Open Administration → Settings.</li>
              <li class="rounded-lg border border-surface-800 bg-surface-950/50 p-4 text-sm text-surface-200">Open the API tab.</li>
              <li class="rounded-lg border border-surface-800 bg-surface-950/50 p-4 text-sm text-surface-200">Enable REST web service and save changes.</li>
            </ol>

            <div class="rounded-lg border border-copper-500/25 bg-copper-500/10 p-4 text-sm text-surface-200">
              Don’t have admin access? Send these instructions to your Redmine admin and continue once the API is enabled.
            </div>

            <div class="flex items-center justify-between gap-3 pt-2">
              <button type="button" class="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-200 transition-colors" @click="prev">
                <ArrowLeft :size="16" /> Back
              </button>
              <button type="button" class="inline-flex items-center gap-2 rounded-lg bg-copper-600 px-5 py-2.5 font-semibold text-white transition-colors hover:bg-copper-500" @click="next">
                I’ve enabled it <ArrowRight :size="16" />
              </button>
            </div>
          </section>

          <section v-else-if="step === 1" class="space-y-6">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.22em] text-copper-400">Step 2 of 2 · Redmine setup</p>
              <h2 class="mt-2 text-2xl font-bold text-surface-50">Retrieve your API access key</h2>
              <p class="mt-1 text-sm text-surface-400">Every Redmine user has a personal API key once the REST service is enabled.</p>
            </div>

            <ol class="space-y-3">
              <li class="rounded-lg border border-surface-800 bg-surface-950/50 p-4 text-sm text-surface-200">Click “My account” in the upper-right corner of Redmine.</li>
              <li class="rounded-lg border border-surface-800 bg-surface-950/50 p-4 text-sm text-surface-200">Find the API access key section in the sidebar.</li>
              <li class="rounded-lg border border-surface-800 bg-surface-950/50 p-4 text-sm text-surface-200">Click Show to reveal your key.</li>
              <li class="rounded-lg border border-surface-800 bg-surface-950/50 p-4 text-sm text-surface-200">Need a fresh key? Reset it from the same section.</li>
            </ol>

            <div class="rounded-lg border border-copper-500/25 bg-copper-500/10 p-4 text-sm text-surface-200">
              Treat your API key like a password. RedSage uses it only to connect to your Redmine instance on your behalf.
            </div>

            <div class="flex items-center justify-between gap-3 pt-2">
              <button type="button" class="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-200 transition-colors" @click="prev">
                <ArrowLeft :size="16" /> Back
              </button>
              <button type="button" class="inline-flex items-center gap-2 rounded-lg bg-copper-600 px-5 py-2.5 font-semibold text-white transition-colors hover:bg-copper-500" @click="next">
                I have my key <ArrowRight :size="16" />
              </button>
            </div>
          </section>

          <section v-else-if="step === 2" class="space-y-6">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.22em] text-copper-400">Connect</p>
              <h2 class="mt-2 text-2xl font-bold text-surface-50">Connect your Redmine instance</h2>
              <p class="mt-1 text-sm text-surface-400">Paste your Redmine URL and the API access key you just copied.</p>
            </div>

            <div class="grid gap-4">
              <label class="block space-y-2">
                <span class="text-sm font-medium text-surface-300">Redmine URL</span>
                <input v-model="redmineUrl" type="url" placeholder="https://redmine.your-company.com" class="w-full px-4 py-2.5 rounded-lg bg-surface-950/60 border border-surface-700 text-surface-100 placeholder-surface-500 focus:outline-none focus:border-copper-500 focus:ring-1 focus:ring-copper-500/30 transition-colors" />
              </label>

              <label class="block space-y-2">
                <span class="text-sm font-medium text-surface-300">API access key</span>
                <div class="relative">
                  <input v-model="apiKey" :type="showKey ? 'text' : 'password'" placeholder="a1b2c3d4e5f6…" class="w-full px-4 py-2.5 pr-24 rounded-lg bg-surface-950/60 border border-surface-700 text-surface-100 placeholder-surface-500 font-mono text-sm focus:outline-none focus:border-copper-500 focus:ring-1 focus:ring-copper-500/30 transition-colors" />
                  <div class="absolute inset-y-0 right-2 flex items-center gap-1">
                    <button type="button" class="rounded-md p-2 text-surface-400 hover:text-surface-200 hover:bg-surface-800/70 transition-colors" :aria-label="showKey ? 'Hide key' : 'Show key'" @click="showKey = !showKey">
                      <Eye v-if="!showKey" :size="16" />
                      <EyeOff v-else :size="16" />
                    </button>
                    <button type="button" class="rounded-md p-2 text-surface-400 hover:text-surface-200 hover:bg-surface-800/70 transition-colors" aria-label="Copy key" @click="copyApiKey">
                      <Copy :size="16" />
                    </button>
                  </div>
                </div>
                <p v-if="copied" class="text-xs text-emerald-400">API key copied to clipboard.</p>
              </label>

              <a href="#" class="inline-flex items-center gap-1.5 text-sm text-copper-400 hover:text-copper-300 transition-colors" @click.prevent="step = 1">
                <ShieldCheck :size="14" /> Where do I find my API key?
              </a>
            </div>

            <div class="flex items-center justify-between gap-3 pt-2">
              <button type="button" class="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-200 transition-colors" @click="prev">
                <ArrowLeft :size="16" /> Back
              </button>
              <button
                type="button"
                :disabled="!canConnect || connecting"
                class="inline-flex items-center gap-2 rounded-lg bg-copper-600 px-5 py-2.5 font-semibold text-white transition-colors hover:bg-copper-500 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-copper-600"
                @click="handleConnect"
              >
                <Loader2 v-if="connecting" :size="16" class="animate-spin" />
                {{ connecting ? 'Connecting…' : 'Connect Redmine' }}
              </button>
            </div>
            <p v-if="connectError" class="mt-3 p-3 bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-700/50 rounded-lg text-rose-700 dark:text-rose-300 text-sm">{{ connectError }}</p>
          </section>

          <section v-else class="space-y-6 text-center">
            <div class="mx-auto grid h-14 w-14 place-items-center rounded-full bg-emerald-500/15 text-emerald-400">
              <Check :size="28" />
            </div>
            <div class="space-y-2">
              <h2 class="text-2xl font-bold text-surface-50">You’re all set, {{ name.split(' ')[0] || 'there' }}!</h2>
              <p class="mx-auto max-w-md text-sm text-surface-400">
                Your Redmine instance is connected. RedSage is ready to turn your conversations into project actions.
              </p>
            </div>
            <div class="flex items-center justify-center gap-3">
              <button type="button" class="inline-flex items-center gap-2 rounded-lg bg-copper-600 px-5 py-2.5 font-semibold text-white transition-colors hover:bg-copper-500" @click="goToLogin">
                Sign in <ArrowRight :size="16" />
              </button>
            </div>
          </section>
        </div>

        <p v-if="step < 3" class="text-center text-xs text-surface-500">
          Already have an account?
          <button type="button" class="font-semibold text-copper-400 hover:text-copper-300 transition-colors" @click="goToLogin">Sign in</button>
        </p>
      </div>
    </section>
  </main>
</template>