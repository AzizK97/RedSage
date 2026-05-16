<script setup lang="ts">
import { computed, ref } from "vue";
import { useTheme } from "@redsage/ui-core/composables/useTheme";
import { useRouter } from "vue-router";
import NavBar from '../components/LandingPage/components/NavBar.vue';
import HeroSection from '../components/LandingPage/components/HeroSection.vue';
import AgentsSection from '../components/LandingPage/components/AgentsSection.vue';
import HowItWorksSection from '../components/LandingPage/components/HowItWorksSection.vue';
import SafetySection from '../components/LandingPage/components/SafetySection.vue';
import TechStackSection from '../components/LandingPage/components/TechStackSection.vue';
import BenchmarkSection from '../components/LandingPage/components/BenchmarkSection.vue';
import GetStartedSection from '../components/LandingPage/components/GetStartedSection.vue';
import CTASection from '../components/LandingPage/components/CTASection.vue';
import FooterSection from '../components/LandingPage/components/FooterSection.vue';

const emit = defineEmits<{ (e: 'start-login'): void }>();
const { isDark } = useTheme();
const router = useRouter();

const bgClass = computed(() => isDark.value ? 'bg-surface-950 text-surface-200' : 'bg-surface-50 text-sage-900');

const showOnboarding = ref(false);
const onboardingSectionRef = ref<HTMLElement | null>(null);
const redmineUrl = ref('');
const apiKey = ref('');
const submitError = ref('');
const submitted = ref(false);

async function startOnboarding() {
  void router.push({ name: 'signup' });
}

function submitApiToken() {
  submitError.value = '';
  submitted.value = false;

  if (!apiKey.value.trim()) {
    submitError.value = 'API access token is required.';
    return;
  }

  const normalizedUrl = redmineUrl.value.trim();
  if (normalizedUrl && !/^https?:\/\//i.test(normalizedUrl)) {
    submitError.value = 'Redmine URL must start with http:// or https://';
    return;
  }

  submitted.value = true;
}
</script>

<template>
  <div :class="['min-h-screen overflow-x-hidden', bgClass]">
    <NavBar @start-login="emit('start-login')" @start-onboarding="startOnboarding" />
    <HeroSection @start-onboarding="startOnboarding" />

    <section v-if="showOnboarding" ref="onboardingSectionRef" class="relative py-12">
      <div class="max-w-4xl mx-auto px-6">
        <div class="glass-card p-6 sm:p-8 space-y-6">
          <div class="space-y-2">
            <h2 class="text-2xl sm:text-3xl font-bold text-sage-900 dark:text-surface-100">Connect your Redmine account</h2>
            <p class="text-surface-600 dark:text-surface-400">
              Paste your Redmine API access token to create your platform account.
            </p>
          </div>

          <div class="space-y-2">
            <p class="text-sm font-semibold text-sage-800 dark:text-sage-300">How to generate your token</p>
            <ol class="list-decimal list-inside text-sm text-surface-600 dark:text-surface-400 space-y-1">
              <li>Open your Redmine account page.</li>
              <li>Go to the API access key section.</li>
              <li>Click Generate (or Reset) and copy the key.</li>
              <li>Paste it below and submit.</li>
            </ol>
          </div>

          <form @submit.prevent="submitApiToken" class="space-y-4">
            <label class="block space-y-2">
              <span class="text-sm font-medium text-surface-700 dark:text-surface-300">Redmine URL (optional)</span>
              <input
                v-model="redmineUrl"
                type="text"
                placeholder="https://redmine.your-company.com"
                class="w-full px-4 py-2 bg-white/80 dark:bg-surface-900/50 border border-sage-200 dark:border-surface-700 rounded-lg text-sage-900 dark:text-surface-100 placeholder-surface-400 dark:placeholder-surface-500 focus:outline-none focus:border-sage-600 focus:ring-1 focus:ring-sage-600/30 transition-colors"
              />
            </label>

            <label class="block space-y-2">
              <span class="text-sm font-medium text-surface-700 dark:text-surface-300">API access token</span>
              <input
                v-model="apiKey"
                type="password"
                placeholder="Paste your Redmine API token"
                class="w-full px-4 py-2 bg-white/80 dark:bg-surface-900/50 border border-sage-200 dark:border-surface-700 rounded-lg text-sage-900 dark:text-surface-100 placeholder-surface-400 dark:placeholder-surface-500 focus:outline-none focus:border-sage-600 focus:ring-1 focus:ring-sage-600/30 transition-colors"
              />
            </label>

            <p v-if="submitError" class="p-3 bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-700/50 rounded-lg text-rose-700 dark:text-rose-300 text-sm">
              {{ submitError }}
            </p>
            <p v-if="submitted" class="p-3 bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-700/50 rounded-lg text-emerald-700 dark:text-emerald-300 text-sm">
              Token captured. Next step is wiring backend validation and account creation.
            </p>

            <button
              type="submit"
              class="w-full sm:w-auto px-6 py-2.5 rounded-lg bg-copper-600 text-white hover:bg-copper-500 transition-colors font-semibold"
            >
              Continue
            </button>
          </form>
        </div>
      </div>
    </section>

    <AgentsSection />
    <HowItWorksSection />
    <SafetySection />
    <TechStackSection />
    <BenchmarkSection />
    <GetStartedSection @start-onboarding="startOnboarding" />
    <CTASection @start-onboarding="startOnboarding" />
    <FooterSection />
  </div>
</template>
