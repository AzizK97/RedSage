<script setup lang="ts">
import { computed } from "vue";
import { useTheme } from "../../composables/useTheme";
import NavBar from './components/NavBar.vue';
import HeroSection from './components/HeroSection.vue';
import AgentsSection from './components/AgentsSection.vue';
import HowItWorksSection from './components/HowItWorksSection.vue';
import SafetySection from './components/SafetySection.vue';
import TechStackSection from './components/TechStackSection.vue';
import BenchmarkSection from './components/BenchmarkSection.vue';
import GetStartedSection from './components/GetStartedSection.vue';
import CTASection from './components/CTASection.vue';
import FooterSection from './components/FooterSection.vue';

const emit = defineEmits<{ (e: 'start-login'): void }>();
const { isDark } = useTheme();

const bgClass = computed(() => isDark.value ? 'bg-surface-950 text-surface-200' : 'bg-surface-50 text-sage-900');
const lightClass = computed(() => !isDark.value);
</script>

<template>
  <div :class="['min-h-screen overflow-x-hidden', bgClass]">
    <NavBar @start-login="emit('start-login')" />
    <HeroSection />
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
