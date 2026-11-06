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
          :is-awaiting-assistant
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
import { ref, computed, watch, useTemplateRef, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { toast } from 'vue3-toastify';

import { MessageInput, SenderRole, type Message, type MessagePayload } from '@/modules/message';
import { AppNotifications, useUserStore } from '@/modules/user';

import { getErrorMessage } from '@/shared/api/client';

import { useChatStore } from '../model/store';
import { RouteNames } from '../routes';
import ChatMessages from './ChatMessages.vue';

const POLLING_INTERVAL_MS = 1000;
const POLLING_TIMEOUT_MS = 15_000;

let pollingTimerId = 0;
let pollingDeadline = 0;
let pollingChatId: string | null = null;

const { chatId = undefined } = defineProps<{
  chatId?: string;
}>();

const router = useRouter();

const chatStore = useChatStore();
const { user } = useUserStore();

const messageInput = useTemplateRef('messageInput');

const isMessagesLoaded = ref(false);
const isSendingMessage = ref(false);
const isAwaitingAssistant = ref(false);

const isEmptyMessagesList = computed(() => {
  return !chatId || (isMessagesLoaded.value && !chatStore.messages.length);
});

watch(
  () => chatId,
  (newChatId) => {
    if (pollingChatId && pollingChatId !== newChatId) {
      stopPolling();
    }
  },
);

onBeforeUnmount(() => {
  stopPolling();
});

function stopPolling() {
  if (pollingTimerId) {
    clearTimeout(pollingTimerId);
    pollingTimerId = 0;
  }
  pollingDeadline = 0;
  pollingChatId = null;
  isAwaitingAssistant.value = false;
}

function startPolling(targetChatId: string, knownAssistantIds: Set<string>) {
  stopPolling();
  pollingChatId = targetChatId;
  pollingDeadline = Date.now() + POLLING_TIMEOUT_MS;
  isAwaitingAssistant.value = true;

  const _createNotification = (message: string) => {
    if (user?.settings.notifications === AppNotifications.ON) {
      new Notification('Ответ готов', {
        body: message,
        icon: '/favicon.ico',
      });
    }
  };

  const tick = async () => {
    try {
      await chatStore.fetchMessages(targetChatId);
    } catch {
      // Не обрабатываем
    }

    const newAssistantMessage = chatStore.messages.find(
      (message) =>
        message.senderRole === SenderRole.ASSISTANT && !knownAssistantIds.has(message.id),
    );

    if (newAssistantMessage) {
      if (!('Notification' in window)) {
        toast.error('Этот браузер не поддерживает уведомления.');
        return;
      }

      if (Notification.permission !== 'granted') {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
          _createNotification(newAssistantMessage.text);
        }
      } else {
        _createNotification(newAssistantMessage.text);
      }
    }

    if (newAssistantMessage || Date.now() >= pollingDeadline) {
      stopPolling();
      return;
    }

    pollingTimerId = setTimeout(tick, POLLING_INTERVAL_MS);
  };

  pollingTimerId = setTimeout(tick, POLLING_INTERVAL_MS);
}

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

  if (!response || sentChatId !== chatId) {
    return;
  }

  messageInput.value?.clear();

  if (!sentChatId) {
    router.push({ name: RouteNames.CHAT, params: { chatId: response.chatId } });
  }

  const knownAssistantIds = new Set(
    chatStore.messages
      .filter((message) => message.senderRole === SenderRole.ASSISTANT)
      .map((message) => message.id),
  );

  startPolling(response.chatId, knownAssistantIds);
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

    &__welcome {
      gap: 5px;
    }

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
