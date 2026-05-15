<script setup lang="ts">
import { computed } from "vue";
import { useTheme } from "@redsage/ui-core/composables/useTheme";
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

const bgClass = computed(() => isDark.value ? 'bg-surface-950 text-surface-200' : 'bg-surface-50 text-sage-900');
</script>

<template>
  <div :class="['min-h-screen overflow-x-hidden', bgClass]">
    <NavBar @start-login="emit('start-login')" />
    <HeroSection @start-login="emit('start-login')" />
    <AgentsSection />
    <HowItWorksSection />
    <SafetySection />
    <TechStackSection />
    <BenchmarkSection />
    <GetStartedSection />
    <CTASection />
    <FooterSection />
  </div>
</template>
