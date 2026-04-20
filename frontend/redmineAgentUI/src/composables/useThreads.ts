import { computed, ref } from "vue";
import type { Message } from "../types";
import { callCreateThreadAPI, callDeleteThreadAPI, callListThreadsAPI, type ThreadSummary as ApiThreadSummary } from "../api/client";

export interface ConversationSummary {
  id: string;
  title: string;
  preview: string;
  updatedAt: number;
}

function safeParse<T>(raw: string | null, fallback: T): T {
  if (!raw) return fallback;

  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function sortConversations(items: ConversationSummary[]) {
  return [...items].sort((a, b) => b.updatedAt - a.updatedAt);
}

export function useThreads(token: string, storageScope: string) {
  const MESSAGES_STORAGE_KEY = `${storageScope}:redmine-chat-messages`;
  const ACTIVE_THREAD_KEY = `${storageScope}:redmine-chat-active-thread`;
  const CONVERSATIONS_STORAGE_KEY = `${storageScope}:redmine-chat-conversations`;

  const conversations = ref<ConversationSummary[]>([]);
  const messagesByThread = ref<Record<string, Message[]>>({});
  const activeThreadId = ref("");

  function persistMessages() {
    localStorage.setItem(MESSAGES_STORAGE_KEY, JSON.stringify(messagesByThread.value));
    localStorage.setItem(ACTIVE_THREAD_KEY, activeThreadId.value);
  }

  function persistActiveThread() {
    localStorage.setItem(ACTIVE_THREAD_KEY, activeThreadId.value);
  }

  function persistConversations() {
    localStorage.setItem(CONVERSATIONS_STORAGE_KEY, JSON.stringify(conversations.value));
  }

  function mapApiThread(item: ApiThreadSummary): ConversationSummary {
    return {
      id: item.id,
      title: item.title,
      preview: item.preview,
      updatedAt: item.updatedAt,
    };
  }

  function syncMessageStoreWithConversations() {
    const validThreadIds = new Set(conversations.value.map((conversation) => conversation.id));
    const currentThreadId = activeThreadId.value;

    const nextMessages: Record<string, Message[]> = {};
    for (const [threadId, messages] of Object.entries(messagesByThread.value)) {
      if (validThreadIds.has(threadId) || threadId === currentThreadId) {
        nextMessages[threadId] = messages;
      }
    }

    messagesByThread.value = nextMessages;
  }

  function buildConversationsFromMessages(): ConversationSummary[] {
    return Object.entries(messagesByThread.value)
      .map(([threadId, messages]) => {
        const latest = messages[messages.length - 1];
        return {
          id: threadId,
          title: "New conversation",
          preview: latest?.content?.slice(0, 70) || "No messages yet",
          updatedAt: latest?.timestamp || Date.now(),
        };
      })
      .sort((a, b) => b.updatedAt - a.updatedAt);
  }

  async function refreshThreads(preferredThreadId?: string) {
    const currentLocalConversations = conversations.value;
    const fallbackFromMessages = buildConversationsFromMessages();

    try {
      const items = await callListThreadsAPI(token);
      if (items.length > 0) {
        conversations.value = sortConversations(items.map(mapApiThread));
        syncMessageStoreWithConversations();
        persistConversations();
      } else {
        conversations.value = currentLocalConversations.length > 0
          ? currentLocalConversations
          : fallbackFromMessages;
      }
    } catch {
      conversations.value = currentLocalConversations.length > 0
        ? currentLocalConversations
        : fallbackFromMessages;
    }

    const preferred = preferredThreadId?.trim();
    const storedActive = localStorage.getItem(ACTIVE_THREAD_KEY);
    const currentActive = activeThreadId.value;

    const candidates = [preferred, currentActive, storedActive].filter(
      (candidate): candidate is string => !!candidate,
    );

    const nextActive = candidates.find((candidate) =>
      conversations.value.some((conversation) => conversation.id === candidate),
    );

    if (nextActive) {
      activeThreadId.value = nextActive;
    } else if (conversations.value.length > 0) {
      activeThreadId.value = conversations.value[0].id;
    } else {
      activeThreadId.value = "";
    }

    persistActiveThread();
    persistMessages();
  }

  const savedMessages = safeParse<Record<string, Message[]>>(
    localStorage.getItem(MESSAGES_STORAGE_KEY),
    {},
  );
  const savedConversations = safeParse<ConversationSummary[]>(
    localStorage.getItem(CONVERSATIONS_STORAGE_KEY),
    [],
  );
  messagesByThread.value = savedMessages;
  conversations.value = sortConversations(savedConversations);

  void refreshThreads();

  const currentConversation = computed(() =>
    conversations.value.find((conversation) => conversation.id === activeThreadId.value) ?? null,
  );

  function setActiveThread(threadId: string) {
    activeThreadId.value = threadId;
    persistActiveThread();
  }

  async function createThread() {
    const { thread_id } = await callCreateThreadAPI(token);
    messagesByThread.value[thread_id] = [];
    activeThreadId.value = thread_id;
    persistMessages();
    await refreshThreads(thread_id);
    activeThreadId.value = thread_id;
    persistActiveThread();
    persistConversations();
    return thread_id;
  }

  function getMessages(threadId: string) {
    return (messagesByThread.value[threadId] ?? []).map((message) => ({ ...message }));
  }

  function saveMessages(threadId: string, messages: Message[]) {
    messagesByThread.value[threadId] = messages.map((message) => ({ ...message }));
    persistMessages();
  }

  function renameThread(threadId: string, title: string) {
    conversations.value = conversations.value.map((conversation) =>
      conversation.id === threadId
        ? { ...conversation, title, updatedAt: Date.now() }
        : conversation,
    );
    persistConversations();
    persistMessages();
  }

  async function deleteThread(threadId: string) {
    // First attempt backend deletion
    let deleteSuccess = false;
    try {
      console.log(`[deleteThread] Calling backend DELETE for thread: ${threadId}`);
      await callDeleteThreadAPI(threadId, token);
      console.log(`[deleteThread] ✅ Backend delete successful for thread: ${threadId}`);
      deleteSuccess = true;
    } catch (error) {
      console.error(`[deleteThread] ❌ Backend delete failed for thread ${threadId}:`, error);
      // Re-throw to let component handle the error
      throw new Error(`Failed to delete thread on server: ${error instanceof Error ? error.message : String(error)}`);
    }

    // Only remove from local state if backend deletion succeeded
    if (deleteSuccess) {
      conversations.value = conversations.value.filter((conversation) => conversation.id !== threadId);

      const nextMessages = { ...messagesByThread.value };
      delete nextMessages[threadId];
      messagesByThread.value = nextMessages;

      if (activeThreadId.value === threadId) {
        if (conversations.value.length > 0) {
          activeThreadId.value = conversations.value[0].id;
        } else {
          activeThreadId.value = "";
        }
      }

      syncMessageStoreWithConversations();
      persistConversations();
      persistMessages();
      console.log(`[deleteThread] ✅ Local state cleaned for thread: ${threadId}`);
    }
  }

  async function loadThreads() {
    await refreshThreads();
  }

  return {
    conversations,
    activeThreadId,
    currentConversation,
    setActiveThread,
    createThread,
    loadThreads,
    getMessages,
    saveMessages,
    renameThread,
    deleteThread,
  };
}

export type ThreadsStore = ReturnType<typeof useThreads>;
