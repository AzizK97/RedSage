import { computed, ref } from "vue";

export type PlatformRole = "admin" | "project_manager";

interface SessionState {
  token: string;
  role: PlatformRole;
}

const SESSION_KEY = "redmine-chat:session";
const token = ref("");
const role = ref<PlatformRole | null>(null);
const userId = ref("");
const initialized = ref(false);

function decodeSubFromToken(accessToken: string): string {
  const segments = accessToken.split(".");
  if (segments.length < 2) return "";
  const payloadSegment = segments[1].replace(/-/g, "+").replace(/_/g, "/");
  const padded = payloadSegment.padEnd(
    payloadSegment.length + ((4 - (payloadSegment.length % 4)) % 4),
    "=",
  );
  try {
    const payload = JSON.parse(atob(padded)) as { sub?: string };
    return typeof payload.sub === "string" ? payload.sub : "";
  } catch {
    return "";
  }
}

function safeParse(raw: string | null): SessionState | null {
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as Partial<SessionState>;
    if (
      typeof parsed.token === "string" &&
      (parsed.role === "admin" || parsed.role === "project_manager")
    ) {
      return { token: parsed.token, role: parsed.role };
    }
  } catch {
    return null;
  }
  return null;
}

function initializeSession() {
  if (initialized.value) return;
  const persisted = safeParse(localStorage.getItem(SESSION_KEY));
  if (persisted) {
    token.value = persisted.token;
    role.value = persisted.role;
    userId.value = decodeSubFromToken(persisted.token);
  }
  initialized.value = true;
}

function persistSession() {
  if (!token.value || !role.value) {
    localStorage.removeItem(SESSION_KEY);
    return;
  }
  localStorage.setItem(SESSION_KEY, JSON.stringify({ token: token.value, role: role.value }));
}

export function useSession() {
  initializeSession();

  const isAuthenticated = computed(() => !!token.value && !!role.value);

  function setSession(nextToken: string, nextRole: PlatformRole) {
    token.value = nextToken.trim();
    role.value = nextRole;
    userId.value = decodeSubFromToken(token.value);
    persistSession();
  }

  function clearSession() {
    token.value = "";
    role.value = null;
    userId.value = "";
    persistSession();
  }

  return {
    token,
    role,
    userId,
    isAuthenticated,
    setSession,
    clearSession,
  };
}
