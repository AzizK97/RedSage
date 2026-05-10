import { ref, onMounted } from 'vue';

export function useTheme() {
  const isDark = ref(true);

  const initTheme = () => {
    const savedTheme = typeof localStorage !== 'undefined' ? localStorage.getItem('showcase-theme') : null;
    const prefersDark = typeof window !== 'undefined' ? window.matchMedia('(prefers-color-scheme: dark)').matches : true;
    
    const theme = savedTheme ? savedTheme === 'dark' : prefersDark;
    isDark.value = theme;
    applyTheme(theme);
  };

  const applyTheme = (dark: boolean) => {
    isDark.value = dark;
    try {
      if (dark) {
        document.documentElement.setAttribute('data-theme', 'dark');
      } else {
        document.documentElement.removeAttribute('data-theme');
      }
      localStorage.setItem('showcase-theme', dark ? 'dark' : 'light');
    } catch (e) {
      /* noop in SSR */
    }
  };

  const toggleTheme = () => {
    applyTheme(!isDark.value);
  };

  onMounted(() => {
    initTheme();
  });

  return { isDark, toggleTheme, initTheme };
}
