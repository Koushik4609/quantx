import { apiClient, handleApiError } from './client';

export interface ChatMessage {
  id: string;
  message_role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export const getChatHistory = async (userId: string): Promise<ChatMessage[]> => {
  try {
    const response = await apiClient.get(`/ai/history/${userId}`);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const sendChatMessage = async (userId: string, portfolioId: string, message: string): Promise<{response: string, tool_calls_made: string[]}> => {
  try {
    const response = await apiClient.post('/ai/chat', {
      user_id: userId,
      portfolio_id: portfolioId,
      message: message
    });
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};
