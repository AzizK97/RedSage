<script setup lang="ts">
const emit = defineEmits<{
  (event: "start-login"): void;
}>();
</script>

<template>
  <div class="landing-features fade-in">
    <section class="features-page bg-grid">
      <div class="section-container">
        <div class="page-header">
          <div class="badge-section">
            <span class="page-badge">Platform Features</span>
          </div>
          <h1 class="page-title">The Future of Redmine is AI-Powered</h1>
          <p class="page-description">ProManager AI transforms your legacy Redmine environment into a high-performance engine using machine learning and intuitive automation tools.</p>
        </div>

        <div class="features-showcase">
          <div class="feature-showcase-card glass-panel interactive-card">
            <div class="feature-number">1</div>
            <h3 class="feature-name">Real-time Analytics Dashboard</h3>
            <p class="feature-detail">Visualize project metrics, team performance, and predictive insights in a single unified dashboard that updates in real-time.</p>
            <div class="feature-tags">
              <span class="tag">Analytics</span>
              <span class="tag">Dashboard</span>
              <span class="tag">Real-time</span>
            </div>
          </div>

          <div class="feature-showcase-card glass-panel interactive-card">
            <div class="feature-number">2</div>
            <h3 class="feature-name">Intelligent Task Distribution</h3>
            <p class="feature-detail">Automatically assign tasks based on team member skills, current workload, and historical performance patterns.</p>
            <div class="feature-tags">
              <span class="tag">AI</span>
              <span class="tag">Automation</span>
              <span class="tag">Optimization</span>
            </div>
          </div>

          <div class="feature-showcase-card glass-panel interactive-card">
            <div class="feature-number">3</div>
            <h3 class="feature-name">Predictive Deadline Alerts</h3>
            <p class="feature-detail">Get early warnings about potential deadline misses with ML-powered forecasting and recommended mitigation strategies.</p>
            <div class="feature-tags">
              <span class="tag">Prediction</span>
              <span class="tag">Alerts</span>
              <span class="tag">Risk</span>
            </div>
          </div>

          <div class="feature-showcase-card glass-panel interactive-card">
            <div class="feature-number">4</div>
            <h3 class="feature-name">Automated Reporting</h3>
            <p class="feature-detail">Generate executive summaries, status reports, and stakeholder updates automatically with customizable templates.</p>
            <div class="feature-tags">
              <span class="tag">Reports</span>
              <span class="tag">Automation</span>
              <span class="tag">Templates</span>
            </div>
          </div>
        </div>

        <div class="cta-wrap">
          <button @click="$emit('start-login')" class="btn btn-primary pulse-btn">Start Free Trial</button>
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

.bg-grid {
  background-size: 40px 40px;
  background-image: linear-gradient(to right, rgba(128, 128, 128, 0.05) 1px, transparent 1px),
                    linear-gradient(to bottom, rgba(128, 128, 128, 0.05) 1px, transparent 1px);
}

.section-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-xl);
}

.features-page {
  padding: 6rem 0;
  min-height: calc(100vh - 80px);
}

.page-header {
  text-align: center;
  margin-bottom: 4rem;
}

.page-badge {
  display: inline-block;
  background: rgba(59, 130, 246, 0.1);
  color: var(--accent-blue);
  padding: 6px 16px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.page-title {
  margin: 0 0 1rem;
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.page-description {
  margin: 0 auto;
  font-size: 1.125rem;
  color: var(--text-secondary);
  max-width: 650px;
  line-height: 1.7;
}

.features-showcase {
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
  border-color: rgba(59, 130, 246, 0.5);
}

.feature-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--accent-blue), #60a5fa);
  color: white;
  font-weight: 800;
  font-size: 1.25rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.feature-name {
  margin: 0 0 1rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.feature-detail {
  margin: 0 0 1.5rem;
  font-size: 1rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.feature-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  padding: 4px 12px;
  border-radius: var(--radius-lg);
  font-size: 12px;
  font-weight: 600;
  border: 1px solid var(--border-subtle);
}

.cta-wrap {
  text-align: center;
}

.btn {
  border: none;
  border-radius: var(--radius-xl);
  padding: 14px 32px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary {
  background: var(--accent-blue);
  color: white;
}

.btn-primary:hover {
  background: var(--accent-blue-hover);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.pulse-btn:active {
  transform: scale(0.98);
}

@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }
}
</style>
