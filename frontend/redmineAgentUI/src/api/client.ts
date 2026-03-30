import type { ChatResponse, ApproveResponse, ApproveRequest } from "../types";

const BASE_API = import.meta.env.VITE_API_URL;

async function callChatAPI(message: string, thread_id: string): Promise<ChatResponse> {
    try {
        const response = await fetch(`${BASE_API}/chat`, 
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message, thread_id })
            });
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API error: ${response.status} - ${errorText}`);
        } else {
            return await response.json();
        }
    } catch (error) {
        console.error("Error calling chat API:", error);
        throw error;
    }
}


async function callApproveAPI(thread_id: string, payload: ApproveRequest): Promise<ApproveResponse> {
    try{
        const response = await fetch(`${BASE_API}/chat/approve/${thread_id}`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API error: ${response.status} - ${errorText}`);
        } else {
            return await response.json();
        }
    }catch(error){
        console.error("Error calling approve API:", error);
        throw error;
    }
}

export { callChatAPI, callApproveAPI }