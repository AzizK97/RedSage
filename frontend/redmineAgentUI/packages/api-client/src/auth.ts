// src/api/auth.ts
import { apiClient } from './client';
import type { LoginResult } from './types.ts';

export const authApi = {
  async login(email: string, password: string): Promise<LoginResult> {
    return apiClient.post('/auth/login', { email, password });
  },

  async redmineConnect(redmine_url: string | undefined, api_key: string): Promise<LoginResult> {
    return apiClient.post('/auth/redmine/connect', { redmine_url, api_key });
  },
};