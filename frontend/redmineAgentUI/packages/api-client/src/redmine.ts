import { apiClient } from './client';

export interface RedmineOption {
  id: string;
  name: string;
}

export interface RedmineMetadata {
  base_url: string;
  trackers: RedmineOption[];
  issue_statuses: RedmineOption[];
  issue_priorities: RedmineOption[];
  version_statuses?: RedmineOption[];
  project_versions?: RedmineOption[];
  project_members?: RedmineOption[];
  issue_summary?: {
    id: string;
    subject: string;
    assigned_to_name: string;
    assigned_to_id?: string | number | null;
    project_name?: string;
    project_identifier?: string;
  } | null;
}

export const redmineApi = {
  async getMetadata(token?: string, projectIdentifier?: string, issueId?: string | number): Promise<RedmineMetadata> {
    const params = new URLSearchParams();
    if (projectIdentifier) params.set('project_identifier', projectIdentifier);
    if (issueId !== undefined && issueId !== null && String(issueId).trim() !== '') params.set('issue_id', String(issueId));
    const query = params.toString() ? `?${params.toString()}` : '';
    return apiClient.get(`/internal/redmine-metadata${query}`, token);
  },
};
