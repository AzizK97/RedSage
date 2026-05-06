import { createRouter, createWebHistory } from 'vue-router';
import { useSession } from './composables/useSession';
import LandingView from './views/auth/LandingView.vue';
import LoginView from './views/auth/LoginView.vue';
import RedmineCallback from './views/auth/RedmineCallback.vue';
import DashboardView from './views/dashboard/DashboardView.vue';
import ChatInterface from './components/ChatInterface.vue';
import ProfileView from './views/profile/ProfileView.vue';

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'landing', component: LandingView },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/auth/redmine/callback', name: 'oauth-callback', component: RedmineCallback },
    { path: '/dashboard', name: 'dashboard', component: DashboardView, meta: { requiresAuth: true } },
    { path: '/chat', name: 'chat', component: ChatInterface, meta: { requiresAuth: true } },
    { path: '/profile', name: 'profile', component: ProfileView, meta: { requiresAuth: true } },
  ],
});

router.beforeEach((to) => {
  const { isAuthenticated } = useSession();

  if (to.name === 'oauth-callback') return true;

  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return { name: 'login', query: { redirect: to.fullPath } };
  }

  if ((to.name === 'landing' || to.name === 'login') && isAuthenticated.value) {
    return { name: 'dashboard' };
  }

  return true;
});
