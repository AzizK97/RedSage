// src/api/chat.ts
import { apiClient } from './client';
import type { 
  ChatResponse, 
  ApproveRequest, 
  ApproveResponse, 
  ThreadSummary, 
  CreateThreadResponse 
} from './types.ts';

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
};