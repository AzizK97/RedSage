//like a DTO
interface ChatRequest {
    message: string,
    thread_id: string
} 

interface ChatResponse {
    response: string,
    requires_human: boolean,
    interrupts: Record<string, any>
}

interface ApproveRequest {
    decision_type: "approve" | "reject" | "edit",
    message?: string,
    edited_action?: {
        name: string;
        args: Record<string, any>
    }
}

interface ApproveResponse{
    status: "approve" | "reject" | "edit",
    response: string
}

interface Message {
    role: "user" | "assistant",
    content: string,
    timestamp: number
}

/** API shape for GET /api/chat/threads */
interface ThreadSummary {
    thread_id: string;
    title: string;
    preview: string;
    updated_at: number;
}

interface CreateThreadResponse {
    thread_id: string
}

interface LoginResult {
    access_token: string;
    full_name: string;
    token_type: string;
}

interface RootInfo {
    name: string;
    version: string;
    docs: string;
}

interface SyncPmResponse {
    synced_count: number;
}

interface SetPmAccessResponse {
    user_id: string;
    redmine_user_id: number;
    email: string;
    full_name: string;
    enabled: boolean;
    generated_account: boolean;
    enabled_by_admin_id: string | null;
}

interface PmCandidate {
    user_id?: string;
    redmine_user_id: number;
    email: string;
    full_name: string;
    in_platform: boolean;
    credentials_ready: boolean;
    enabled: boolean;
}

interface MonitoringMetrics {
    total_projects: number;
    open_issues: number;
    in_progress: number;
    overdue: number;
    critical: number;
}

interface MonitoringProjectStatus {
    project_id: number;
    project_name: string;
    open_issues: number;
    in_progress: number;
    overdue: number;
    critical: number;
}

interface MonitoringRunTrend {
    started_at: string;
    events_count: number;
}

interface MonitoringEvent {
    event_type: string;
    severity: "critical" | "important" | "info";
    title: string;
    details: string;
    occurred_at: string;
    project_id?: number;
    issue_id?: number;
}

interface MonitoringLastRun {
    id: string;
    started_at: string;
    projects_count: number;
    issues_count: number;
    events_count: number;
    synced_pms: number;
}

interface MonitoringOverview {
    metrics: MonitoringMetrics;
    last_run: MonitoringLastRun | null;
    project_status: MonitoringProjectStatus[];
    run_trend: MonitoringRunTrend[];
    recent_events: MonitoringEvent[];
}

interface MonitoringRunResponse {
    status: "success" | "skipped";
    run_id?: string;
    projects_count?: number;
    issues_count?: number;
    events_count?: number;
    synced_pms?: number;
    reason?: string;
}

export type {
    ChatRequest,
    ChatResponse,
    ApproveRequest,
    ApproveResponse,
    Message,
    ThreadSummary,
    CreateThreadResponse,
    LoginResult,
    RootInfo,
    SyncPmResponse,
    SetPmAccessResponse,
    PmCandidate,
    MonitoringMetrics,
    MonitoringProjectStatus,
    MonitoringRunTrend,
    MonitoringEvent,
    MonitoringLastRun,
    MonitoringOverview,
    MonitoringRunResponse
}