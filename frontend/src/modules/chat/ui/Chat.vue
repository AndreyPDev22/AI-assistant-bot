<template>
  <div class="chat">
    <MessageItem
      v-for="message in chatStore.messages"
      :key="message.id"
      :message
    />
    <MessageInput
      ref="messageInput"
      class="chat__input"
      :is-disabled="isSendingMessage"
      @send="sendMessage"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, useTemplateRef } from 'vue';
import { toast } from 'vue3-toastify';

import { MessageInput, MessageItem, type Message, type MessagePayload } from '@/modules/message';
import { ApiError } from '@/shared/api/client';
import { useChatStore } from '../model/store';

const TEST_CHAT_ID = '1';

function getErrorMessage(error: unknown, fallback: string) {
  return error instanceof ApiError ? error.message : fallback;
}

const chatStore = useChatStore();

try {
  await chatStore.fetchMessages(TEST_CHAT_ID);
} catch (error) {
  toast.error(getErrorMessage(error, 'Не удалось загрузить сообщения'));
}

const messageInput = useTemplateRef('messageInput');
const isSendingMessage = ref(false);

async function sendMessage(payload: MessagePayload) {
  isSendingMessage.value = true;

  let response: Message | undefined;
  try {
    response = await chatStore.sendMessage(TEST_CHAT_ID, payload);
  } catch (error) {
    toast.error(getErrorMessage(error, 'Не удалось отправить сообщение'));
  } finally {
    isSendingMessage.value = false;
  }

  if (response) {
    messageInput.value?.clear();
  }
}
</script>

<style lang="scss" scoped>
.chat {
  &__input {
    margin-top: 30px;
  }
}
</style>
