// src/api/auth.ts
import { apiClient } from './client';
import type { LoginResult } from '../types';

export const authApi = {
  async login(email: string, password: string): Promise<LoginResult> {
    return apiClient.post('/auth/login', { email, password });
  },
};