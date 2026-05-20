import { apiClient } from "./client";
import type { AtRiskProjectInsight, DashboardProject, OverdueTicketInsight, TaskDistributionItem } from './types.ts';

export const dashboardApi = {
  async listProjects(token: string): Promise<{ items: DashboardProject[] }> {
    return apiClient.get("/dashboard/projects", token);
  },

  async getInsights(
    token: string,
    projectIdentifier?: string | null,
  ): Promise<{ top_overdue_tickets: OverdueTicketInsight[]; at_risk_projects: AtRiskProjectInsight[]; task_distribution: TaskDistributionItem[] }> {
    const query = projectIdentifier?.trim() ? `?project_identifier=${encodeURIComponent(projectIdentifier.trim())}` : "";
    return apiClient.get(`/dashboard/insights${query}`, token);
  },
};
