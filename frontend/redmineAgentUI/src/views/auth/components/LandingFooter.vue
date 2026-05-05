<script setup lang="ts">
const emit = defineEmits<{
  (event: "navigate", page: "home" | "features" | "pricing" | "integration"): void;
}>();
</script>

<template>
  <footer class="showcase-footer">
    <div class="section-container">
      <div class="footer-grid">
        <div class="footer-col">
          <div class="footer-brand">
            <svg class="footer-logo" fill="currentColor" height="24" viewBox="0 0 48 48" width="24">
              <path clip-rule="evenodd" d="M24 4H42V17.3333V30.6667H24V44H6V30.6667V17.3333H24V4Z" fill-rule="evenodd"></path>
            </svg>
            <span>ProManager AI</span>
          </div>
          <p class="footer-desc">The most advanced AI assistant for Redmine project management, powered by machine learning and enterprise security.</p>
        </div>

        <div class="footer-col">
          <h4 class="footer-heading">Product</h4>
          <ul class="footer-links">
            <li><button @click="$emit('navigate', 'features')" class="footer-link">Features</button></li>
            <li><button @click="$emit('navigate', 'pricing')" class="footer-link">Pricing</button></li>
            <li><button @click="$emit('navigate', 'integration')" class="footer-link">Integration</button></li>
            <li><a href="#" class="footer-link">Enterprise</a></li>
          </ul>
        </div>

        <div class="footer-col">
          <h4 class="footer-heading">Company</h4>
          <ul class="footer-links">
            <li><a href="#" class="footer-link">About</a></li>
            <li><a href="#" class="footer-link">Blog</a></li>
            <li><a href="#" class="footer-link">Careers</a></li>
          </ul>
        </div>

        <div class="footer-col">
          <h4 class="footer-heading">Legal</h4>
          <ul class="footer-links">
            <li><a href="#" class="footer-link">Privacy</a></li>
            <li><a href="#" class="footer-link">Terms</a></li>
            <li><a href="#" class="footer-link">Security</a></li>
          </ul>
        </div>
      </div>

      <div class="footer-divider"></div>

      <div class="footer-bottom">
        <p class="footer-copyright">© 2026 ProManager AI. All rights reserved.</p>
        <div class="footer-social">
          <a href="#" class="social-link">Twitter</a>
          <a href="#" class="social-link">LinkedIn</a>
          <a href="#" class="social-link">GitHub</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.section-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-xl);
}

.showcase-footer {
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-subtle);
  padding: 6rem 0 3rem;
  color: var(--text-primary);
}

.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 4rem;
  margin-bottom: 4rem;
}

.footer-col {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 0.5rem;
  font-weight: 800;
  font-size: 1.25rem;
  color: var(--text-primary);
}

.footer-logo {
  width: 28px;
  height: 28px;
  fill: var(--accent-blue);
}

.footer-desc {
  margin: 0;
  font-size: 1rem;
  color: var(--text-secondary);
  line-height: 1.6;
  max-width: 320px;
}

.footer-heading {
  margin: 0 0 0.5rem;
  font-size: 0.875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-primary);
}

.footer-links {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.footer-link {
  background: none;
  border: none;
  padding: 0;
  color: var(--text-secondary);
  font-size: 1rem;
  cursor: pointer;
  text-align: left;
  transition: color var(--transition-fast);
  text-decoration: none;
}

.footer-link:hover {
  color: var(--accent-blue);
}

.footer-divider {
  height: 1px;
  background: var(--border-subtle);
  margin: 2rem 0;
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.footer-copyright {
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.footer-social {
  display: flex;
  gap: 1.5rem;
}

.social-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: color var(--transition-fast);
}

.social-link:hover {
  color: var(--accent-blue);
}

@media (max-width: 900px) {
  .footer-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 3rem;
  }
  
  .footer-bottom {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
