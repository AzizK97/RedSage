<script setup lang="ts">
import { onMounted } from 'vue';
import { useSession } from '@redsage/ui-core/composables/useSession';

// This component reads the access token from the URL fragment (or query) after
// the backend redirects the user here following OAuth. It persists the
// platform JWT in the SPA session and navigates to the app root.

const { setSession } = useSession();

function parseFragment() {
  const hash = window.location.hash || '';
  const query = window.location.search || '';
  const params = new URLSearchParams(hash.startsWith('#') ? hash.slice(1) : hash);
  if (!params.has('token')) {
    // Fallback to query params
    const q = new URLSearchParams(query.startsWith('?') ? query.slice(1) : query);
    return {
      token: q.get('token') || '',
      full_name: q.get('full_name') || '',
    };
  }
  return {
    token: params.get('token') || '',
    full_name: params.get('full_name') || '',
  };
}

onMounted(() => {
  const { token, full_name } = parseFragment();
  if (!token) {
    // Nothing to do - redirect to root
    window.location.replace('/');
    return;
  }

  try {
    // Try to infer role from token payload in client; if invalid, default to project_manager
    const segments = token.split('.');
    let role: 'admin' | 'project_manager' = 'project_manager';
    if (segments.length >= 2) {
      const payloadSeg = segments[1].replace(/-/g, '+').replace(/_/g, '/');
      const padded = payloadSeg.padEnd(payloadSeg.length + ((4 - (payloadSeg.length % 4)) % 4), '=');
      const payload = JSON.parse(atob(padded)) as { role?: string };
      if (payload.role === 'admin' || payload.role === 'project_manager') {
        role = payload.role;
      }
    }

    setSession(token, role, full_name || '');
  } catch (err) {
    // If parsing fails, still store the token with a default role
    setSession(token, 'project_manager', full_name || '');
  }

  // Clean the URL and navigate to application root
  history.replaceState({}, '', '/');
  window.location.replace('/');
});
</script>

<template>
  <main class="login-shell">
    <section class="login-card">
      <h1>Signing in...</h1>
      <p class="subtitle">Completing sign-in with Redmine. You will be redirected shortly.</p>
    </section>
  </main>
</template>

<style scoped>
.login-shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: var(--bg-primary);
}

.login-card {
  width: min(440px, 100%);
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: var(--space-xl);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}
</style>
