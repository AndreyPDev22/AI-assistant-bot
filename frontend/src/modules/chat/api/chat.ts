import type { Message, MessagePayload } from '@/modules/message';

import { apiRequest, APIResponseStatus } from '@/shared/api/client';

import type { Chat } from '../model/chat';

export const chatApi = {
  getChats: () => {
    return apiRequest<Chat[]>('/api/chats');
  },

  createChat: () => {
    return apiRequest<Chat>('/api/chats', { method: 'POST' });
  },

  getMessages: (chatId: string) => {
    return apiRequest<Message[]>(`/api/chats/${chatId}/messages`);
  },

  // TODO: files содержат blob:-ссылки (выбор файла, голосовые), серверу они недоступны.
  // Когда определится контракт бэкенда, отправлять реальные File (multipart/form-data) или загружать отдельно.
  sendMessage: (chatId: string, payload: MessagePayload) => {
    return apiRequest<Message>(`/api/chats/${chatId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  },

  toggleFavorite: (chatId: string) => {
    return apiRequest<Chat>(`/api/chats/${chatId}/favorite`, { method: 'PATCH' });
  },

  deleteChat: async (chatId: string) => {
    try {
      await apiRequest(`/api/chats/${chatId}`, {
        method: 'DELETE',
      });
    } catch {
      return { status: APIResponseStatus.INTERNAL_SERVER_ERROR };
    }

    return { status: APIResponseStatus.NO_CONTENT };
  },
};
