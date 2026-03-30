import { ref } from "vue";

const THREAD_KEY = "thread_id";

export function useThreads() {
  const threadId = ref(localStorage.getItem(THREAD_KEY) || crypto.randomUUID());

  function persist() {
    localStorage.setItem(THREAD_KEY, threadId.value);
  }

  function newThread() {
    threadId.value = crypto.randomUUID();
    persist();
  }

  persist();

  return { threadId, newThread };
}