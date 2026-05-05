<script setup lang="ts">
import { Play, Check } from "@lucide/vue";

const emit = defineEmits<{
  (event: "start-login"): void;
  (event: "navigate", page: "features"): void;
}>();
</script>

<template>
  <div class="landing-home fade-in">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-container">
        <div class="hero-left">
          <div class="hero-badge">
            <span class="badge-icon">✨</span>
            <span class="badge-text" style="color: white;">New: Redmine AI Integration</span>
          </div>
          <h1 class="hero-title">
            Master Redmine with <br/>
            <span class="title-accent">AI Intelligence</span>
          </h1>
          <p class="hero-description">
            Unlock real-time project insights, automate tracking, and streamline your workflow with the most advanced AI assistant for Redmine. Experience a 40% boost in team productivity.
          </p>
          <div class="hero-buttons">
            <button @click="$emit('start-login')" class="btn btn-primary">
              Start Free Trial
            </button>
            <button @click="$emit('navigate', 'features')" class="btn btn-secondary">
              <Play :size="18" />
              View Demo
            </button>
          </div>
          <div class="hero-trust">
            <div class="avatar-group">
              <div class="avatar avatar-1"></div>
              <div class="avatar avatar-2"></div>
              <div class="avatar avatar-3"></div>
            </div>
            <span class="trust-text">Joined by 2,000+ teams this month</span>
          </div>
        </div>

        <div class="hero-preview floating-animation">
          <div class="preview-card glass-panel">
            <img alt="ProManager AI Dashboard" class="preview-image" src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&h=400&fit=crop" />
          </div>
        </div>
      </div>
    </section>

    <!-- Trusted By Section -->
    <section class="trusted-section">
      <div class="section-container">
        <p class="trusted-label">TRUSTED BY INNOVATIVE TEAMS WORLDWIDE</p>
        <div class="trusted-logos">
          <div class="company-logo gradient-text-subtle">TechCorp</div>
          <div class="company-logo gradient-text-subtle">Nexus</div>
          <div class="company-logo gradient-text-subtle">SecureSoft</div>
          <div class="company-logo gradient-text-subtle">Synergy</div>
          <div class="company-logo gradient-text-subtle">Orbital</div>
        </div>
      </div>
    </section>

    <!-- Features Overview -->
    <section class="features-overview">
      <div class="section-container">
        <div class="section-header">
          <h2 class="section-title">Transform your project data into intelligence</h2>
          <p class="section-subtitle">ProManager AI connects directly with your Redmine instance to provide unparalleled visibility and control over complex software projects.</p>
        </div>

        <div class="features-grid">
          <div class="feature-card interactive-card">
            <div class="feature-icon bg-icon-blue">📈</div>
            <h3 class="feature-title">Predictive Analytics</h3>
            <p class="feature-text">Anticipate bottlenecks before they happen with our machine learning models. We analyze historical data to forecast delivery dates with 95% accuracy.</p>
          </div>

          <div class="feature-card interactive-card">
            <div class="feature-icon bg-icon-green">🤖</div>
            <h3 class="feature-title">Automated Workflows</h3>
            <p class="feature-text">Let AI handle status updates and repetitive reporting tasks automatically. Focus on building while our assistant keeps documentation in sync.</p>
          </div>

          <div class="feature-card interactive-card">
            <div class="feature-icon bg-icon-amber">🎯</div>
            <h3 class="feature-title">Smart Insights</h3>
            <p class="feature-text">Get real-time summaries of project health and team performance. Receive daily AI briefings that highlight exactly what needs your attention.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Visibility Section -->
    <section class="visibility-section">
      <div class="section-container">
        <div class="visibility-grid">
          <div class="visibility-left">
            <div class="visibility-image hover-zoom glass-panel">
              <img alt="Modern office workspace" src="https://images.unsplash.com/photo-1552664730-d307ca884978?w=500&h=400&fit=crop" />
            </div>
          </div>

          <div class="visibility-right">
            <h2 class="visibility-title">Visibility at every level</h2>
            <div class="visibility-items">
              <div class="visibility-item">
                <div class="check-container">
                  <Check :size="18" class="check-icon" />
                </div>
                <div>
                  <h4 class="item-title">Resource Optimization</h4>
                  <p class="item-text">Intelligently allocate team members based on capacity and skill set without manual spreadsheets.</p>
                </div>
              </div>

              <div class="visibility-item">
                <div class="check-container">
                  <Check :size="18" class="check-icon" />
                </div>
                <div>
                  <h4 class="item-title">Automated Risk Detection</h4>
                  <p class="item-text">Early warning system for scope creep and deadline slippage based on real-time commit activity.</p>
                </div>
              </div>

              <div class="visibility-item">
                <div class="check-container">
                  <Check :size="18" class="check-icon" />
                </div>
                <div>
                  <h4 class="item-title">Stakeholder Reporting</h4>
                  <p class="item-text">Generate executive-ready summaries with a single click, translated from technical jargon to business value.</p>
                </div>
              </div>
            </div>

            <button class="btn btn-outline glow-on-hover">Explore Enterprise Solutions</button>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section glow-bg">
      <div class="section-container">
        <div class="cta-content glass-panel-strong">
          <h2 class="cta-title">Ready to transform your project management?</h2>
          <p class="cta-subtitle">Join thousands of project managers who have already upgraded their Redmine experience with AI-powered intelligence.</p>
          <div class="cta-buttons">
            <button @click="$emit('start-login')" class="btn btn-primary-bright pulse">Get Started Now</button>
            <button class="btn btn-outline-light">Talk to Sales</button>
          </div>
          <p class="cta-note">No credit card required • 14-day free trial • Cancel anytime</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* Keyframes */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-12px); }
  100% { transform: translateY(0px); }
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(59, 130, 246, 0); }
  100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
}

