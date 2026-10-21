<template>
  <MessageItem
    v-for="message in chatStore.messages"
    :key="message.id"
    :message
  />
</template>

<script setup lang="ts">
import { toast } from 'vue3-toastify';

import { MessageItem } from '@/modules/message';

import { getErrorMessage } from '@/shared/api/client';

import { useChatStore } from '../model/store';

const { chatId } = defineProps<{
  chatId: string;
}>();

const chatStore = useChatStore();

try {
  await chatStore.fetchMessages(chatId);
} catch (error) {
  toast.error(getErrorMessage(error, 'Не удалось загрузить сообщения'));
}
</script>
