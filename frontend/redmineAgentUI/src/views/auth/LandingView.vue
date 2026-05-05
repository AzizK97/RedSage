<script setup lang="ts">
import { ChevronRight } from "@lucide/vue";

const emit = defineEmits<{
  (event: "start-login"): void;
}>();

const scrollToFeatures = () => {
  const el = document.getElementById("features");
  el?.scrollIntoView({ behavior: "smooth" });
};

function beginLogin() {
  emit("start-login");
}
</script>

<template>
  <div class="landing-container">
    <!-- Navigation -->
    <nav class="landing-nav">
      <div class="nav-content">
        <div class="nav-logo">
          <div class="logo-icon">RS</div>
          <span class="logo-text">RedSage</span>
        </div>
        <div class="hidden md:flex nav-links">
          <a href="#features" class="nav-link">Features</a>
          <a href="#integration" class="nav-link">Integration</a>
          <a href="#security" class="nav-link">Security</a>
        </div>
        <div class="nav-actions">
          <button class="nav-signin">Sign In</button>
          <button @click="beginLogin" class="nav-cta">Get Started</button>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <!-- Left Column -->
        <div class="hero-copy">
          <div class="hero-badge">
            <span class="badge-icon">✨</span>
            <span class="badge-text">New: Redmine AI Integration</span>
          </div>
          <h1 class="hero-title">
            Master Redmine with
            <br />
            <span class="title-gradient">AI Intelligence</span>
          </h1>
          <p class="hero-description">
            Unlock real-time project insights, automate tracking, and streamline your workflow with an AI assistant built for Redmine. Get 40% more done, faster.
          </p>
          <div class="hero-buttons">
            <button @click="beginLogin" class="btn btn-primary">
              Start Free Trial
            </button>
            <button @click="scrollToFeatures" class="btn btn-secondary">
              View Features
              <ChevronRight :size="18" />
            </button>
          </div>
          <div class="hero-trust">
            <div class="trust-avatars">
              <div class="avatar"></div>
              <div class="avatar"></div>
              <div class="avatar"></div>
            </div>
            <span class="trust-text">Trusted by 500+ teams</span>
          </div>
        </div>

        <!-- Right Column - Dashboard Preview -->
        <div class="hero-preview">
          <div class="preview-card">
            <div class="preview-placeholder">
              <div class="preview-icon">📊</div>
              <p class="preview-label">Dashboard Preview</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Trusted By Section -->
    <section class="trusted-section">
      <div class="trusted-content">
        <p class="trusted-label">TRUSTED BY INNOVATIVE TEAMS</p>
        <div class="trusted-logos">
          <div class="logo">TechCorp</div>
          <div class="logo">Nexus</div>
          <div class="logo">SecureSoft</div>
          <div class="logo">Synergy</div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="features-section">
      <div class="features-header">
        <h2 class="features-title">Transform project data into intelligence</h2>
        <p class="features-subtitle">
          RedSage connects directly with your Redmine to provide real-time visibility and control. AI-powered insights at every level.
        </p>
      </div>

      <div class="features-grid">
        <!-- Feature 1 -->
        <div class="feature-card">
          <div class="feature-icon predictive">📈</div>
          <h3 class="feature-title">Predictive Analytics</h3>
          <p class="feature-description">
            Anticipate bottlenecks before they happen. ML models analyze historical data to forecast delivery dates with 95% accuracy.
          </p>
          <ul class="feature-list">
            <li>✓ AI-driven deadline forecasting</li>
            <li>✓ Automatic risk scoring</li>
            <li>✓ Resource conflict detection</li>
          </ul>
        </div>

        <!-- Feature 2 -->
        <div class="feature-card">
          <div class="feature-icon chat">🤖</div>
          <h3 class="feature-title">Smart Chat Assistant</h3>
          <p class="feature-description">
            Ask natural language questions about your projects. Get instant summaries, status updates, and actionable recommendations.
          </p>
          <ul class="feature-list">
            <li>✓ Instant ticket summaries</li>
            <li>✓ Natural language queries</li>
            <li>✓ Real-time project Q&A</li>
          </ul>
        </div>

        <!-- Feature 3 -->
        <div class="feature-card">
          <div class="feature-icon insights">🎯</div>
          <h3 class="feature-title">Smart Insights</h3>
          <p class="feature-description">
            Real-time dashboards show project health and team performance. Get daily AI briefings highlighting exactly what needs attention.
          </p>
          <ul class="feature-list">
            <li>✓ Live project dashboards</li>
            <li>✓ Team velocity tracking</li>
            <li>✓ Daily AI briefings</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Integration Section -->
    <section id="integration" class="integration-section">
      <div class="integration-content">
        <div class="integration-copy">
          <h2 class="integration-title">Seamless Integration</h2>
          <p class="integration-description">
            We don't replace Redmine—we evolve it. RedSage sits on top of your existing database, meaning no migrations, no data loss, and zero downtime.
          </p>
          <div class="integration-stats">
            <div class="stat">
              <p class="stat-value">15 Min</p>
              <p class="stat-label">Setup Time</p>
            </div>
            <div class="stat">
              <p class="stat-value">100%</p>
              <p class="stat-label">Data Sovereignty</p>
            </div>
            <div class="stat">
              <p class="stat-value">Unlimited</p>
              <p class="stat-label">Projects</p>
            </div>
            <div class="stat">
              <p class="stat-value">SSO</p>
              <p class="stat-label">Enterprise Ready</p>
            </div>
          </div>
        </div>
        <div class="integration-preview">
          <div class="preview-box">
            <div class="preview-icon">🔗</div>
            <p class="preview-label">Secure Integration</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Security Section -->
    <section id="security" class="security-section">
      <div class="security-header">
        <h2 class="security-title">Enterprise Security</h2>
        <p class="security-subtitle">
          Your data stays secure with end-to-end encryption, role-based access control, and compliance with enterprise standards.
        </p>
      </div>
      <div class="security-grid">
        <div class="security-card">
          <div class="security-icon">🔒</div>
          <h3>Encryption</h3>
          <p>End-to-end encrypted data transmission and storage</p>
        </div>
        <div class="security-card">
          <div class="security-icon">👥</div>
          <h3>Access Control</h3>
          <p>Role-based permissions mirroring Redmine structure</p>
        </div>
        <div class="security-card">
          <div class="security-icon">✅</div>
          <h3>Compliance</h3>
          <p>SOC 2 Type II and GDPR compliant</p>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="cta-content">
        <h2 class="cta-title">Ready to transform your project management?</h2>
        <p class="cta-subtitle">
          Join 500+ teams who have upgraded their Redmine experience with AI-powered intelligence and real-time insights.
        </p>
        <div class="cta-buttons">
          <button @click="beginLogin" class="btn btn-light">Get Started Now</button>
          <button class="btn btn-outline">Talk to Sales</button>
        </div>
        <p class="cta-note">No credit card required • 14-day free trial • Cancel anytime</p>
      </div>
    </section>

    <!-- Footer -->
    <footer class="landing-footer">
      <div class="footer-content">
        <div class="footer-grid">
          <div class="footer-col">
            <div class="footer-brand">
              <div class="footer-logo">RS</div>
              <span>RedSage</span>
            </div>
            <p class="footer-description">
              AI-powered Redmine assistant for real project insight. Transform how teams manage complex projects.
            </p>
          </div>
          <div class="footer-col">
            <h4 class="footer-heading">Product</h4>
            <ul class="footer-links">
              <li><a href="#features">Features</a></li>
              <li><a href="#integration">Pricing</a></li>
              <li><a href="#">Enterprise</a></li>
            </ul>
          </div>
          <div class="footer-col">
            <h4 class="footer-heading">Company</h4>
            <ul class="footer-links">
              <li><a href="#">About</a></li>
              <li><a href="#">Blog</a></li>
              <li><a href="#">Careers</a></li>
            </ul>
          </div>
          <div class="footer-col">
            <h4 class="footer-heading">Legal</h4>
            <ul class="footer-links">
              <li><a href="#">Privacy</a></li>
              <li><a href="#">Terms</a></li>
              <li><a href="#">Security</a></li>
            </ul>
          </div>
        </div>
        <div class="footer-divider"></div>
        <div class="footer-bottom">
          <p class="footer-copyright">© 2026 RedSage. All rights reserved.</p>
          <div class="footer-social">
            <a href="#">Twitter</a>
            <a href="#">LinkedIn</a>
            <a href="#">GitHub</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.landing-container {
  background: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
}

