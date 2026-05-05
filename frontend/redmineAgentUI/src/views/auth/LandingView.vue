<script setup lang="ts">
import { ref } from "vue";
import LandingHome from "./components/LandingHome.vue";
import LandingFeatures from "./components/LandingFeatures.vue";
import LandingPricing from "./components/LandingPricing.vue";
import LandingIntegration from "./components/LandingIntegration.vue";
import LandingFooter from "./components/LandingFooter.vue";

const emit = defineEmits<{
  (event: "start-login"): void;
}>();

const currentPage = ref<"home" | "features" | "pricing" | "integration">("home");

function beginLogin() {
  emit("start-login");
}

function navigate(page: "home" | "features" | "pricing" | "integration") {
  currentPage.value = page;
  window.scrollTo({ top: 0, behavior: "smooth" });
}
</script>

<template>
  <div class="showcase-root">
    <!-- Navigation Bar -->
    <nav class="showcase-nav glass-nav">
      <div class="nav-container">
        <div class="nav-brand" @click="navigate('home')" role="button" tabindex="0">
          <svg class="nav-logo" fill="currentColor" height="32" viewBox="0 0 48 48" width="32">
            <path clip-rule="evenodd" d="M24 4H42V17.3333V30.6667H24V44H6V30.6667V17.3333H24V4Z" fill-rule="evenodd"></path>
          </svg>
          <span class="nav-title">ProManager AI</span>
        </div>
        
        <div class="nav-links">
          <button @click="navigate('home')" :class="['nav-link', currentPage === 'home' && 'active']">Home</button>
          <button @click="navigate('features')" :class="['nav-link', currentPage === 'features' && 'active']">Features</button>
          <button @click="navigate('pricing')" :class="['nav-link', currentPage === 'pricing' && 'active']">Pricing</button>
          <button @click="navigate('integration')" :class="['nav-link', currentPage === 'integration' && 'active']">Integration</button>
        </div>

        <div class="nav-actions">
          <button @click="beginLogin" class="nav-signin">Sign In</button>
          <button @click="beginLogin" class="nav-cta">Start Free Trial</button>
        </div>
      </div>
    </nav>

    <!-- Dynamic Page Content -->
    <main class="page-content">
      <transition name="fade-page" mode="out-in">
        <LandingHome 
          v-if="currentPage === 'home'" 
          @start-login="beginLogin" 
          @navigate="navigate" 
        />
        <LandingFeatures 
          v-else-if="currentPage === 'features'" 
          @start-login="beginLogin" 
        />
        <LandingPricing 
          v-else-if="currentPage === 'pricing'" 
          @start-login="beginLogin" 
        />
        <LandingIntegration 
          v-else-if="currentPage === 'integration'" 
          @start-login="beginLogin" 
        />
      </transition>
    </main>

    <!-- Footer -->
    <LandingFooter @navigate="navigate" />
  </div>
</template>

<style scoped>
.showcase-root {
  background: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Glassmorphism Navigation */
.showcase-nav {
  position: sticky;
  top: 0;
  z-index: 50;
  border-bottom: 1px solid var(--border-subtle);
  padding: 1rem 2rem;
  transition: all var(--transition-normal);
}

.glass-nav {
  background: rgba(var(--bg-primary-rgb, 255, 255, 255), 0.7);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

:root[data-theme="dark"] .glass-nav {
  background: rgba(15, 15, 15, 0.7);
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.nav-brand:hover {
  opacity: 0.8;
}

.nav-logo {
  width: 32px;
  height: 32px;
  fill: var(--accent-blue);
}

.nav-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.nav-links {
  display: flex;
  gap: 2rem;
  flex: 1;
  justify-content: center;
}

.nav-link {
  background: none;
  border: none;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  transition: color var(--transition-fast), transform var(--transition-fast);
  padding: 0.5rem;
  position: relative;
}

.nav-link:hover {
  color: var(--text-primary);
}

.nav-link.active {
  color: var(--accent-blue);
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 10%;
  width: 80%;
  height: 2px;
  background-color: var(--accent-blue);
  border-radius: 2px;
}

.nav-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-signin {
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0.5rem 0.75rem;
  transition: color var(--transition-fast);
}

.nav-signin:hover {
  color: var(--accent-blue);
}

.nav-cta {
  background: var(--accent-blue);
  color: #fff;
  border: none;
  border-radius: var(--radius-xl);
  padding: 10px 24px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

.nav-cta:hover {
  background: var(--accent-blue-hover);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.35);
}

/* Page Content */
.page-content {
  flex: 1;
  min-height: calc(100vh - 80px);
}

/* Page Transitions */
.fade-page-enter-active,
.fade-page-leave-active {
  transition: opacity 0.2s ease;
}

.fade-page-enter-from,
.fade-page-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .nav-links {
    display: none;
  }
  
  .showcase-nav {
    padding: 1rem;
  }
}
</style>
