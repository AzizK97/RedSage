import { computed, ref } from "vue";

export type PlatformRole = "admin" | "project_manager";

interface SessionState {
  token: string;
  role: PlatformRole;
  fullName: string;
  email: string;
}

const SESSION_KEY = "redmine-chat:session";
const token = ref("");
const role = ref<PlatformRole | null>(null);
const fullName = ref("");
const email = ref("");
const userId = ref("");
const initialized = ref(false);

function decodePayloadFromToken(accessToken: string): { sub: string; email: string } {
  const segments = accessToken.split(".");
  if (segments.length < 2) return { sub: "", email: "" };
  const payloadSegment = segments[1].replace(/-/g, "+").replace(/_/g, "/");
  const padded = payloadSegment.padEnd(
    payloadSegment.length + ((4 - (payloadSegment.length % 4)) % 4),
    "=",
  );
  try {
    const payload = JSON.parse(atob(padded)) as { sub?: string; email?: string };
    return {
      sub: typeof payload.sub === "string" ? payload.sub : "",
      email: typeof payload.email === "string" ? payload.email : "",
    };
  } catch {
    return { sub: "", email: "" };
  }
}

function decodeSubFromToken(accessToken: string): string {
  return decodePayloadFromToken(accessToken).sub;
}

function safeParse(raw: string | null): SessionState | null {
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as Partial<SessionState>;
    if (
      typeof parsed.token === "string" &&
      (parsed.role === "admin" || parsed.role === "project_manager")
    ) {
      return {
        token: parsed.token,
        role: parsed.role,
        fullName: typeof parsed.fullName === "string" ? parsed.fullName : "",
        email: typeof parsed.email === "string" ? parsed.email : "",
      };
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
    fullName.value = persisted.fullName;
    email.value = persisted.email;
    userId.value = decodeSubFromToken(persisted.token);
  }
  initialized.value = true;
}

function persistSession() {
  if (!token.value || !role.value) {
    localStorage.removeItem(SESSION_KEY);
    return;
  }
  localStorage.setItem(
    SESSION_KEY,
    JSON.stringify({
      token: token.value,
      role: role.value,
      fullName: fullName.value,
      email: email.value,
    }),
  );
}

export function useSession() {
  initializeSession();

  const isAuthenticated = computed(() => !!token.value && !!role.value);

  function setSession(nextToken: string, nextRole: PlatformRole, nextFullName = "") {
    token.value = nextToken.trim();
    role.value = nextRole;
    fullName.value = nextFullName.trim();
    const decoded = decodePayloadFromToken(token.value);
    userId.value = decoded.sub;
    email.value = decoded.email;
    persistSession();
  }

  function clearSession() {
    token.value = "";
    role.value = null;
    fullName.value = "";
    email.value = "";
    userId.value = "";
    persistSession();
  }

  return {
    token,
    role,
    fullName,
    email,
    userId,
    isAuthenticated,
    setSession,
    clearSession,
  };
}
