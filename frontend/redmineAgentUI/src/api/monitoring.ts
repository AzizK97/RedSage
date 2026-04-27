import { apiClient } from './client';
import type { MonitoringOverview, MonitoringRunResponse } from '../types';

export const monitoringApi = {
  async getOverview(token: string): Promise<MonitoringOverview> {
    return apiClient.get('/monitoring/overview', token);
  },

  async runNow(token: string): Promise<MonitoringRunResponse> {
    return apiClient.post('/monitoring/run', {}, token);
  },
};
