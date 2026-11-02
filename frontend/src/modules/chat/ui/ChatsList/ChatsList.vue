<template>
  <ul class="chats-list">
    <template
      v-for="type in CHAT_GROUP_ORDER"
      :key="type"
    >
      <li
        v-if="chatGroups[type].length"
        class="chats-group"
      >
        <p class="chats-group__title">{{ CHAT_GROUP_TYPE_TITLES[type] }}</p>
        <ul class="chats-group__chats">
          <ChatItem
            v-for="chat in chatGroups[type]"
            :key="chat.id"
            :chat="chat"
            :opened="openedChatId === chat.id"
            @open="openedChatId = chat.id"
            @close="openedChatId = null"
            @navigate="$emit('closeList')"
          />
        </ul>
      </li>
    </template>
  </ul>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { toast } from 'vue3-toastify';

import { getErrorMessage } from '@/shared/api/client';
import { MILLISECONDS_IN_DAY } from '@/shared/constants';

import { useChatStore } from '../../model/store';
import type { Chat } from '../../model/chat';
import ChatItem from './ChatItem.vue';

enum ChatGroupType {
  FAVORITE = 'favorite',
  TODAY = 'today',
  YESTERDAY = 'yesterday',
  LAST_WEEK = 'week',
  LAST_MONTH = 'month',
  LAST_YEAR = 'year',
  OTHER = 'other',
}

const CHAT_GROUP_ORDER: ChatGroupType[] = [
  ChatGroupType.FAVORITE,
  ChatGroupType.TODAY,
  ChatGroupType.YESTERDAY,
  ChatGroupType.LAST_WEEK,
  ChatGroupType.LAST_MONTH,
  ChatGroupType.LAST_YEAR,
  ChatGroupType.OTHER,
];

const CHAT_GROUP_TYPE_TITLES: Record<ChatGroupType, string> = {
  [ChatGroupType.FAVORITE]: '♡ Избранное',
  [ChatGroupType.TODAY]: 'Сегодня',
  [ChatGroupType.YESTERDAY]: 'Вчера',
  [ChatGroupType.LAST_WEEK]: 'За последнюю неделю',
  [ChatGroupType.LAST_MONTH]: 'За последний месяц',
  [ChatGroupType.LAST_YEAR]: 'За последний год',
  [ChatGroupType.OTHER]: 'Ранее',
};

const CHAT_GROUP_MAX_AGE_IN_DAYS: [ChatGroupType, number][] = [
  [ChatGroupType.TODAY, 1],
  [ChatGroupType.YESTERDAY, 2],
  [ChatGroupType.LAST_WEEK, 7],
  [ChatGroupType.LAST_MONTH, 30],
  [ChatGroupType.LAST_YEAR, 365],
];

const openedChatId = ref<string | null>(null);

defineEmits<{
  closeList: [];
}>();

function getChatGroupType(chat: Chat, now: number): ChatGroupType {
  if (chat.isFavorite) {
    return ChatGroupType.FAVORITE;
  }

  const timeDelta = now - new Date(chat.updatedAt).getTime();
  const group = CHAT_GROUP_MAX_AGE_IN_DAYS.find(([, maxAgeInDays]) => {
    return timeDelta < maxAgeInDays * MILLISECONDS_IN_DAY;
  });

  return group ? group[0] : ChatGroupType.OTHER;
}

const chatStore = useChatStore();

try {
  await chatStore.fetchChats();
} catch (error) {
  toast.error(getErrorMessage(error, 'Не удалось загрузить чаты'));
}

const chatGroups = computed(() => {
  const groups: Record<ChatGroupType, Chat[]> = {
    [ChatGroupType.FAVORITE]: [],
    [ChatGroupType.TODAY]: [],
    [ChatGroupType.YESTERDAY]: [],
    [ChatGroupType.LAST_WEEK]: [],
    [ChatGroupType.LAST_MONTH]: [],
    [ChatGroupType.LAST_YEAR]: [],
    [ChatGroupType.OTHER]: [],
  };

  const now = Date.now();
  chatStore.chats.forEach((chat) => {
    groups[getChatGroupType(chat, now)].push(chat);
  });

  return groups;
});
</script>

<style lang="scss" scoped>
.chats-list,
.chats-group__chats {
  display: flex;
  flex-direction: column;
  list-style-type: none;
}

.chats-list {
  gap: 25px;
  height: 100%;

  margin-inline: -10px;
  padding-inline: 10px;

  overflow-y: auto;
  scrollbar-width: none;
}

.chats-group {
  &__title {
    font-size: var(--font-size-md);
    line-height: 1.2;
    font-weight: 500;
    color: var(--color-pink-600);
  }

  &__chats {
    margin-top: 10px;
  }
}
</style>
