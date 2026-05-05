import { apiClient } from './client';
import { mergeMockFields } from '../mocks/searchMock';

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
  const resp = await apiClient.get<{ total: number; items: SearchResultItem[] }>(`/search?${params.toString()}`, token);
  // Merge mock fields for UI enhancements when backend lacks them
  const items = (resp.items || []).map((it) => mergeMockFields(it));
  return { total: resp.total, items };
}
