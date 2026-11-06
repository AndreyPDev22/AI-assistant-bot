<template>
  <MessageItem
    v-for="message in chatStore.messages"
    :key="message.id"
    :message
  />

  <div
    v-if="isAwaitingAssistant"
    class="typing-indicator"
  >
    <span class="typing-indicator__dot" />
    <span class="typing-indicator__dot" />
    <span class="typing-indicator__dot" />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

import { MessageItem } from '@/modules/message';

import { useChatStore } from '../model/store';

const { chatId, isAwaitingAssistant = false } = defineProps<{
  chatId: string;
  isAwaitingAssistant?: boolean;
}>();

const router = useRouter();

const chatStore = useChatStore();

try {
  await chatStore.fetchMessages(chatId);
} catch {
  router.push({ path: '/' });
}
</script>

<style lang="scss" scoped>
.typing-indicator {
  display: inline-flex;
  align-items: center;
  gap: 4px;

  align-self: flex-start;
  padding: 12px 16px;

  border-radius: 16px;
  background-color: var(--color-pink-100);

  &__dot {
    width: 6px;
    height: 6px;

    border-radius: 50%;
    background-color: var(--color-pink-600);

    animation: typing-bounce 1.2s infinite ease-in-out;

    &:nth-child(2) {
      animation-delay: 0.15s;
    }

    &:nth-child(3) {
      animation-delay: 0.3s;
    }
  }
}

@keyframes typing-bounce {
  0%,
  60%,
  100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  30% {
    transform: translateY(-4px);
    opacity: 1;
  }
}
</style>
