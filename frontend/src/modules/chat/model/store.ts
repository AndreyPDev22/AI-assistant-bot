import { ref } from 'vue';
import { defineStore } from 'pinia';

import type { Message, MessagePayload } from '@/modules/message';

import { chatApi } from '../api/chat';
import type { Chat } from './chat';

export const useChatStore = defineStore('chat', () => {
  const chats = ref<Chat[]>([]);
  const messages = ref<Message[]>([]);
  const currentChatId = ref<string | null>(null);

  let draftChat: Chat | null = null;

  async function fetchChats() {
    chats.value = await chatApi.getChats();
  }

  async function fetchMessages(chatId: string) {
    currentChatId.value = chatId;

    const fetchedMessages = await chatApi.getMessages(chatId);

    if (currentChatId.value === chatId) {
      messages.value = fetchedMessages;
    }
  }

  function moveChatToTop(chat: Chat) {
    chats.value = [
      chat,
      ...chats.value.filter((item) => {
        return item.id !== chat.id;
      }),
    ];
  }

  async function sendMessageToNewChat(payload: MessagePayload) {
    draftChat ??= await chatApi.createChat();

    const newChat = draftChat;
    const message = await chatApi.sendMessage(newChat.id, payload);

    draftChat = null;
    currentChatId.value = newChat.id;
    messages.value = [message];
    moveChatToTop({ ...newChat, messages: [message], updatedAt: new Date().toISOString() });

    return { chatId: newChat.id, message };
  }

  async function sendMessageToChat(chatId: string, payload: MessagePayload) {
    const message = await chatApi.sendMessage(chatId, payload);

    if (currentChatId.value === chatId) {
      messages.value.push(message);
    }

    const chat = chats.value.find((item) => {
      return item.id === chatId;
    });

    if (chat) {
      chat.messages.push(message);
      chat.updatedAt = new Date().toISOString();
      moveChatToTop(chat);
    }

    return { chatId, message };
  }

  function sendMessage(chatId: string | undefined, payload: MessagePayload) {
    return chatId ? sendMessageToChat(chatId, payload) : sendMessageToNewChat(payload);
  }

  return { chats, messages, fetchChats, fetchMessages, sendMessage };
});
