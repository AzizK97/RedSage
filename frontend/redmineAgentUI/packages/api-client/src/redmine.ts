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
}

export const redmineApi = {
  async getMetadata(token?: string): Promise<RedmineMetadata> {
    return apiClient.get('/internal/redmine-metadata', token);
  },
};
