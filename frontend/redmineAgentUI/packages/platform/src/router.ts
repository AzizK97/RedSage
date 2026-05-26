import { createRouter, createWebHistory } from 'vue-router';
import { useSession } from '@redsage/ui-core/composables/useSession';
import LandingView from './views/LandingView.vue';
import LoginView from './views/auth/LoginView.vue';
import SignupView from './views/auth/SignupView.vue';
import RedmineCallback from './views/auth/RedmineCallback.vue';
import DashboardView from './views/DashboardView.vue';
import ChatInterface from './components/Dashboard/ChatInterface.vue';
import ProfileView from './components/Dashboard/ProfileView.vue';
import Accessmanagement from './components/Dashboard/Accessmanagement.vue';

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'landing', component: LandingView },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/signup', name: 'signup', component: SignupView },
    { path: '/auth/redmine/callback', name: 'oauth-callback', component: RedmineCallback },
    { path: '/dashboard', name: 'dashboard', component: DashboardView, meta: { requiresAuth: true } },
    { path: '/access-management', name: 'access-management', component: Accessmanagement, meta: { requiresAuth: true, requiresAdmin: true } },
    { path: '/chat', name: 'chat', component: ChatInterface, meta: { requiresAuth: true } },
    { path: '/profile', name: 'profile', component: ProfileView, meta: { requiresAuth: true } },
  ],
});

router.beforeEach((to) => {
  const { isAuthenticated, role } = useSession();

  if (to.name === 'oauth-callback') return true;

  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return { name: 'login', query: { redirect: to.fullPath } };
  }

  if (to.meta.requiresAdmin && role.value !== 'admin') {
    return { name: 'dashboard' };
  }

  if ((to.name === 'landing' || to.name === 'login' || to.name === 'signup') && isAuthenticated.value) {
    return { name: 'dashboard' };
  }

  return true;
});
