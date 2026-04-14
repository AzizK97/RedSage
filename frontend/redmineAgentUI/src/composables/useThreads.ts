import { computed, ref } from "vue";
import type { Message } from "../types";
import { callDeleteThreadAPI } from "../api/client";

export interface ConversationSummary {
  id: string;
  title: string;
  preview: string;
  updatedAt: number;
}

const THREADS_STORAGE_KEY = "redmine-chat-threads";
const MESSAGES_STORAGE_KEY = "redmine-chat-messages";
const ACTIVE_THREAD_KEY = "redmine-chat-active-thread";

const conversations = ref<ConversationSummary[]>([]);
const messagesByThread = ref<Record<string, Message[]>>({});
const activeThreadId = ref("");

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

function deriveTitle(messages: Message[]) {
  const firstUserMessage = messages.find((message) => message.role === "user")?.content?.trim();
  if (firstUserMessage) {
    return firstUserMessage.length > 42
      ? `${firstUserMessage.slice(0, 42)}...`
      : firstUserMessage;
  }

  return "New conversation";
}

function derivePreview(messages: Message[]) {
  const lastMessage = messages[messages.length - 1]?.content?.trim();
  if (lastMessage) {
    return lastMessage.length > 70 ? `${lastMessage.slice(0, 70)}...` : lastMessage;
  }

  return "No messages yet";
}

function persistState() {
  localStorage.setItem(THREADS_STORAGE_KEY, JSON.stringify(conversations.value));
  localStorage.setItem(MESSAGES_STORAGE_KEY, JSON.stringify(messagesByThread.value));
  localStorage.setItem(ACTIVE_THREAD_KEY, activeThreadId.value);
}

function hydrateState() {
  conversations.value = sortConversations(
    safeParse<ConversationSummary[]>(localStorage.getItem(THREADS_STORAGE_KEY), []),
  );
  messagesByThread.value = safeParse<Record<string, Message[]>>(
    localStorage.getItem(MESSAGES_STORAGE_KEY),
    {},
  );

  const storedActive = localStorage.getItem(ACTIVE_THREAD_KEY);
  if (storedActive && messagesByThread.value[storedActive]) {
    activeThreadId.value = storedActive;
  } else if (conversations.value.length > 0) {
    activeThreadId.value = conversations.value[0].id;
  } else {
    activeThreadId.value = crypto.randomUUID();
    conversations.value = [
      {
        id: activeThreadId.value,
        title: "New conversation",
        preview: "No messages yet",
        updatedAt: Date.now(),
      },
    ];
    messagesByThread.value[activeThreadId.value] = [];
    persistState();
  }
}

function ensureThreadExists(threadId: string) {
  const exists = conversations.value.some((conversation) => conversation.id === threadId);
  if (exists) return;

  conversations.value = sortConversations([
    {
      id: threadId,
      title: "New conversation",
      preview: "No messages yet",
      updatedAt: Date.now(),
    },
    ...conversations.value,
  ]);
  messagesByThread.value[threadId] = messagesByThread.value[threadId] ?? [];
  persistState();
}

hydrateState();

export function useThreads() {
  const currentConversation = computed(() =>
    conversations.value.find((conversation) => conversation.id === activeThreadId.value) ?? null,
  );

  function setActiveThread(threadId: string) {
    activeThreadId.value = threadId;
    ensureThreadExists(threadId);
    persistState();
  }

  function createThread() {
    const id = crypto.randomUUID();
    activeThreadId.value = id;
    messagesByThread.value[id] = [];
    conversations.value = sortConversations([
      {
        id,
        title: "New conversation",
        preview: "No messages yet",
        updatedAt: Date.now(),
      },
      ...conversations.value,
    ]);
    persistState();
    return id;
  }

  function getMessages(threadId: string) {
    return (messagesByThread.value[threadId] ?? []).map((message) => ({ ...message }));
  }

  function saveMessages(threadId: string, messages: Message[]) {
    messagesByThread.value[threadId] = messages.map((message) => ({ ...message }));

    const updatedConversation: ConversationSummary = {
      id: threadId,
      title: deriveTitle(messages),
      preview: derivePreview(messages),
      updatedAt: Date.now(),
    };

    const remaining = conversations.value.filter((conversation) => conversation.id !== threadId);
    conversations.value = sortConversations([updatedConversation, ...remaining]);
    persistState();
  }

  function renameThread(threadId: string, title: string) {
    conversations.value = conversations.value.map((conversation) =>
      conversation.id === threadId
        ? { ...conversation, title, updatedAt: Date.now() }
        : conversation,
    );
    persistState();
  }

  async function deleteThread(threadId: string) {
    // First attempt backend deletion
    let deleteSuccess = false;
    try {
      console.log(`[deleteThread] Calling backend DELETE for thread: ${threadId}`);
      await callDeleteThreadAPI(threadId);
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
          const newId = crypto.randomUUID();
          activeThreadId.value = newId;
          conversations.value = [
            {
              id: newId,
              title: "New conversation",
              preview: "No messages yet",
              updatedAt: Date.now(),
            },
          ];
          messagesByThread.value[newId] = [];
        }
      }

      persistState();
      console.log(`[deleteThread] ✅ Local state cleaned for thread: ${threadId}`);
    }
  }

  return {
    conversations,
    activeThreadId,
    currentConversation,
    setActiveThread,
    createThread,
    getMessages,
    saveMessages,
    renameThread,
    deleteThread,
  };
}
