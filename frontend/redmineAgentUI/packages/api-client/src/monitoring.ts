import { apiClient } from './client';
import type { MonitoringOverview, MonitoringRunResponse, MonitoringLastRun, MonitoringNotification } from './types.ts';

export const monitoringApi = {
  async getOverview(token: string): Promise<MonitoringOverview> {
    return apiClient.get('/monitoring/overview', token);
  },

  async runNow(token: string): Promise<MonitoringRunResponse> {
    // new endpoint name used by backend
    return apiClient.post('/monitoring/run-now', {}, token);
  },

  async getStatus(token: string): Promise<MonitoringLastRun> {
    return apiClient.get('/monitoring/status', token);
  },

  async listNotifications(token: string): Promise<{ items: MonitoringNotification[] }> {
    return apiClient.get('/monitoring/notifications', token);
  },
};
