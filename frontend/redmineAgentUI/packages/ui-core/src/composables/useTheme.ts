import { ref, onMounted } from 'vue';

const isDark = ref(true);
let _initialized = false;

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

const initTheme = () => {
  if (_initialized) return;
  _initialized = true;
  try {
    const savedTheme = typeof localStorage !== 'undefined' ? localStorage.getItem('showcase-theme') : null;
    const prefersDark = typeof window !== 'undefined' ? window.matchMedia('(prefers-color-scheme: dark)').matches : true;
    const theme = savedTheme ? savedTheme === 'dark' : prefersDark;
    applyTheme(theme);
  } catch (e) {
    /* noop in SSR */
  }
};

export function useTheme() {
  onMounted(() => {
    initTheme();
  });

  const toggleTheme = () => {
    applyTheme(!isDark.value);
  };

  return { isDark, toggleTheme, initTheme };
}
