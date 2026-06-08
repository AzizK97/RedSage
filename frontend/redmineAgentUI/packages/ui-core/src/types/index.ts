export interface ChatRequest {
  message: string;
  thread_id: string;
}

export interface ChatResponse {
  response: string;
  requires_human: boolean;
  interrupts: Record<string, any>;
}

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

export interface ApproveRequest {
  decision_type: 'approve' | 'reject' | 'edit';
  message?: string;
  edited_action?: {
    name: string;
    args: Record<string, any>;
  };
}

export interface ApproveResponse {
  status: 'approve' | 'reject' | 'edit';
  response: string;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  isStreaming?: boolean;
  finished?: boolean;
  streaming?: boolean;
}

export interface ThreadSummary {
  thread_id: string;
  title: string;
  preview: string;
  updated_at: number;
}

export interface CreateThreadResponse {
  thread_id: string;
}

export interface LoginResult {
  access_token: string;
  full_name: string;
  token_type: string;
}

export interface RootInfo {
  name: string;
  version: string;
  docs: string;
}

export interface SyncPmResponse {
  synced_count: number;
}

export interface SetPmAccessResponse {
  user_id: string;
  redmine_user_id: number;
  email: string;
  full_name: string;
  enabled: boolean;
  projects_name: string[];
  enabled_by_admin_id: string | null;
}

export interface PmCandidate {
  user_id?: string;
  redmine_user_id: number;
  email: string;
  full_name: string;
  in_platform: boolean;
  projects_name: string[];
  enabled: boolean;
}

export interface MonitoringOverview {
  status: string;
  run_trend?: Array<{ started_at: string; events_count?: number | string }>;
}

export interface MonitoringRunResponse {
  status: string;
}

export interface MonitoringLastRun {
  status: string;
}

export interface MonitoringNotification {
  id: string;
  message: string;
  created_at?: number;
  title?: string;
  subtitle?: string;
  severity?: 'critical' | 'warning' | 'success' | 'info';
}

export interface DashboardProject {
  id: string | number;
  name: string;
  identifier?: string;
  progress?: number;
  health?: 'On track' | 'At risk' | 'Delayed' | string;
  open_issues?: number;
  closed_issues?: number;
  completion_eta?: string;
}

export interface OverdueTicketInsight {
  id: string | number;
  issue_id?: number | string;
  title: string;
  project_identifier?: string;
  project_name?: string;
  subject?: string;
  due_date?: string;
  url?: string;
}

export interface AtRiskProjectInsight {
  id: string | number;
  name: string;
  project_identifier?: string;
  overdue_count?: number;
  high_priority_open_count?: number;
  project_name?: string;
  reason?: string;
  recommended_action?: string;
  url?: string;
  project_id?: string | number;
}

export interface ProjectStatus {
  id: string;
  name?: string;
  identifier?: string;
  progress?: number;
  health?: 'On track' | 'At risk' | 'Delayed' | string;
  owner?: string;
  completionEta?: string;
  open_issues?: number;
  closed_issues?: number;
}

export interface TaskDistributionItem {
  assignee_id?: string | number | null;
  assignee_name: string;
  project_identifier?: string;
  project_name?: string;
  open_tasks?: number;
  overdue_tasks?: number;
  critical_tasks?: number;
  estimated_hours?: number;
  load_score?: number;
}