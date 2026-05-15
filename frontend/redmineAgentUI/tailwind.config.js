/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './packages/platform/src/**/*.{js,ts,jsx,tsx,vue}',
    './packages/ui-core/src/**/*.{js,ts,jsx,tsx,vue}',
    './packages/plugin-widget/src/**/*.{js,ts,jsx,tsx,vue}',
  ],
  darkMode: ['selector', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        sage: {
          50: 'rgb(var(--sage-50) / <alpha-value>)',
          100: 'rgb(var(--sage-100) / <alpha-value>)',
          200: 'rgb(var(--sage-200) / <alpha-value>)',
          300: 'rgb(var(--sage-300) / <alpha-value>)',
          400: 'rgb(var(--sage-400) / <alpha-value>)',
          500: 'rgb(var(--sage-500) / <alpha-value>)',
          600: 'rgb(var(--sage-600) / <alpha-value>)',
          700: 'rgb(var(--sage-700) / <alpha-value>)',
          800: 'rgb(var(--sage-800) / <alpha-value>)',
          900: 'rgb(var(--sage-900) / <alpha-value>)',
          950: 'rgb(var(--sage-950) / <alpha-value>)',
        },
        copper: {
          50: 'rgb(var(--copper-50) / <alpha-value>)',
          100: 'rgb(var(--copper-100) / <alpha-value>)',
          200: 'rgb(var(--copper-200) / <alpha-value>)',
          300: 'rgb(var(--copper-300) / <alpha-value>)',
          400: 'rgb(var(--copper-400) / <alpha-value>)',
          500: 'rgb(var(--copper-500) / <alpha-value>)',
          600: 'rgb(var(--copper-600) / <alpha-value>)',
          700: 'rgb(var(--copper-700) / <alpha-value>)',
          800: 'rgb(var(--copper-800) / <alpha-value>)',
          900: 'rgb(var(--copper-900) / <alpha-value>)',
          950: 'rgb(var(--copper-950) / <alpha-value>)',
        },
        surface: {
          50: 'rgb(var(--surface-50) / <alpha-value>)',
          100: 'rgb(var(--surface-100) / <alpha-value>)',
          200: 'rgb(var(--surface-200) / <alpha-value>)',
          300: 'rgb(var(--surface-300) / <alpha-value>)',
          400: 'rgb(var(--surface-400) / <alpha-value>)',
          500: 'rgb(var(--surface-500) / <alpha-value>)',
          600: 'rgb(var(--surface-600) / <alpha-value>)',
          700: 'rgb(var(--surface-700) / <alpha-value>)',
          800: 'rgb(var(--surface-800) / <alpha-value>)',
          900: 'rgb(var(--surface-900) / <alpha-value>)',
          950: 'rgb(var(--surface-950) / <alpha-value>)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'float-delayed': 'float 6s ease-in-out 2s infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-up': 'slideUp 0.6s ease-out',
        'slide-up-delayed': 'slideUp 0.6s ease-out 0.15s both',
        'slide-up-delayed-2': 'slideUp 0.6s ease-out 0.3s both',
        'slide-up-delayed-3': 'slideUp 0.6s ease-out 0.45s both',
        'fade-in': 'fadeIn 0.8s ease-out',
        'scale-in': 'scaleIn 0.5s ease-out',
        'glow': 'glow 3s ease-in-out infinite',
        'shimmer': 'shimmer 3s ease-in-out infinite',
        'route-line': 'routeLine 2s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.9)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        glow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(95, 129, 91, 0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(95, 129, 91, 0.6)' },
        },
        shimmer: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        typing: {
          '0%': { width: '0' },
          '50%': { width: '100%' },
          '100%': { width: '0' },
        },
        routeLine: {
          '0%, 100%': { opacity: '0.3' },
          '50%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
};
