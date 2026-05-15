import { chatApi } from '@redsage/api-client/chat';
import type { ApproveRequest, Message } from '../types/index.ts';
import { ref, watch, type Ref } from 'vue';
import { useThreads } from './useThreads';

function pushMessage(messages: Ref<Message[]>, role: "user" | "assistant", content: string) {
    messages.value.push({ role, content, timestamp: Date.now() });
}

export function useChat(token: string, userId: string) {

    const {
        activeThreadId,
        currentConversation,
        getMessages,
        saveMessages,
        conversations,
        createThread,
        setActiveThread,
        deleteThread,
        syncError,
        isSyncing,
        reloadThreadMessages,
    } = useThreads(token, userId);

    const messages: Ref<Message[]> = ref(getMessages(activeThreadId.value));
    const threadId = activeThreadId;
    const isLoading: Ref<boolean> = ref(false);
    const pendingInterrupt: Ref<Record<string, any> | null> = ref(null);
    const error: Ref<string | null> = ref(null);
    const loadingStatus: Ref<string> = ref("");
    const showLoadingStatus: Ref<boolean> = ref(false);
    let loadingTimer: ReturnType<typeof setInterval> | null = null;

    function buildLoadingSteps(text: string): string[] {
        const q = text.toLowerCase();

        if (/(member|team|role)/.test(q)) {
            return ["Reading sources...", "Fetching project members...", "Analyzing team roles..."];
        }
        if (/(version|sprint|milestone)/.test(q)) {
            return ["Reading sources...", "Fetching versions...", "Analyzing sprint timeline..."];
        }
        if (/(issue|ticket|task|bug)/.test(q)) {
            return ["Reading sources...", "Fetching issues...", "Analyzing issue details..."];
        }
        if (/(project)/.test(q)) {
            return ["Reading sources...", "Fetching projects...", "Analyzing project data..."];
        }

        return ["Thinking...", "Gathering Redmine data...", "Analyzing results..."];
    }

    function startLoadingStatus(userText: string) {
        const steps = buildLoadingSteps(userText);
        let index = 0;

        showLoadingStatus.value = true;
        loadingStatus.value = steps[index];

        if (loadingTimer) {
            clearInterval(loadingTimer);
        }

        loadingTimer = setInterval(() => {
            index = (index + 1) % steps.length;
            loadingStatus.value = steps[index];
        }, 1700);
    }

    function stopLoadingStatus() {
        if (loadingTimer) {
            clearInterval(loadingTimer);
        }
        loadingTimer = null;
        showLoadingStatus.value = false;
        loadingStatus.value = "";
    }

    watch(
        activeThreadId,
        (nextThreadId) => {
            const localMessages = getMessages(nextThreadId);
            messages.value = localMessages;
            pendingInterrupt.value = null;
            error.value = null;
        },
        { immediate: true },
    );

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
        const currentThreadId = threadId.value;

        if (!currentThreadId) {
            error.value = "No active conversation found.";
            isLoading.value = false;
            return;
        }

        let responseReceived = false;

        try{
            pushMessage(messages, "user", userText);
            saveMessages(currentThreadId, messages.value);
            startLoadingStatus(userText);

            const response = await chatApi.sendMessage(userText, currentThreadId, token);
            responseReceived = true;
            pushMessage(messages, "assistant", response.response);
            const hasInterruptPayload = Array.isArray(response.interrupts)
                ? response.interrupts.length > 0
                : !!response.interrupts && Object.keys(response.interrupts).length > 0;
            pendingInterrupt.value = (response.requires_human || hasInterruptPayload)
                ? response.interrupts
                : null;

            try {
                await reloadThreadMessages(currentThreadId);
                messages.value = getMessages(currentThreadId);
            } catch {
                // Keep optimistic messages if history sync fails.
            }
            saveMessages(currentThreadId, messages.value);
        }catch(err: any){
            if (!responseReceived) {
                messages.value = messages.value.slice(0, beforeCount);
                saveMessages(currentThreadId, messages.value);
            }
            error.value = err?.message || "Failed to send message";
        }finally{
            stopLoadingStatus();
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
        const currentThreadId = threadId.value;

        if (!currentThreadId) {
            error.value = "No active conversation found for this decision.";
            isLoading.value = false;
            return;
        }

        try{
            const response = await chatApi.approve(currentThreadId, payload, token);
            pushMessage(messages, "assistant", response.response);
            pendingInterrupt.value = null;

            try {
                await reloadThreadMessages(currentThreadId);
                messages.value = getMessages(currentThreadId);
            } catch {
                // Keep optimistic assistant message if history sync fails.
            }
            saveMessages(currentThreadId, messages.value);
        }catch(err: any){
            error.value = err?.message || "Failed to submit decision";
        }finally{
            isLoading.value = false;
        }
    }

    return{
        messages,
        threadId,
        activeThreadId,
        isLoading,
        pendingInterrupt,
        error,
        loadingStatus,
        showLoadingStatus,
        isSyncing,
        syncError,
        currentConversation,
        conversations,
        createThread,
        setActiveThread,
        deleteThread,
        sendMessage,
        submitDecision
    };
}