.fade-in {
  animation: fadeIn 0.6s ease-out forwards;
}

.floating-animation {
  animation: float 6s ease-in-out infinite;
}

.pulse {
  animation: pulse 2s infinite;
}

/* Glass and Modern UI Utilities */
.glass-panel {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--card-shadow);
}

.glass-panel-strong {
  background: var(--bg-tertiary);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--accent-blue);
  border-radius: var(--radius-xl);
  padding: 3rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.interactive-card {
  transition: transform var(--transition-normal), box-shadow var(--transition-normal);
}

.interactive-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 30px rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.4);
}

.hover-zoom img {
  transition: transform 0.5s ease;
}

.hover-zoom:hover img {
  transform: scale(1.03);
}

.glow-bg {
  background: radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.1) 0%, var(--bg-primary) 70%);
}

.title-accent {
  background: linear-gradient(90deg, var(--accent-blue), #9333ea);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
}

.gradient-text-subtle {
  background: linear-gradient(90deg, var(--text-secondary), var(--text-primary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Layout */
.section-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-xl);
}

/* Hero */
.hero-section {
  padding: 6rem var(--space-xl) 4rem;
  background: radial-gradient(circle at top left, rgba(59, 130, 246, 0.08) 0%, transparent 40%), var(--bg-primary);
}

.hero-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 4rem;
  align-items: center;
}

.hero-left {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm);
  background: linear-gradient(90deg, var(--accent-blue), #8b5cf6);
  padding: 8px 16px;
  border-radius: 999px;
  width: fit-content;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
}

.hero-title {
  margin: 0;
  font-size: 3.5rem;
  font-weight: 800;
  line-height: 1.15;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.hero-description {
  margin: 0;
  font-size: 1.125rem;
  color: var(--text-secondary);
  line-height: 1.6;
  max-width: 500px;
}

.hero-buttons {
  display: flex;
  gap: var(--space-md);
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
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  letter-spacing: 0.02em;
}

.btn-primary {
  background: var(--accent-blue);
  color: #fff;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-primary:hover {
  background: var(--accent-blue-hover);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
}

.btn-primary-bright {
  background: linear-gradient(135deg, var(--accent-blue), #60a5fa);
  color: #ffffff;
  border: 1px solid rgba(255,255,255,0.2);
}

.btn-primary-bright:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4);
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

.btn-outline {
  background: transparent;
  color: var(--text-primary);
  border: 2px solid var(--accent-blue);
}

.btn-outline:hover {
  background: rgba(59, 130, 246, 0.1);
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.2);
}

.btn-outline-light {
  background: transparent;
  color: var(--text-primary);
  border: 2px solid var(--border-subtle);
}

.btn-outline-light:hover {
  background: var(--bg-secondary);
  border-color: var(--text-secondary);
}

.hero-trust {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding-top: var(--space-sm);
}

.avatar-group {
  display: flex;
  margin-right: -12px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid var(--bg-primary);
  margin-right: -12px;
}

.avatar-1 { background: linear-gradient(135deg, #60a5fa, #3b82f6); }
.avatar-2 { background: linear-gradient(135deg, #a855f7, #7c3aed); }
.avatar-3 { background: linear-gradient(135deg, #10b981, #059669); }

.trust-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
}

/* Preview */
.hero-preview {
  position: relative;
  z-index: 10;
}

.preview-card {
  padding: 8px;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  height: auto;
  border-radius: calc(var(--radius-xl) - 4px);
  object-fit: cover;
}

/* Trusted */
.trusted-section {
  padding: 3rem var(--space-xl);
  border-top: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
}

.trusted-label {
  margin: 0 0 var(--space-lg);
  font-size: 12px;
  font-weight: 700;
  color: var(--text-secondary);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  text-align: center;
}

.trusted-logos {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 3rem;
  opacity: 0.7;
}

.company-logo {
  font-weight: 800;
  font-size: 1.25rem;
  letter-spacing: -0.03em;
}

/* Features */
.features-overview {
  padding: 6rem var(--space-xl);
  background: var(--bg-primary);
}

.section-header {
  text-align: center;
  margin-bottom: 4rem;
}

.section-title {
  margin: 0 0 var(--space-md);
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.section-subtitle {
  margin: 0 auto;
  font-size: 1.125rem;
  color: var(--text-secondary);
  max-width: 650px;
  line-height: 1.7;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 2.5rem;
}

.feature-icon {
  font-size: 2rem;
  margin-bottom: 1.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
}

.bg-icon-blue { background: rgba(59, 130, 246, 0.1); color: var(--accent-blue); }
.bg-icon-green { background: rgba(16, 185, 129, 0.1); color: var(--accent-green); }
.bg-icon-amber { background: rgba(245, 158, 11, 0.1); color: var(--accent-amber); }

.feature-title {
  margin: 0 0 1rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.feature-text {
  margin: 0;
  font-size: 1rem;
  color: var(--text-secondary);
  line-height: 1.7;
}

/* Visibility */
.visibility-section {
  padding: 6rem var(--space-xl);
  background: var(--bg-secondary);
}

.visibility-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
}

.visibility-image {
  border-radius: var(--radius-xl);
  overflow: hidden;
  padding: 8px;
}

.visibility-image img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: calc(var(--radius-xl) - 4px);
}

.visibility-title {
  margin: 0 0 2rem;
  font-size: 2.25rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.visibility-items {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.visibility-item {
  display: flex;
  gap: 1rem;
}

.check-container {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 4px;
}

.check-icon {
  color: var(--accent-blue);
}

.item-title {
  margin: 0 0 0.25rem;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.item-text {
  margin: 0;
  font-size: 1rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* CTA */
.cta-section {
  padding: 6rem var(--space-xl);
  text-align: center;
}

.cta-content {
  max-width: 800px;
  margin: 0 auto;
}

.cta-title {
  margin: 0 0 1.5rem;
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.cta-subtitle {
  margin: 0 0 2.5rem;
  font-size: 1.125rem;
  color: var(--text-secondary);
  line-height: 1.7;
}

.cta-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.cta-note {
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .hero-container,
  .visibility-grid {
    grid-template-columns: 1fr;
  }
  .hero-title {
    font-size: 2.5rem;
  }
  .cta-title, .section-title, .visibility-title {
    font-size: 2rem;
  }
  .btn {
    width: 100%;
  }
}
</style>
