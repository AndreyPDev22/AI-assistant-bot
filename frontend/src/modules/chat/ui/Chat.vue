<template>
  <div :class="['chat', { 'chat--empty': isEmptyMessagesList }]">
    <div class="chat__messages">
      <Suspense @resolve="isMessagesLoaded = true">
        <ChatMessages :chat-id="TEST_CHAT_ID" />
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
import { toast } from 'vue3-toastify';

import { MessageInput, type Message, type MessagePayload } from '@/modules/message';

import { ApiError } from '@/shared/api/client';

import { useChatStore } from '../model/store';
import ChatMessages from './ChatMessages.vue';

const TEST_CHAT_ID = '1';

function getErrorMessage(error: unknown, fallback: string) {
  return error instanceof ApiError ? error.message : fallback;
}

const chatStore = useChatStore();

const messageInput = useTemplateRef('messageInput');

const isMessagesLoaded = ref(false);
const isSendingMessage = ref(false);

const isEmptyMessagesList = computed(() => isMessagesLoaded.value && !chatStore.messages.length);

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
