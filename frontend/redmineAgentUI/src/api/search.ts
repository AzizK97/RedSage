import { apiClient } from './client';

export interface SearchResultItem {
  id: number | string;
  thread_id?: string;
  role?: string;
  content?: string;
  title?: string;
  preview?: string;
  created_at?: string;
  rank?: number;
}

export async function search(q: string, type: 'messages'|'threads' = 'messages', token?: string, limit = 20, offset = 0) {
  const params = new URLSearchParams({ q, type, limit: String(limit), offset: String(offset) });
  return apiClient.get<{ total: number; items: SearchResultItem[] }>(`/search?${params.toString()}`, token);
}
