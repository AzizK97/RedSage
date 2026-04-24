// src/api/admin.ts
import { apiClient } from './client';
import type { PmCandidate, RootInfo, SetPmAccessResponse, SyncPmResponse } from '../types';

export const adminApi = {
  async syncProjectManagers(token: string): Promise<SyncPmResponse> {
    return apiClient.post('/admin/users/sync-pm', {}, token);
  },

  async setPmAccess(
    token: string,
    payload: { redmine_user_id: number; enabled: boolean },
  ): Promise<SetPmAccessResponse> {
    return apiClient.post('/admin/users/pm-access', payload, token);
  },

  async listPmCandidates(token: string): Promise<{ items: PmCandidate[] }> {
    return apiClient.get('/admin/users/pm-candidates', token);
  },

  async pingApi(): Promise<RootInfo> {
    return apiClient.get('/');
  },
};