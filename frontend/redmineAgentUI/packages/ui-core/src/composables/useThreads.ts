import { computed, ref } from "vue";
import type { Message } from "../types";
import { chatApi } from "@redsage/api-client/chat";
import type { ThreadSummary } from "../types";

export interface ConversationSummary {
  id: string;
  title: string;
  preview: string;
  updatedAt: number;
}

let lastUserId: string | null = null;
let lastToken = "";

const conversations = ref<ConversationSummary[]>([]);
const messagesByThread = ref<Record<string, Message[]>>({});
const activeThreadId = ref("");

let hydrated = false;
let syncStarted = false;
const syncError = ref<string | null>(null);
const isSyncing = ref(false);

function buildKeys(userId: string) {
  const prefix = `redmine-chat:${userId}:`;
  return {
    messages: `${prefix}messages`,
    active: `${prefix}active-thread`,
    conversations: `${prefix}conversations`,
  };
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

function cloneMessages(messages: Message[]) {
  return messages.map((message) => ({ ...message }));
}

function normalizeMessages(rawMessages: unknown): Message[] {
  if (!Array.isArray(rawMessages)) return [];

  return rawMessages
    .filter((item) => !!item && typeof item === "object")
    .map((item) => {
      const candidate = item as Partial<Message>;
      const role = candidate.role === "assistant" ? "assistant" : "user";
      const content = typeof candidate.content === "string" ? candidate.content : "";
      const timestamp =
        typeof candidate.timestamp === "number" ? candidate.timestamp : Date.now();

      return { role, content, timestamp };
    });
}

function deriveTitle(messages: Message[]) {
  const firstUser = messages.find((message) => message.role === "user" && message.content.trim());
  if (!firstUser) return "New conversation";

  const compact = firstUser.content.replace(/\s+/g, " ").trim();
  return compact.length > 42 ? `${compact.slice(0, 42)}…` : compact;
}

function derivePreview(messages: Message[]) {
  const latest = messages[messages.length - 1];
  if (!latest?.content?.trim()) return "No messages yet";

  const compact = latest.content.replace(/\s+/g, " ").trim();
  return compact.length > 70 ? `${compact.slice(0, 70)}…` : compact;
}

function persistState(userId: string) {
  const keys = buildKeys(userId);
  localStorage.setItem(keys.conversations, JSON.stringify(conversations.value));
  localStorage.setItem(keys.messages, JSON.stringify(messagesByThread.value));
  localStorage.setItem(keys.active, activeThreadId.value);
}

function createLocalConversation(threadId: string): ConversationSummary {
  return {
    id: threadId,
    title: "New conversation",
    preview: "No messages yet",
    updatedAt: Date.now(),
  };
}

function ensureThreadExists(threadId: string) {
  const id = threadId.trim();
  if (!id) return;

  const exists = conversations.value.some((conversation) => conversation.id === id);

  if (!exists) {
    conversations.value = sortConversations([createLocalConversation(id), ...conversations.value]);
  }

  messagesByThread.value[id] = normalizeMessages(messagesByThread.value[id] ?? []);
}

function resetModuleState() {
  conversations.value = [];
  messagesByThread.value = {};
  activeThreadId.value = "";
  hydrated = false;
  syncStarted = false;
}

function hydrateState(userId: string) {
  if (hydrated) return;

  const keys = buildKeys(userId);
  const storedConversations = safeParse<ConversationSummary[]>(
    localStorage.getItem(keys.conversations),
    [],
  );
  const storedMessages = safeParse<Record<string, Message[]>>(
    localStorage.getItem(keys.messages),
    {},
  );
  const storedActive = localStorage.getItem(keys.active)?.trim() || "";

  messagesByThread.value = Object.fromEntries(
    Object.entries(storedMessages).map(([threadId, threadMessages]) => [
      threadId,
      normalizeMessages(threadMessages),
    ]),
  );

  conversations.value = sortConversations(
    storedConversations
      .filter((item) => !!item?.id)
      .map((item) => ({
        id: item.id,
        title: typeof item.title === "string" && item.title.trim() ? item.title : "New conversation",
        preview:
          typeof item.preview === "string" && item.preview.trim()
            ? item.preview
            : "No messages yet",
        updatedAt: typeof item.updatedAt === "number" ? item.updatedAt : Date.now(),
      })),
  );

  if (conversations.value.length === 0 && Object.keys(messagesByThread.value).length > 0) {
    conversations.value = sortConversations(
      Object.entries(messagesByThread.value).map(([threadId, threadMessages]) => ({
        id: threadId,
        title: deriveTitle(threadMessages),
        preview: derivePreview(threadMessages),
        updatedAt: threadMessages[threadMessages.length - 1]?.timestamp ?? Date.now(),
      })),
    );
  }

  if (storedActive) {
    activeThreadId.value = storedActive;
    ensureThreadExists(storedActive);
  }

  if (!activeThreadId.value && conversations.value.length > 0) {
    activeThreadId.value = conversations.value[0].id;
  }

  persistState(userId);
  hydrated = true;
}

function mapListItem(t: ThreadSummary): ConversationSummary {
  return {
    id: t.thread_id,
    title: t.title,
    preview: t.preview,
    updatedAt: t.updated_at,
  };
}

export function useThreads(token: string, userId: string) {
  if (userId && userId !== lastUserId) {
    lastUserId = userId;
    resetModuleState();
  }
  if (token && token !== lastToken) {
    lastToken = token;
  }

  if (userId) {
    hydrateState(userId);
  }

  async function loadThreadMessages(threadId: string) {
    if (!userId) return;
    const { messages: raw } = await chatApi.getThreadMessages(threadId, token);
    const list = normalizeMessages(raw);
    messagesByThread.value = { ...messagesByThread.value, [threadId]: list };
    persistState(userId);
  }

  async function refreshThreadsFromServer(preferredThreadId?: string) {
    if (!userId) return;
    const candidate = preferredThreadId?.trim();
    isSyncing.value = true;
    syncError.value = null;
    try {
      const list = await chatApi.listThreads(token);
      if (list.length > 0) {
        const mapped = list.map(mapListItem);
        conversations.value = sortConversations(mapped);
        const pick =
          candidate && list.some((t) => t.thread_id === candidate)
            ? candidate
            : list[0].thread_id;
        activeThreadId.value = pick;
        await loadThreadMessages(pick);
        persistState(userId);
        return;
      }

      const created = await chatApi.createThread(token);
      const newId = created.thread_id;
      conversations.value = sortConversations([
        createLocalConversation(newId),
      ]);
      activeThreadId.value = newId;
      messagesByThread.value[newId] = [];
      persistState(userId);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to sync conversations from server.";
      syncError.value = message;
      if (!activeThreadId.value) {
        activeThreadId.value = conversations.value[0]?.id ?? "";
      }
    } finally {
      isSyncing.value = false;
    }
  }

  if (userId && !syncStarted) {
    syncStarted = true;
    void refreshThreadsFromServer();
  }

  const currentConversation = computed(
    () => conversations.value.find((conversation) => conversation.id === activeThreadId.value) ?? null,
  );

  async function setActiveThread(threadId: string) {
    if (!userId) return;
    syncError.value = null;
    ensureThreadExists(threadId);
    activeThreadId.value = threadId;
    try {
      await loadThreadMessages(threadId);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to load selected conversation.";
      syncError.value = message;
    }
    persistState(userId);
  }

  async function createThread() {
    if (!userId) {
      return String(crypto.randomUUID());
    }
    syncError.value = null;
    let threadId: string = String(crypto.randomUUID());
    try {
      const created = await chatApi.createThread(token);
      if (created?.thread_id) {
        threadId = String(created.thread_id);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to create conversation on server.";
      syncError.value = message;
      throw error;
    }
    ensureThreadExists(threadId);
    activeThreadId.value = threadId;
    messagesByThread.value = { ...messagesByThread.value, [threadId]: [] };
    const remaining = conversations.value.filter((conversation) => conversation.id !== threadId);
    conversations.value = sortConversations([
      {
        id: threadId,
        title: "New conversation",
        preview: "No messages yet",
        updatedAt: Date.now(),
      },
      ...remaining,
    ]);
    persistState(userId);
    return threadId;
  }

  function getMessages(threadId: string) {
    return cloneMessages(messagesByThread.value[threadId] ?? []);
  }

  function saveMessages(threadId: string, messages: Message[]) {
    if (!userId) return;
    ensureThreadExists(threadId);

    const normalizedMessages = normalizeMessages(messages);
    messagesByThread.value[threadId] = normalizedMessages;

    const updatedConversation: ConversationSummary = {
      id: threadId,
      title: deriveTitle(normalizedMessages),
      preview: derivePreview(normalizedMessages),
      updatedAt: Date.now(),
    };

    const remaining = conversations.value.filter((conversation) => conversation.id !== threadId);
    conversations.value = sortConversations([updatedConversation, ...remaining]);
    persistState(userId);
  }

  function renameThread(threadId: string, title: string) {
    if (!userId) return;
    const normalizedTitle = title.trim() || "New conversation";
    conversations.value = conversations.value.map((conversation) =>
      conversation.id === threadId
        ? { ...conversation, title: normalizedTitle, updatedAt: Date.now() }
        : conversation,
    );
    persistState(userId);
  }

  async function deleteThread(threadId: string) {
    if (!userId) return;
    syncError.value = null;
    try {
      await chatApi.deleteThread(threadId, token);
      await refreshThreadsFromServer();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to delete conversation.";
      syncError.value = message;
      throw error;
    }
  }

  async function reloadThreadMessages(threadId: string) {
    await loadThreadMessages(threadId);
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
    syncError,
    isSyncing,
    refreshThreadsFromServer,
    reloadThreadMessages,
  };
}
