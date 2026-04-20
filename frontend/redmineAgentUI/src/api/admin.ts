const BASE_API = import.meta.env.VITE_API_URL;

export interface SyncPmResponse {
  synced_count: number;
}

export interface SetPmAccessResponse {
  user_id: string;
  redmine_user_id: number;
  email: string;
  enabled: boolean;
  generated_password: string | null;
}

export interface PmCandidate {
  user_id: string;
  redmine_user_id: number;
  email: string;
  full_name: string;
  in_platform: boolean;
  credentials_ready: boolean;
  enabled: boolean;
}

function authHeaders(token: string) {
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
}

async function parseJsonOrThrow(response: Response) {
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error: ${response.status} - ${errorText}`);
  }

  return response.json();
}

async function syncProjectManagers(token: string): Promise<SyncPmResponse> {
  const response = await fetch(`${BASE_API}/admin/users/sync-pm`, {
    method: "POST",
    headers: authHeaders(token),
  });

  return parseJsonOrThrow(response);
}

async function setPmAccess(
  token: string,
  payload: { redmine_user_id: number; enabled: boolean },
): Promise<SetPmAccessResponse> {
  const response = await fetch(`${BASE_API}/admin/users/pm-access`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });

  return parseJsonOrThrow(response);
}

async function listPmCandidates(token: string): Promise<{ items: PmCandidate[] }> {
  const response = await fetch(`${BASE_API}/admin/users/pm-candidates`, {
    method: "GET",
    headers: authHeaders(token),
  });

  return parseJsonOrThrow(response);
}

async function pingApi(): Promise<{ name: string; version: string; docs: string }> {
  const response = await fetch(`${BASE_API}/`);
  return parseJsonOrThrow(response);
}

export { listPmCandidates, pingApi, setPmAccess, syncProjectManagers };