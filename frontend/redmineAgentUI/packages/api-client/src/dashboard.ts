import { apiClient } from "./client";
import type { AtRiskProjectInsight, DashboardProject, OverdueTicketInsight } from './types.ts';

export const dashboardApi = {
  async listProjects(token: string): Promise<{ items: DashboardProject[] }> {
    return apiClient.get("/dashboard/projects", token);
  },

  async getInsights(
    token: string,
  ): Promise<{ top_overdue_tickets: OverdueTicketInsight[]; at_risk_projects: AtRiskProjectInsight[] }> {
    return apiClient.get("/dashboard/insights", token);
  },
};
