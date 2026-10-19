import type { Message, MessagePayload } from '@/modules/message';
import { apiRequest } from '@/shared/api/client';

export const chatApi = {
  getMessages: (chatId: string) => {
    return apiRequest<Message[]>(`/api/chats/${chatId}/messages`);
  },

  // TODO: files содержат blob:-ссылки (выбор файла, голосовые), серверу они недоступны.
  // Когда определится контракт бэкенда, отправлять реальные File (multipart/form-data) или загружать отдельно.
  sendMessage: (chatId: string, payload: MessagePayload) =>
    apiRequest<Message>(`/api/chats/${chatId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
};
