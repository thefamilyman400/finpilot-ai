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

  // Get a specific conversation by ID (with message history)
  getConversation: async (conversationId: string): Promise<Conversation> => {
    const response = await api.get<Conversation>(`/copilot/conversations/${conversationId}`);
    return response.data;
  },

  // Create a new conversation
  createConversation: async (title?: string): Promise<Conversation> => {
    const response = await api.post<Conversation>('/copilot/conversations', { title });
    return response.data;
  },

  // Send a message to the AI assistant and optionally continue an existing conversation
  chat: async (message: string, conversationId?: string) => {
    const response = await api.post<{
      conversation_id: string;
      user_message: Message;
      assistant_message: Message;
      conversation_title: string;
      tokens_used: number;
    }>('/copilot/chat', {
      message,
      conversation_id: conversationId,
    });
    return response.data;
  },

  // Convenience alias for backwards compatibility
  sendMessage: async (conversationId: string | undefined, content: string) => {
    return copilotService.chat(content, conversationId);
  },

  // Get messages in a conversation
  getMessages: async (conversationId: string): Promise<Message[]> => {
    const response = await api.get<Conversation>(`/copilot/conversations/${conversationId}`);
    return response.data.messages;
  },

  // Delete a conversation
  deleteConversation: async (conversationId: string): Promise<void> => {
    await api.delete(`/copilot/conversations/${conversationId}`);
  },

  // Update conversation title
  updateConversationTitle: async (conversationId: string, title: string): Promise<Conversation> => {
    const response = await api.put<Conversation>(`/copilot/conversations/${conversationId}`, { title });
    return response.data;
  },
};

// Made with Bob
