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
      <img
        class="chat__welcome-logo"
        src="@/shared/assets/star.svg"
        alt=""
      />
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
@use '@/styles/breakpoints' as *;

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
    flex-direction: column;
    gap: 10px;

    align-items: center;
    justify-content: center;
  }

  &__welcome-logo {
    display: none;
    width: 35px;
    height: 35px;
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

  @include tablet {
    width: 100%;
    max-width: 600px;
    margin-inline: auto;

    &__welcome-logo {
      display: block;
    }

    &__welcome-title {
      font-size: var(--font-size-2xl);
      max-width: none;
    }
  }

  @include desktop {
    &__welcome-logo {
      width: 37px;
      height: 37px;
    }

    &__welcome-title {
      font-size: var(--font-size-xl);
    }

    &--empty {
      justify-content: center;
      gap: 20px;

      .chat__welcome {
        flex: none;
        flex-direction: row;
        gap: 3px;
      }

      .chat__input {
        margin-top: 0;
      }
    }
  }
}
</style>
