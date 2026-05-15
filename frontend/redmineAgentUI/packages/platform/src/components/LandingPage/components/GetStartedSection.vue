<script setup lang="ts">
import { Check } from 'lucide-vue-next';
import AnimatedSection from './AnimatedSection.vue';
import { useTheme } from '@redsage/ui-core/composables/useTheme';

const plans = [
  {
    name: 'Starter',
    price: 'Free',
    period: '',
    desc: 'For individuals and small teams getting started.',
    features: ['Up to 5 users', '1 Redmine project', '100 queries/month', 'Community support', 'Read-only agents'],
    cta: 'Get Started Free',
    ctaClass: 'bg-white dark:bg-surface-800 border border-sage-200 dark:border-surface-700 text-sage-700 dark:text-surface-300 hover:bg-sage-50 dark:hover:bg-surface-700 hover:border-sage-300 dark:hover:border-sage-500/40',
    popular: false,
  },
  {
    name: 'Pro',
    price: '$29',
    period: '/user/mo',
    desc: 'For growing teams that need full AI capabilities.',
    features: ['Unlimited users', 'Unlimited projects', 'Unlimited queries', 'Priority support', 'All 4 agents', 'API access', 'Audit trail', 'Custom workflows'],
    cta: 'Start Free Trial',
    ctaClass: 'bg-copper-600 text-white hover:bg-copper-500 shadow-lg shadow-copper-300/30 dark:shadow-copper-700/25',
    popular: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    desc: 'For organizations with advanced security and compliance needs.',
    features: ['Everything in Pro', 'Self-hosted deployment', 'SSO / SAML', 'SLA guarantee', 'Dedicated support', 'Custom agent training', 'On-premise option'],
    cta: 'Contact Sales',
    ctaClass: 'bg-white dark:bg-surface-800 border border-sage-200 dark:border-surface-700 text-sage-700 dark:text-surface-300 hover:bg-sage-50 dark:hover:bg-surface-700 hover:border-sage-300 dark:hover:border-sage-500/40',
    popular: false,
  },
];

const { isDark } = useTheme();
</script>

<template>
  <section id="pricing" class="relative py-32">
    <div class="absolute inset-0">
      <div class="absolute top-0 left-0 right-0 section-divider" />
      <div class="absolute bottom-1/3 left-1/3 w-96 h-96 bg-sage-100/40 dark:bg-sage-500/5 rounded-full blur-3xl" />
    </div>

    <div class="relative max-w-7xl mx-auto px-6">
      <AnimatedSection class="text-center mb-16">
        <span class="inline-block text-xs font-semibold uppercase tracking-widest text-sage-600 dark:text-sage-400 mb-4">Pricing</span>
        <h2 class="text-4xl sm:text-5xl font-extrabold tracking-tight mb-6 text-sage-950 dark:text-white">
          Start Free, <span class="gradient-text-copper">Scale When Ready</span>
        </h2>
        <p class="text-lg text-surface-600 dark:text-surface-400 max-w-2xl mx-auto">
          No credit card required. Try RedSage on your Redmine instance in minutes.
        </p>
      </AnimatedSection>

      <div class="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto" >
        <AnimatedSection v-for="(plan, i) in plans" :key="plan.name" :delay="100 * i">
          <div :class="['glass-card p-7 h-full flex flex-col relative', 
                        !isDark ? 'bg-white' : 'bg-surface-900',
                        plan.popular ? 'border-copper-300 dark:border-copper-500/40 ring-1 ring-copper-200 dark:ring-copper-500/20' : '',
                      ]">
            <div v-if="plan.popular" class="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full bg-copper-600 text-white text-xs font-semibold">
              Most Popular
            </div>

            <div class="mb-6">
              <h3 class="text-lg font-bold text-sage-900 dark:text-white mb-1">{{ plan.name }}</h3>
              <p class="text-sm text-surface-500 dark:text-surface-400">{{ plan.desc }}</p>
            </div>

            <div class="mb-6">
              <span class="text-4xl font-extrabold text-sage-950 dark:text-white">{{ plan.price }}</span>
              <span class="text-sm text-surface-500 dark:text-surface-400">{{ plan.period }}</span>
            </div>

            <ul class="space-y-2.5 mb-8 flex-1">
              <li v-for="feat in plan.features" :key="feat" class="flex items-start gap-2 text-sm text-surface-600 dark:text-surface-400">
                <Check :size="16" class="text-sage-500 dark:text-sage-400 shrink-0 mt-0.5" />
                {{ feat }}
              </li>
            </ul>

            <a href="#" :class="['block text-center py-3 rounded-xl font-semibold text-sm transition-all', plan.ctaClass]">
              {{ plan.cta }}
            </a>
          </div>
        </AnimatedSection>
      </div>

      <!-- Integration callout
      <AnimatedSection :delay="300" class="mt-16 grid sm:grid-cols-2 gap-6 max-w-3xl mx-auto">
        <div class="glass-card p-6 group transition-all">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-lg bg-copper-50 dark:bg-copper-500/10 border border-copper-100 dark:border-copper-500/15 flex items-center justify-center">
              <Zap :size="20" class="text-copper-600 dark:text-copper-400" />
            </div>
            <h4 class="font-bold text-sage-900 dark:text-white">Quick Setup</h4>
          </div>
          <p class="text-sm text-surface-600 dark:text-surface-400 leading-relaxed">
            Connect your Redmine instance in under 5 minutes. Just API URL, key, and you're live.
          </p>
        </div>
      </AnimatedSection> -->
    </div>
  </section>
</template>
