import { callChatAPI, callApproveAPI } from '../api/client';
import type { ApproveRequest, Message } from '../types/index';
import { ref, type Ref } from 'vue';

function pushMessage(messages: Ref<Message[]>, role: "user" | "assistant", content: string) {
    messages.value.push({ role, content, timestamp: Date.now() });
}

export function useChat() {

    const messages: Ref<Message[]> = ref([]);
    const threadId: Ref<string> = ref("");
    const isLoading: Ref<boolean> = ref(false);
    const pendingInterrupt: Ref<Record<string, any> | null> = ref(null);
    const error: Ref<string | null> = ref(null);

    const localThreadId = localStorage.getItem("thread_id");
    threadId.value = localThreadId ? localThreadId : crypto.randomUUID();
    localStorage.setItem("thread_id", threadId.value);

    async function sendMessage(userText: string) {

        if (isLoading.value) return;
        if (userText.trim() === "") return;
        if (pendingInterrupt.value) {
            error.value = "Please address the pending interrupt before sending a new message.";
            return;
        }

        error.value = null;
        isLoading.value = true;
        const beforeCount = messages.value.length;

        try{
            pushMessage(messages, "user", userText);
            const response = await callChatAPI(userText, threadId.value);
            pushMessage(messages, "assistant", response.response);
            pendingInterrupt.value = response.requires_human ? response.interrupts : null;
        }catch(err: any){
            while(messages.value.length > beforeCount) messages.value.pop();
            error.value = err?.message || "Failed to send message";
        }finally{
            isLoading.value = false;
        }
    }

    async function submitDecision(payload: ApproveRequest){
        if (isLoading.value) return;

        if(payload.decision_type === "edit") {
            const hasValidEdit = payload.edited_action &&
                typeof payload.edited_action.name === "string" &&
                payload.edited_action.name.trim() !== "" &&
                payload.edited_action.args && 
                typeof payload.edited_action.args === "object";
                
            if (!hasValidEdit) {
                error.value = "For edit decision, edited_action.name and edited_action.args are required.";
                return;
            }
        }

        error.value = null;
        isLoading.value = true;

        try{
            const response = await callApproveAPI(threadId.value, payload);
            pushMessage(messages, "assistant", response.response);
            pendingInterrupt.value = null;
        }catch(err: any){
            error.value = err?.message || "Failed to submit decision";
        }finally{
            isLoading.value = false;
        }
    }

    return{
        messages,
        threadId,
        isLoading,
        pendingInterrupt,
        error,
        sendMessage,
        submitDecision
    };
}

