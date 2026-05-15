export interface ChatResponse {
  response: string;
  requires_human: boolean;
  interrupts: Record<string, any>;
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
  generated_account: boolean;
  enabled_by_admin_id: string | null;
}

export interface PmCandidate {
  user_id?: string;
  redmine_user_id: number;
  email: string;
  full_name: string;
  in_platform: boolean;
  credentials_ready: boolean;
  enabled: boolean;
}

export interface MonitoringOverview {
  status: string;
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
  id: string;
  name: string;
}

export interface OverdueTicketInsight {
  id: string;
  title: string;
}

export interface AtRiskProjectInsight {
  id: string;
  name: string;
}

export interface ProjectStatus {
  id: string;
  status: string;
}