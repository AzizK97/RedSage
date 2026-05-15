import { ref, onMounted, onUnmounted, type Ref } from 'vue';

export function useInView(threshold = 0.15): { el: Ref<HTMLElement | null>; isVisible: Ref<boolean> } {
  const el = ref<HTMLElement | null>(null);
  const isVisible = ref(false);

  let observer: IntersectionObserver | null = null;

  onMounted(() => {
    if (!el.value) return;
    observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          isVisible.value = true;
          observer?.disconnect();
        }
      },
      { threshold }
    );
    observer.observe(el.value);
  });

  onUnmounted(() => observer?.disconnect());

  return { el, isVisible };
}
