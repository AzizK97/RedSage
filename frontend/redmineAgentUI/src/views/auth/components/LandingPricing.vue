<script setup lang="ts">
import { Check } from "@lucide/vue";

const emit = defineEmits<{
  (event: "start-login"): void;
}>();
</script>

<template>
  <div class="landing-pricing fade-in">
    <section class="pricing-page">
      <div class="section-container">
        <div class="pricing-header">
          <h1 class="pricing-title">Simple, Transparent Pricing</h1>
          <p class="pricing-subtitle">Choose the plan that fits your team's needs and start managing projects with AI power today. No hidden fees, just pure productivity.</p>
        </div>

        <div class="pricing-grid">
          <div class="pricing-card glass-panel interactive-card">
            <h3 class="pricing-name">Starter</h3>
            <div class="pricing-amount">
              <span class="price">$0</span>
              <span class="period">/month</span>
            </div>
            <p class="pricing-desc">Perfect for individuals and small side projects.</p>
            <button @click="$emit('start-login')" class="btn btn-pricing-cta">Get Started</button>
            <hr class="divider" />
            <ul class="pricing-features">
              <li><Check :size="18" class="text-accent" /> Up to 3 active projects</li>
              <li><Check :size="18" class="text-accent" /> 100 AI queries per month</li>
              <li><Check :size="18" class="text-accent" /> Basic task management</li>
              <li><Check :size="18" class="text-accent" /> Email support</li>
            </ul>
          </div>

          <div class="pricing-card pricing-card-featured interactive-card">
            <div class="pricing-badge glow-badge">Most Popular</div>
            <h3 class="pricing-name text-gradient">Professional</h3>
            <div class="pricing-amount">
              <span class="price">$49</span>
              <span class="period">/month</span>
            </div>
            <p class="pricing-desc">The ideal choice for growing professional teams.</p>
            <button @click="$emit('start-login')" class="btn btn-pricing-cta btn-pricing-primary pulse">Get Started</button>
            <hr class="divider" />
            <ul class="pricing-features">
              <li><Check :size="18" class="text-accent" /> Unlimited active projects</li>
              <li><Check :size="18" class="text-accent" /> 10,000 AI queries per month</li>
              <li><Check :size="18" class="text-accent" /> Advanced analytics dashboard</li>
              <li><Check :size="18" class="text-accent" /> Priority support</li>
            </ul>
          </div>

          <div class="pricing-card glass-panel interactive-card">
            <h3 class="pricing-name">Enterprise</h3>
            <div class="pricing-amount">
              <span class="price">Custom</span>
              <span class="period">/month</span>
            </div>
            <p class="pricing-desc">For large organizations with advanced needs.</p>
            <button class="btn btn-pricing-cta">Contact Sales</button>
            <hr class="divider" />
            <ul class="pricing-features">
              <li><Check :size="18" class="text-accent" /> Everything in Pro +</li>
              <li><Check :size="18" class="text-accent" /> Unlimited AI queries</li>
              <li><Check :size="18" class="text-accent" /> SSO & Advanced Security</li>
              <li><Check :size="18" class="text-accent" /> Dedicated support</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-in {
  animation: fadeIn 0.6s ease-out forwards;
}

@keyframes pulseBorder {
  0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(59, 130, 246, 0); }
  100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
}

.pulse {
  animation: pulseBorder 2s infinite;
}

.section-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-xl);
}

.pricing-page {
  padding: 6rem 0;
  min-height: calc(100vh - 80px);
  background: var(--bg-primary);
}

.pricing-header {
  text-align: center;
  margin-bottom: 5rem;
}

.pricing-title {
  margin: 0 0 1rem;
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.pricing-subtitle {
  margin: 0 auto;
  font-size: 1.125rem;
  color: var(--text-secondary);
  max-width: 700px;
  line-height: 1.7;
}

.pricing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
  align-items: start;
}

.glass-panel {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
}

.interactive-card {
  padding: 2.5rem;
  transition: transform var(--transition-normal), box-shadow var(--transition-normal);
  position: relative;
}

.interactive-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
  border-color: var(--accent-blue);
}

.pricing-card-featured {
  background: linear-gradient(180deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
  border: 2px solid var(--accent-blue);
  border-radius: var(--radius-xl);
  box-shadow: 0 16px 40px rgba(59, 130, 246, 0.15);
  transform: scale(1.02);
  z-index: 10;
}

.pricing-card-featured:hover {
  transform: scale(1.02) translateY(-6px);
  box-shadow: 0 20px 40px rgba(59, 130, 246, 0.25);
}

.glow-badge {
  position: absolute;
  top: -14px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(90deg, var(--accent-blue), #60a5fa);
  color: white;
  padding: 6px 20px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.pricing-name {
  margin: 0 0 1rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.text-gradient {
  background: linear-gradient(90deg, var(--accent-blue), #9333ea);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.pricing-amount {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 1rem;
}

.price {
  font-size: 3.5rem;
  font-weight: 900;
  color: var(--text-primary);
  letter-spacing: -0.03em;
}

.period {
  font-size: 1rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.pricing-desc {
  margin: 0 0 2rem;
  font-size: 1rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.btn {
  width: 100%;
  border: none;
  border-radius: var(--radius-xl);
  padding: 14px 16px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-pricing-cta {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
}

.btn-pricing-cta:hover {
  background: var(--border-subtle);
}

.btn-pricing-primary {
  background: var(--accent-blue);
  color: white;
  border: none;
}

.btn-pricing-primary:hover {
  background: var(--accent-blue-hover);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
}

.divider {
  border: none;
  border-top: 1px solid var(--border-subtle);
  margin: 2rem 0;
}

.pricing-features {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.pricing-features li {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1rem;
  color: var(--text-primary);
}

.text-accent {
  color: var(--accent-blue);
  flex-shrink: 0;
}

@media (max-width: 1024px) {
  .pricing-card-featured {
    transform: scale(1);
  }
  .pricing-card-featured:hover {
    transform: translateY(-6px);
  }
}

@media (max-width: 768px) {
  .pricing-title {
    font-size: 2rem;
  }
  .pricing-grid {
    grid-template-columns: 1fr;
  }
}
</style>
