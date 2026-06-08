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
        getPendingInterrupt,
        setPendingInterrupt,
        saveMessages,
        conversations,
        createThread,
        setActiveThread,
        deleteThread,
        syncError,
        isSyncing,
        reloadThreadMessages,
        renameThread,
    } = useThreads(token, userId);

    const messages: Ref<Message[]> = ref(getMessages(activeThreadId.value));
    const threadId = activeThreadId;
    const isLoading: Ref<boolean> = ref(false);
    const isStreaming: Ref<boolean> = ref(false);
    const pendingInterrupt: Ref<Record<string, any> | null> = ref(null);
    const error: Ref<string | null> = ref(null);
    const loadingStatus: Ref<string> = ref("");
    const showLoadingStatus: Ref<boolean> = ref(false);
    let loadingTimer: ReturnType<typeof setInterval> | null = null;

    function buildLoadingSteps(): string[] {
        // const q = text.toLowerCase();

        // if (/(member|team|role)/.test(q)) {
        //     return ["Reading sources...", "Fetching project members...", "Analyzing team roles..."];
        // }
        // if (/(version|sprint|milestone)/.test(q)) {
        //     return ["Reading sources...", "Fetching versions...", "Analyzing sprint timeline..."];
        // }
        // if (/(issue|ticket|task|bug)/.test(q)) {
        //     return ["Reading sources...", "Fetching issues...", "Analyzing issue details..."];
        // }
        // if (/(project)/.test(q)) {
        //     return ["Reading sources...", "Fetching projects...", "Analyzing project data..."];
        // }

        return ["Thinking...", "Gathering Redmine data...", "Analyzing results..."];
    }

    function startLoadingStatus() {
        const steps = buildLoadingSteps();
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
            pendingInterrupt.value = getPendingInterrupt(nextThreadId);
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

        let receivedAnyToken = false;
        let streamDone = false;
        let assistantMessageIndex = -1;

        try{
                pushMessage(messages, "user", userText);
                // create assistant placeholder with streaming metadata
                messages.value.push({ role: "assistant", content: "", timestamp: Date.now(), isStreaming: true, finished: false });
                assistantMessageIndex = messages.value.length - 1;
                isStreaming.value = true;
            saveMessages(currentThreadId, messages.value);
            startLoadingStatus();

            await chatApi.streamMessage(userText, currentThreadId, token, {
                onToken: (tokenChunk) => {
                    if (!receivedAnyToken) {
                        receivedAnyToken = true;
                        stopLoadingStatus();
                    }

                    if (assistantMessageIndex < 0 || !messages.value[assistantMessageIndex]) {
                        messages.value.push({ role: "assistant", content: "", timestamp: Date.now(), isStreaming: true, finished: false });
                        assistantMessageIndex = messages.value.length - 1;
                    }

                    // append token and ensure streaming flag
                    const msg = messages.value[assistantMessageIndex];
                    msg.content += tokenChunk;
                    msg.isStreaming = true;
                    msg.finished = false;
                },
                onEvent: (event) => {
                    if (event.type === "error") {
                        const detail =
                            typeof event.content === "string" && event.content.trim()
                                ? event.content
                                : "Streaming failed";
                        throw new Error(detail);
                    }

                    // Fallback for non-token streams that still emit full answers.
                    if (event.type === "answer" && typeof event.content === "string") {
                        if (!receivedAnyToken) {
                            receivedAnyToken = true;
                            stopLoadingStatus();
                        }
                        if (assistantMessageIndex < 0 || !messages.value[assistantMessageIndex]) {
                            messages.value.push({ role: "assistant", content: "", timestamp: Date.now() });
                            assistantMessageIndex = messages.value.length - 1;
                        }
                        messages.value[assistantMessageIndex].content += event.content;
                    }
                },
                onDone: () => {
                    streamDone = true;
                    isStreaming.value = false;
                    if (assistantMessageIndex >= 0 && messages.value[assistantMessageIndex]) {
                        messages.value[assistantMessageIndex].isStreaming = false;
                        messages.value[assistantMessageIndex].finished = true;
                    }
                },
            });

            if (!streamDone) {
                throw new Error("Stream ended unexpectedly before completion.");
            }

            pendingInterrupt.value = null;
            setPendingInterrupt(currentThreadId, null);
            saveMessages(currentThreadId, messages.value);
        }catch(err: any){
            if (!receivedAnyToken) {
                messages.value = messages.value.slice(0, beforeCount);
                saveMessages(currentThreadId, messages.value);
            } else {
                saveMessages(currentThreadId, messages.value);
            }
            error.value = err?.message || "Failed to send message";
            isStreaming.value = false;
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
            setPendingInterrupt(currentThreadId, null);

            try {
                await reloadThreadMessages(currentThreadId);
                messages.value = getMessages(currentThreadId);
                pendingInterrupt.value = getPendingInterrupt(currentThreadId);
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
        isStreaming,
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
        renameThread,
        sendMessage,
        submitDecision
    };
}