/* Navigation */
.landing-nav {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(15, 15, 15, 0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-subtle);
  padding: var(--space-md) var(--space-lg);
}

.nav-content {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-lg);
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--accent-blue), #a855f7);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 14px;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  color: var(--text-primary);
}

.nav-links {
  display: flex;
  gap: var(--space-lg);
  flex: 1;
  justify-content: center;
}

.nav-link {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s;
}

.nav-link:hover {
  color: var(--accent-blue);
}

.nav-actions {
  display: flex;
  gap: var(--space-md);
  align-items: center;
}

.nav-signin {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  padding: 6px 12px;
  transition: color 0.2s;
}

.nav-signin:hover {
  color: var(--accent-blue);
}

.nav-cta {
  background: var(--accent-blue);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

.nav-cta:hover {
  background: var(--accent-blue-hover);
}

.hidden {
  display: none;
}

@media (min-width: 768px) {
  .hidden {
    display: block;
  }
}

/* Hero Section */
.hero-section {
  position: relative;
  padding: var(--space-xl) var(--space-lg);
  background: linear-gradient(135deg, var(--bg-primary), var(--bg-secondary));
  overflow: hidden;
}

.hero-content {
  max-width: 1280px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: var(--space-xl);
  align-items: center;
}

.hero-copy {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  z-index: 10;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm);
  background: rgba(59, 130, 246, 0.1);
  color: var(--accent-blue);
  padding: 8px 16px;
  border-radius: 999px;
  width: fit-content;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.badge-icon {
  font-size: 16px;
}

.hero-title {
  margin: 0;
  font-size: clamp(2.5rem, 5vw, 3.5rem);
  font-weight: 900;
  line-height: 1.1;
  color: var(--text-primary);
}

.title-gradient {
  background: linear-gradient(90deg, var(--accent-blue), #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  margin: 0;
  font-size: 18px;
  color: var(--text-secondary);
  line-height: 1.6;
  max-width: 500px;
}

.hero-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-md);
  margin-top: var(--space-md);
}

