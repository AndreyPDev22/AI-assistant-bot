<template>
  <div :class="['chat', { 'chat--empty': isEmptyMessagesList }]">
    <div class="chat__messages">
      <Suspense
        @pending="isMessagesLoaded = false"
        @resolve="isMessagesLoaded = true"
      >
        <ChatMessages
          v-if="chatId"
          :key="chatId"
          :chat-id
        />
        <template #fallback>
          <p>Загрузка сообщений...</p>
        </template>
      </Suspense>
    </div>
    <div class="chat__welcome">
      <h1 class="chat__welcome-title">AI-ассистент для студентов</h1>
    </div>

    <MessageInput
      ref="messageInput"
      class="chat__input"
      :is-disabled="isSendingMessage"
      @send="sendMessage"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, useTemplateRef } from 'vue';
import { useRouter } from 'vue-router';
import { toast } from 'vue3-toastify';

import { MessageInput, type Message, type MessagePayload } from '@/modules/message';

import { getErrorMessage } from '@/shared/api/client';

import { useChatStore } from '../model/store';
import { RouteNames } from '../routes';
import ChatMessages from './ChatMessages.vue';

const { chatId = undefined } = defineProps<{
  chatId?: string;
}>();

const router = useRouter();
const chatStore = useChatStore();

const messageInput = useTemplateRef('messageInput');

const isMessagesLoaded = ref(false);
const isSendingMessage = ref(false);

const isEmptyMessagesList = computed(() => {
  return !chatId || (isMessagesLoaded.value && !chatStore.messages.length);
});

async function sendMessage(payload: MessagePayload) {
  const sentChatId = chatId;

  isSendingMessage.value = true;

  let response: { chatId: string; message: Message } | undefined;
  try {
    response = await chatStore.sendMessage(sentChatId, payload);
  } catch (error) {
    toast.error(getErrorMessage(error, 'Не удалось отправить сообщение'));
  } finally {
    isSendingMessage.value = false;
  }

  if (response && sentChatId === chatId) {
    messageInput.value?.clear();

    if (!sentChatId) {
      router.push({ name: RouteNames.CHAT, params: { chatId: response.chatId } });
    }
  }
}
</script>

<style lang="scss" scoped>
.chat {
  height: 100%;
  gap: 30px;

  &,
  &__welcome,
  &__messages {
    display: flex;
  }

  &,
  &__messages {
    flex-direction: column;
  }

  &__welcome,
  &__messages {
    flex: 1;
  }

  &__welcome {
    display: none;

    align-items: center;
    justify-content: center;
  }

  &__welcome-title {
    font-family: 'Montserrat', sans-serif;
    font-size: var(--font-size-xl);
    line-height: 1.2;
    font-weight: 300;
    text-align: center;
    max-width: 187px;
  }

  &__messages {
    gap: 24px;
    min-height: 0;

    overflow-y: auto;
    scrollbar-width: none;
  }

  &__input {
    margin-top: auto;
    flex-shrink: 0;
  }

  &--empty {
    .chat__messages {
      display: none;
    }

    .chat__welcome {
      display: flex;
    }
  }
}
</style>
