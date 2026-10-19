import { ref } from 'vue';
import { defineStore } from 'pinia';

import type { Message, MessagePayload } from '@/modules/message';

import { chatApi } from '../api/chat';

export const useChatStore = defineStore('chat', () => {
  const messages = ref<Message[]>([]);

  async function fetchMessages(chatId: string) {
    messages.value = await chatApi.getMessages(chatId);
  }

  async function sendMessage(chatId: string, payload: MessagePayload) {
    const message = await chatApi.sendMessage(chatId, payload);
    messages.value.push(message);

    return message;
  }

  return { messages, fetchMessages, sendMessage };
});
