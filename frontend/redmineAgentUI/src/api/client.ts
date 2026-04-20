import type { ChatResponse, ApproveResponse, ApproveRequest } from "../types";

const BASE_API = import.meta.env.VITE_API_URL;

export interface ThreadSummary {
    id: string;
    title: string;
    preview: string;
    updatedAt: number;
}

export interface CreateThreadResponse {
    thread_id: string;
}

function authHeaders(token: string) {
    return {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
    };
}

async function callChatAPI(message: string, thread_id: string, token: string): Promise<ChatResponse> {
    try {
        const response = await fetch(`${BASE_API}/chat`, 
            {
                method: "POST",
                headers: authHeaders(token),
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


async function callApproveAPI(thread_id: string, payload: ApproveRequest, token: string): Promise<ApproveResponse> {
    try{
        const response = await fetch(`${BASE_API}/chat/approve/${thread_id}`,
            {
                method: "POST",
                headers: authHeaders(token),
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

async function callDeleteThreadAPI(thread_id: string, token: string): Promise<{ status: string; thread_id: string }>{
    try{
        const response = await fetch(`${BASE_API}/chat/thread/${thread_id}`,{
            method: "DELETE",
            headers: authHeaders(token),
        });

        if (!response.ok){
            const errorText = await response.text();
            throw new Error(`API error: ${response.status} - ${errorText}`);
        }

        return await response.json();
    } catch (error){
        console.error("Error calling delete thread API:", error);
        throw error;
    }
}

async function callListThreadsAPI(token: string): Promise<ThreadSummary[]> {
    try {
        const response = await fetch(`${BASE_API}/chat/threads`, {
            method: "GET",
            headers: authHeaders(token),
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API error: ${response.status} - ${errorText}`);
        }

        return await response.json();
    } catch (error) {
        console.error("Error calling list threads API:", error);
        throw error;
    }
}

async function callCreateThreadAPI(token: string): Promise<CreateThreadResponse> {
    try {
        const response = await fetch(`${BASE_API}/chat/thread`, {
            method: "POST",
            headers: authHeaders(token),
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API error: ${response.status} - ${errorText}`);
        }

        return await response.json();
    } catch (error) {
        console.error("Error calling create thread API:", error);
        throw error;
    }
}

async function callThreadMessagesAPI(thread_id: string, token: string) {
    try {
        const response = await fetch(`${BASE_API}/chat/thread/${thread_id}/messages`, {
            method: "GET",
            headers: authHeaders(token),
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API error: ${response.status} - ${errorText}`);
        }

        return await response.json();
    } catch (error) {
        console.error("Error calling thread messages API:", error);
        throw error;
    }
}

export { callChatAPI, callApproveAPI, callDeleteThreadAPI, callListThreadsAPI, callCreateThreadAPI, callThreadMessagesAPI }