.btn {
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: var(--accent-blue);
  color: white;
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
}

.btn-primary:hover {
  background: var(--accent-blue-hover);
  transform: translateY(-2px);
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
}

.btn-secondary:hover {
  background: var(--bg-tertiary);
}

.hero-trust {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding-top: var(--space-md);
}

.trust-avatars {
  display: flex;
  gap: -12px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid var(--bg-primary);
  background: linear-gradient(135deg, var(--accent-blue), #60a5fa);
  margin-right: -12px;
}

.avatar:first-child {
  margin-right: 0;
  background: linear-gradient(135deg, var(--accent-blue), #3b82f6);
}

.avatar:nth-child(2) {
  background: linear-gradient(135deg, #a855f7, #7c3aed);
}

.avatar:nth-child(3) {
  background: linear-gradient(135deg, #ec4899, #be185d);
}

.trust-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
}

/* Hero Preview */
.hero-preview {
  position: relative;
}

.preview-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.5);
}

.preview-placeholder {
  aspect-ratio: 16 / 9;
  background: linear-gradient(135deg, var(--bg-tertiary), var(--bg-secondary));
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
}

.preview-icon {
  font-size: 48px;
}

.preview-label {
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  margin: 0;
}

/* Trusted By */
.trusted-section {
  padding: var(--space-lg);
  border-top: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
}

.trusted-content {
  max-width: 1280px;
  margin: 0 auto;
  text-align: center;
}

.trusted-label {
  margin: 0 0 var(--space-lg);
  font-size: 12px;
  font-weight: bold;
  color: var(--text-secondary);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.trusted-logos {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: var(--space-xl);
  opacity: 0.6;
}

.logo {
  font-weight: bold;
  color: var(--text-primary);
  font-size: 14px;
}

/* Features Section */
.features-section {
  padding: var(--space-xl) var(--space-lg);
  background: var(--bg-primary);
}

.features-header {
  max-width: 1280px;
  margin: 0 auto var(--space-xl);
  text-align: center;
}

.features-title {
  margin: 0 0 var(--space-md);
  font-size: 32px;
  font-weight: 900;
  color: var(--text-primary);
}

.features-subtitle {
  margin: 0;
  font-size: 16px;
  color: var(--text-secondary);
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}

.features-grid {
  max-width: 1280px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--space-lg);
}

.feature-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: var(--space-lg);
  transition: all 0.3s;
}

.feature-card:hover {
  border-color: var(--accent-blue);
  box-shadow: 0 12px 32px rgba(59, 130, 246, 0.2);
}

.feature-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin-bottom: var(--space-lg);
  background: rgba(59, 130, 246, 0.1);
}

