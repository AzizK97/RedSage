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

export type { ChatRequest, ChatResponse, ApproveRequest, ApproveResponse, Message }