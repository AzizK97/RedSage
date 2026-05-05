<script setup lang="ts">
const emit = defineEmits<{
  (event: "start-login"): void;
}>();
</script>

<template>
  <div class="landing-integration fade-in">
    <section class="integration-page">
      <div class="section-container">
        <div class="integration-header">
          <span class="integration-badge glow-badge">Enterprise Integration</span>
          <h1 class="integration-title">Seamless Redmine Integration for Your Workflow</h1>
          <p class="integration-description">Connect your Redmine account via secure API keys and enjoy real-time project synchronization with enterprise-grade encryption.</p>
          <div class="integration-buttons">
            <button @click="$emit('start-login')" class="btn btn-primary">Get Started</button>
            <button class="btn btn-secondary">Watch Demo</button>
          </div>
        </div>

        <div class="integration-features">
          <div class="integration-feature glass-panel interactive-card">
            <div class="integration-icon icon-bg-blue">🔗</div>
            <h3 class="integration-feature-title">API-First Connection</h3>
            <p class="integration-feature-text">Easily connect using your personal or admin API access key. No password sharing required, maintaining full control over your credentials.</p>
          </div>

          <div class="integration-feature glass-panel interactive-card">
            <div class="integration-icon icon-bg-green">🔒</div>
            <h3 class="integration-feature-title">Enterprise Security</h3>
            <p class="integration-feature-text">State-of-the-art AES-256 encryption protects your data both in transit and at rest, meeting global compliance standards for data safety.</p>
          </div>

          <div class="integration-feature glass-panel interactive-card">
            <div class="integration-icon icon-bg-amber">🔄</div>
            <h3 class="integration-feature-title">Real-time Sync</h3>
            <p class="integration-feature-text">Bidirectional updates ensure that changes in Redmine or our platform reflect instantly, keeping your entire team on the same page.</p>
          </div>
        </div>

        <div class="how-it-works glass-panel-strong">
          <h2 class="how-title">How It Works</h2>
          <p class="how-subtitle">Set up your connection in three simple steps</p>

          <div class="steps-grid">
            <div class="step">
              <div class="step-number gradient-circle">1</div>
              <h4 class="step-title">Generate API Key</h4>
              <p class="step-text">Navigate to 'My Account' in your Redmine instance and generate your unique API access token securely.</p>
            </div>

            <div class="step">
              <div class="step-divider"></div>
              <div class="step-number gradient-circle">2</div>
              <h4 class="step-title">Connect Account</h4>
              <p class="step-text">Paste your API key in our secure connection form. No passwords stored, only encrypted tokens.</p>
            </div>

            <div class="step">
              <div class="step-divider"></div>
              <div class="step-number gradient-circle">3</div>
              <h4 class="step-title">Start Syncing</h4>
              <p class="step-text">Your Redmine data syncs automatically. Start using ProManager AI immediately with full access to your projects.</p>
            </div>
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

.section-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-xl);
}

.integration-page {
  padding: 6rem 0;
  min-height: calc(100vh - 80px);
  background: var(--bg-primary);
}

.integration-header {
  text-align: center;
  margin-bottom: 5rem;
}

.integration-badge {
  display: inline-block;
  background: rgba(59, 130, 246, 0.1);
  color: var(--accent-blue);
  padding: 6px 16px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 1.5rem;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.glow-badge {
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.2);
}

.integration-title {
  margin: 0 0 1.5rem;
  font-size: 2.75rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.integration-description {
  margin: 0 auto 2.5rem;
  font-size: 1.125rem;
  color: var(--text-secondary);
  max-width: 650px;
  line-height: 1.7;
}

.integration-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  border: none;
  border-radius: var(--radius-xl);
  padding: 14px 28px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary {
  background: var(--accent-blue);
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-primary:hover {
  background: var(--accent-blue-hover);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
}

.btn-secondary:hover {
  background: var(--bg-tertiary);
  border-color: var(--text-secondary);
}

.integration-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 4rem;
}

.glass-panel {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 2.5rem;
}

.interactive-card {
  transition: transform var(--transition-normal), box-shadow var(--transition-normal);
}

.interactive-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
  border-color: var(--accent-blue);
}

.integration-icon {
  font-size: 2.5rem;
  margin-bottom: 1.5rem;
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
}

.icon-bg-blue { background: rgba(59, 130, 246, 0.1); color: var(--accent-blue); }
.icon-bg-green { background: rgba(16, 185, 129, 0.1); color: var(--accent-green); }
.icon-bg-amber { background: rgba(245, 158, 11, 0.1); color: var(--accent-amber); }

.integration-feature-title {
  margin: 0 0 1rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.integration-feature-text {
  margin: 0;
  font-size: 1rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.glass-panel-strong {
  background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 4rem 3rem;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.how-title {
  margin: 0 0 1rem;
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--text-primary);
}

.how-subtitle {
  margin: 0 0 3.5rem;
  font-size: 1.125rem;
  color: var(--text-secondary);
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  position: relative;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 2;
}

.step-divider {
  display: none;
}

.gradient-circle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-blue), #60a5fa);
  color: white;
  font-size: 1.75rem;
  font-weight: 800;
  margin-bottom: 1.5rem;
  border: 4px solid var(--bg-primary);
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
}

.step-title {
  margin: 0 0 1rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.step-text {
  margin: 0;
  font-size: 1rem;
  color: var(--text-secondary);
  line-height: 1.6;
  max-width: 300px;
}

/* Connecting lines between steps for desktop */
@media (min-width: 900px) {
  .steps-grid::before {
    content: '';
    position: absolute;
    top: 32px;
    left: 16%;
    right: 16%;
    height: 2px;
    background: var(--border-subtle);
    z-index: 1;
  }
}

@media (max-width: 899px) {
  .steps-grid {
    grid-template-columns: 1fr;
    gap: 3rem;
  }
  
  .step-text {
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .integration-title,
  .how-title {
    font-size: 2rem;
  }
}
</style>