.feature-icon.chat {
  background: rgba(168, 85, 247, 0.1);
}

.feature-icon.insights {
  background: rgba(236, 72, 153, 0.1);
}

.feature-title {
  margin: 0 0 var(--space-md);
  font-size: 18px;
  font-weight: bold;
  color: var(--text-primary);
}

.feature-description {
  margin: 0 0 var(--space-md);
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.feature-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.feature-list li {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Integration Section */
.integration-section {
  padding: var(--space-xl) var(--space-lg);
  background: linear-gradient(135deg, var(--bg-secondary), var(--bg-primary));
}

.integration-content {
  max-width: 1280px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-xl);
  align-items: center;
}

.integration-title {
  margin: 0 0 var(--space-lg);
  font-size: 32px;
  font-weight: 900;
  color: var(--text-primary);
}

.integration-description {
  margin: 0 0 var(--space-lg);
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.integration-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-md);
}

.stat {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: var(--space-md);
}

.stat-value {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
  color: var(--accent-blue);
}

.stat-label {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.preview-box {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(168, 85, 247, 0.1));
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 12px;
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
}

.preview-box .preview-icon {
  font-size: 48px;
}

.preview-box .preview-label {
  color: var(--text-secondary);
}

/* Security Section */
.security-section {
  padding: var(--space-xl) var(--space-lg);
  background: var(--bg-primary);
}

.security-header {
  max-width: 1280px;
  margin: 0 auto var(--space-xl);
  text-align: center;
}

.security-title {
  margin: 0 0 var(--space-md);
  font-size: 32px;
  font-weight: 900;
  color: var(--text-primary);
}

.security-subtitle {
  margin: 0;
  font-size: 16px;
  color: var(--text-secondary);
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}

.security-grid {
  max-width: 1280px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-lg);
}

.security-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: var(--space-lg);
  text-align: center;
}

.security-icon {
  font-size: 32px;
  margin-bottom: var(--space-md);
}

.security-card h3 {
  margin: 0 0 var(--space-sm);
  font-size: 16px;
  font-weight: bold;
  color: var(--text-primary);
}

.security-card p {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* CTA Section */
.cta-section {
  padding: var(--space-xl) var(--space-lg);
  background: linear-gradient(135deg, var(--accent-blue), #7c3aed);
}

.cta-content {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.cta-title {
  margin: 0 0 var(--space-lg);
  font-size: 32px;
  font-weight: 900;
  color: white;
}

.cta-subtitle {
  margin: 0 0 var(--space-xl);
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
}

.cta-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.btn-light {
  background: white;
  color: var(--accent-blue);
}

.btn-light:hover {
  background: rgba(255, 255, 255, 0.9);
}

.btn-outline {
  background: transparent;
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: white;
}

.cta-note {
  margin: 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

/* Footer */
.landing-footer {
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-subtle);
  padding: var(--space-xl) var(--space-lg);
  color: var(--text-primary);
}

.footer-content {
  max-width: 1280px;
  margin: 0 auto;
}

.footer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-xl);
  margin-bottom: var(--space-xl);
}

.footer-col {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-md);
}

.footer-logo {
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, var(--accent-blue), #a855f7);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.footer-brand span {
  font-weight: bold;
  color: var(--text-primary);
}

.footer-description {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.footer-heading {
  margin: 0 0 var(--space-md);
  font-size: 12px;
  font-weight: bold;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.footer-links {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.footer-links a {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 13px;
  transition: color 0.2s;
}

.footer-links a:hover {
  color: var(--accent-blue);
}

.footer-divider {
  height: 1px;
  background: var(--border-subtle);
  margin: var(--space-lg) 0;
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-lg);
  flex-wrap: wrap;
}

.footer-copyright {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
}

.footer-social {
  display: flex;
  gap: var(--space-lg);
}

.footer-social a {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 12px;
  transition: color 0.2s;
}

.footer-social a:hover {
  color: var(--accent-blue);
}

/* Responsive */
@media (max-width: 768px) {
  .hero-content {
    grid-template-columns: 1fr;
  }

  .integration-content {
    grid-template-columns: 1fr;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .hero-title {
    font-size: 28px;
  }

  .features-title,
  .integration-title,
  .security-title,
  .cta-title {
    font-size: 24px;
  }

  .nav-links,
  .nav-signin {
    display: none;
  }

  .cta-buttons {
    flex-direction: column;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>


