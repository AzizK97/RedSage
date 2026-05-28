import { apiClient } from './client';

export interface ThreadSearchResult {
  thread_id: string;
  title: string;
  preview: string;
  updated_at: number | null;
}

export interface ThreadSearchResponse {
  total: number;
  items: ThreadSearchResult[];
}

export async function searchThreads(
  q: string,
  token: string,
  limit = 20,
  offset = 0,
): Promise<ThreadSearchResponse> {
  const params = new URLSearchParams({
    q,
    limit: String(limit),
    offset: String(offset),
  });
  return apiClient.get<ThreadSearchResponse>(`/search?${params.toString()}`, token);
}
