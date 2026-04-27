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
    managed_projects: string[];
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
    PmCandidate
}