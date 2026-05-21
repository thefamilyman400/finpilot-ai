import api from './api';
import type { Conversation, Message } from '../types';

export const copilotService = {
  // Get all conversations for the current user
  getConversations: async (params?: {
    page?: number;
    page_size?: number;
  }): Promise<{ conversations: Conversation[]; total: number }> => {
    const response = await api.get<{ conversations: Conversation[]; total: number }>('/copilot/conversations', { params });
    return response.data;
  },

  // Get a specific conversation by ID
  getConversation: async (conversationId: string): Promise<Conversation> => {
    const response = await api.get<Conversation>(`/copilot/conversations/${conversationId}`);
    return response.data;
  },

  // Create a new conversation
  createConversation: async (title?: string): Promise<Conversation> => {
    const response = await api.post<Conversation>('/copilot/conversations', { title });
    return response.data;
  },

  // Send a message in a conversation
  sendMessage: async (conversationId: string, content: string): Promise<Message> => {
    const response = await api.post<Message>(`/copilot/conversations/${conversationId}/messages`, {
      content,
    });
    return response.data;
  },

  // Get messages in a conversation
  getMessages: async (conversationId: string): Promise<Message[]> => {
    const response = await api.get<Message[]>(`/copilot/conversations/${conversationId}/messages`);
    return response.data;
  },

  // Delete a conversation
  deleteConversation: async (conversationId: string): Promise<void> => {
    await api.delete(`/copilot/conversations/${conversationId}`);
  },

  // Update conversation title
  updateConversationTitle: async (conversationId: string, title: string): Promise<Conversation> => {
    const response = await api.patch<Conversation>(`/copilot/conversations/${conversationId}`, { title });
    return response.data;
  },

  // Get AI suggestions based on context
  getSuggestions: async (context?: string): Promise<{ suggestions: string[] }> => {
    const response = await api.post<{ suggestions: string[] }>('/copilot/suggestions', { context });
    return response.data;
  },

  // Analyze financial data with AI
  analyzeFinancials: async (params?: {
    account_ids?: string[];
    time_period?: string;
  }): Promise<{
    analysis: string;
    insights: string[];
    recommendations: string[];
  }> => {
    const response = await api.post('/copilot/analyze', params);
    return response.data;
  },

  // Get quick answers to financial questions
  quickAnswer: async (question: string): Promise<{ answer: string; sources?: string[] }> => {
    const response = await api.post<{ answer: string; sources?: string[] }>('/copilot/quick-answer', {
      question,
    });
    return response.data;
  },
};

// Made with Bob
