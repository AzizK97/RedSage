/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        sage: {
          50: '#f4f7f4',
          100: '#e0e8df',
          200: '#c3d1c1',
          300: '#a1b49e',
          400: '#7d9a79',
          500: '#5f815b',
          600: '#4a6847',
          700: '#3c5439',
          800: '#324530',
          900: '#2a3a28',
          950: '#141d13',
        },
        copper: {
          50: '#fdf6f0',
          100: '#f9e6d4',
          200: '#f2c9a4',
          300: '#e9a66e',
          400: '#e0853f',
          500: '#d4692a',
          600: '#b8501f',
          700: '#993d1b',
          800: '#7d331d',
          900: '#6a2c1b',
          950: '#3b150c',
        },
        surface: {
          50: '#f6f7f5',
          100: '#eef0eb',
          200: '#dde1d8',
          300: '#c4cbbf',
          400: '#a3ad9c',
          500: '#87907e',
          600: '#6d7567',
          700: '#585f53',
          800: '#3a3f35',
          900: '#1e211b',
          950: '#0e100c',
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
  plugins: [],
};
