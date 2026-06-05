// src/api/chat.ts
import { apiClient } from './client';
import type { 
  ChatResponse, 
  ApproveRequest, 
  ApproveResponse, 
  ThreadSummary, 
  CreateThreadResponse 
} from './types.ts';

export interface StreamEventPayload {
  type: string;
  agent?: string;
  content?: string;
  [key: string]: unknown;
}

export interface StreamHandlers {
  onEvent?: (event: StreamEventPayload) => void;
  onToken?: (token: string, event: StreamEventPayload) => void;
  onDone?: () => void;
}

export const chatApi = {
  async sendMessage(message: string, thread_id: string, token: string): Promise<ChatResponse> {
    return apiClient.post('/chat', { message, thread_id }, token);
  },

  async approve(thread_id: string, payload: ApproveRequest, token: string): Promise<ApproveResponse> {
    return apiClient.post(`/chat/approve/${thread_id}`, payload, token);
  },

  async listThreads(token: string): Promise<ThreadSummary[]> {
    return apiClient.get('/chat/threads', token);
  },

  async createThread(token: string): Promise<CreateThreadResponse> {
    return apiClient.post('/chat/thread', {}, token);
  },

  async deleteThread(thread_id: string, token: string): Promise<{ status: string; thread_id: string }> {
    return apiClient.delete(`/chat/thread/${thread_id}`, token);
  },

  async renameThread(thread_id: string, title: string, token: string): Promise<{ status: string; thread_id: string; title: string }> {
    return apiClient.patch(`/chat/thread/${thread_id}/rename`, { title }, token);
  },

  async getThreadMessages(
    thread_id: string,
    token: string,
  ): Promise<{ messages: { role: string; content: string; timestamp: number }[]; pending_interrupt?: Record<string, any> | null }> {
    return apiClient.get(`/chat/thread/${thread_id}/messages`, token);
  },

  async streamMessage(
    message: string,
    thread_id: string,
    token: string,
    handlers: StreamHandlers = {},
  ): Promise<void> {
    const response = await apiClient.postStream('/chat/stream', { message, thread_id }, token);

    if (!response.body) {
      throw new Error('Streaming is not supported by the current browser response body.');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    const processFrame = (frame: string) => {
      const lines = frame
        .split(/\r?\n/)
        .filter((line) => line.startsWith('data:'));

      if (lines.length === 0) return;

      const payload = lines
        .map((line) => line.replace(/^data:\s?/, ''))
        .join('\n')
        .trim();

      if (!payload) return;

      if (payload === '[DONE]') {
        handlers.onDone?.();
        return;
      }

      let event: StreamEventPayload;
      try {
        event = JSON.parse(payload) as StreamEventPayload;
      } catch {
        return;
      }

      handlers.onEvent?.(event);

      if (event.type === 'token' && typeof event.content === 'string' && event.content.length > 0) {
        handlers.onToken?.(event.content, event);
      }
    };

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const frames = buffer.split(/\r?\n\r?\n/);
      buffer = frames.pop() ?? '';
      for (const frame of frames) {
        processFrame(frame);
      }
    }

    buffer += decoder.decode();
    if (buffer.trim()) {
      processFrame(buffer);
    }
  },
};