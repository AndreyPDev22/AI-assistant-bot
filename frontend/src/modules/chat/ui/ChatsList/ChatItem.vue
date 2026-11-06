<template>
  <li :class="['chat', { 'chat--opened': opened }]">
    <RouterLink
      class="chat__link"
      :to="{ name: RouteNames.CHAT, params: { chatId: chat.id } }"
      @click="$emit('navigate')"
    >
      <span class="chat__title">{{ chat.messages[0]?.text || 'Новый чат' }}</span>
    </RouterLink>
    <button
      v-if="opened"
      class="chat__actions-close"
      type="button"
      aria-label="Закрыть"
      @click="$emit('close')"
    >
      <img
        src="./assets/close.svg"
        alt=""
      />
    </button>
    <button
      v-else
      class="chat__menu-btn"
      type="button"
      aria-label="Действия с чатом"
      @click.stop="$emit('open')"
    >
      <img
        src="./assets/dots.svg"
        alt=""
      />
    </button>
    <ul
      v-if="opened"
      v-click-outside="() => $emit('close')"
      class="chat__actions"
    >
      <li
        v-for="action in chatActions"
        :key="action.title"
      >
        <button
          class="chat__action"
          type="button"
          @click="
            {
              action.action();
              $emit('close');
            }
          "
        >
          <img
            :src="action.icon"
            alt=""
          />
          <span>{{ action.title }}</span>
        </button>
      </li>
    </ul>
  </li>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { toast } from 'vue3-toastify';
import clickOutside from 'click-outside-vue3';

import { RouteNames } from '../../routes';

import type { Chat } from '../../model/chat';
import { useChatStore } from '../../model/store';

import heartIcon from './assets/heart.svg';
import trashIcon from './assets/trash.svg';

const { chat } = defineProps<{
  chat: Chat;
  opened: boolean;
}>();

defineEmits<{
  open: [];
  close: [];
  navigate: [];
}>();

const vClickOutside = clickOutside.directive;

const { t } = useI18n();
const chatStore = useChatStore();

const chatActions = computed(() => [
  {
    title: chat.isFavorite ? t('chats.deleteFromFavorite') : t('chats.addToFavorite'),
    icon: heartIcon,
    action: async () => {
      try {
        await chatStore.toggleFavorite(chat.id);
      } catch (err) {
        toast.error(err);
      }
    },
  },
  {
    title: t('chats.deleteChat'),
    icon: trashIcon,
    action: async () => {
      try {
        await chatStore.deleteChat(chat.id);
      } catch (err) {
        toast.error(err);
      }
    },
  },
]);
</script>

<style lang="scss" scoped>
@use '@/styles/breakpoints' as *;

.chat {
  position: relative;

  &__link {
    display: block;
    margin-inline: -10px;
    padding: 5px 40px 5px 10px;
    overflow: hidden;

    line-height: 1.2;

    color: inherit;
    text-decoration: none;

    &:hover,
    .chat--opened &,
    .chat:has(.chat__actions-close:hover, .chat__menu-btn:hover) & {
      background-color: var(--color-pink-125);
    }

    &.router-link-active {
      color: var(--color-pink-600);
    }
  }

  &__title {
    display: block;
    position: relative;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  &__menu-btn {
    position: absolute;
    top: 0;
    right: -10px;
    bottom: 0;

    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;

    border: none;
    background: none;
    cursor: pointer;

    @include tablet {
      visibility: hidden;

      .chat:hover & {
        visibility: visible;
      }
    }
  }

  &__actions {
    position: absolute;
    top: 100%;
    right: -10px;
    left: -10px;
    z-index: 10;

    padding-top: 5px;

    list-style-type: none;
    border-radius: 2px;
    background-color: var(--color-pink-50);

    @include tablet {
      background-color: var(--color-pink-125);
    }
  }

  &__actions-close {
    position: absolute;
    top: 50%;
    right: -10px;
    z-index: 11;

    display: flex;
    padding: 5px 10px;
    transform: translateY(-50%);

    border: none;
    background: none;
    cursor: pointer;
  }

  &__action {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    height: 33px;
    padding: 0 10px;

    border: none;
    background: none;
    font: inherit;
    text-align: left;
    color: var(--color-pink-600);
    cursor: pointer;

    img {
      flex-shrink: 0;
      width: 14px;
    }

    span {
      color: inherit;
    }
  }
}
</style>
