/// <reference types="vite/client" />
// src/api/client.ts
const BASE_API = import.meta.env.VITE_API_URL || '/api';
const REQUEST_TIMEOUT_MS = 3600000;

export function authHeaders(token?: string): Record<string, string> {
  const resolvedToken = token?.trim();

  if (!resolvedToken) {
    return {
      'Content-Type': 'application/json',
    };
  }

  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${resolvedToken}`,
  };
}

export async function handleResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get("content-type") || "";

  if (!response.ok) {
    let errorText = "Unknown error";

    if (contentType.includes('application/json')) {
      const payload = await response.json().catch(() => null);
      if (payload && typeof payload === 'object') {
        errorText =
          (payload as Record<string, unknown>).detail?.toString() ||
          (payload as Record<string, unknown>).message?.toString() ||
          JSON.stringify(payload);
      }
    } else {
      errorText = await response.text().catch(() => "Unknown error");
    }

    throw new Error(`API Error ${response.status}: ${errorText}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  if (contentType.includes("application/json")) {
    return response.json();
  }

  const text = await response.text().catch(() => "");
  return (text as unknown) as T;
}

async function fetchWithTimeout(input: string, init: RequestInit): Promise<Response> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    return await fetch(input, { ...init, signal: controller.signal });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error(`Request timed out after ${REQUEST_TIMEOUT_MS / 1000}s`);
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

// Reusable HTTP client
export const apiClient = {
  async get<T>(endpoint: string, token?: string): Promise<T> {
    const headers = authHeaders(token);
    const response = await fetchWithTimeout(`${BASE_API}${endpoint}`, {
      method: "GET",
      headers
    });
    return handleResponse<T>(response);
  },

  async post<T>(endpoint: string, body: unknown, token?: string): Promise<T> {
    const headers = authHeaders(token);
    const response = await fetchWithTimeout(`${BASE_API}${endpoint}`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
    return handleResponse<T>(response);
  },

  async delete<T>(endpoint: string, token?: string): Promise<T> {
    const headers = authHeaders(token);
    const response = await fetchWithTimeout(`${BASE_API}${endpoint}`, {
      method: "DELETE",
      headers,
    });
    return handleResponse<T>(response);
  },
};