<template>
  <aside :class="['sidebar', { 'sidebar--open': isOpen }]">
    <div class="sidebar__header">
      <button
        class="sidebar__logo"
        aria-label="Открыть боковую панель"
        @click="$emit('open')"
      >
        <img
          src="@/shared/assets/star.svg"
          alt=""
        />
      </button>
      <h2 class="sidebar__title">AI-ассистент</h2>
      <button
        class="sidebar__close"
        aria-label="Скрыть боковую панель"
        @click="$emit('close')"
      >
        <img
          src="./assets/close.svg"
          alt=""
        />
      </button>
    </div>
    <AddChatBtn @select="$emit('navigate')" />
    <div class="chats">
      <Suspense>
        <ChatsList @close-list="$emit('navigate')" />
        <template #fallback>
          <p class="chats__loading">Загрузка чатов...</p>
        </template>
      </Suspense>
    </div>
    <button
      class="sidebar__user"
      aria-label="Открыть профиль"
      @click="$emit('toggleProfile')"
    >
      <img
        :class="[
          'sidebar__user-avatar',
          { 'sidebar__user-avatar--default': profilePhoto === DEFAULT_USER_IMAGE },
        ]"
        :src="profilePhoto"
        alt=""
      />
      <span class="sidebar__user-name">{{ fullName }}</span>
    </button>
    <div class="sidebar__profile-container"></div>
  </aside>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';

import { AddChatBtn, ChatsList } from '@/modules/chat';
import { useUserStore } from '@/modules/user';

import DEFAULT_USER_IMAGE from '@/shared/assets/user.svg';

defineProps<{
  isOpen: boolean;
}>();

defineEmits<{
  open: [];
  close: [];
  navigate: [];
  toggleProfile: [];
}>();

const { profilePhoto, fullName } = storeToRefs(useUserStore());
</script>

<style lang="scss" scoped>
@use '@/styles/breakpoints' as *;

.sidebar {
  position: relative;
  display: none;
  flex-direction: column;
  flex-shrink: 0;

  height: 100dvh;
  width: 296px;
  padding: 20px;

  background-color: var(--color-pink-50);
  box-shadow: 2px 6px 5px 0px var(--color-shadow);

  border-top-right-radius: 10px;
  border-bottom-right-radius: 10px;

  &__header {
    display: flex;
    align-items: center;
  }

  &__logo {
    display: flex;
    flex-shrink: 0;
    padding: 0;

    border: none;
    background: none;

    cursor: pointer;

    img {
      width: 37px;
      height: 37px;
    }
  }

  &__title {
    margin-left: 4px;

    font-family: 'Montserrat';
    font-size: var(--font-size-xl);
    font-weight: 500;
  }

  &__close {
    display: flex;
    margin-left: auto;
    padding: 0;

    border: none;
    background: none;

    cursor: pointer;

    img {
      width: 20px;
      height: 17px;
    }
  }

  &__user {
    position: relative;

    display: flex;
    align-items: center;
    gap: 12px;

    margin-top: 30px;
    padding: 0;

    border: none;
    background: none;

    cursor: pointer;
  }

  &__user-avatar {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-shrink: 0;

    width: 48px;
    height: 48px;

    border-radius: 50%;
    background-color: var(--color-pink-300);

    &--default {
      padding: 8px 12px;
    }
  }

  &__user-name {
    font-size: var(--font-size-lg);
    font-weight: 500;
  }

  &__profile-container {
    &:has(*) {
      position: absolute;
      left: 10px;
      right: 10px;
      top: calc(100% - 76px);

      padding: 20px 15px;
      transform: translateY(-100%);

      border-radius: 11px;
      background-color: white;
      box-shadow: 2px 2px 6.7px 0px #ba9b9d;
    }
  }

  .chats {
    flex: 1;
    min-height: 0;
    margin: 30px -10px 0;
    padding-inline: 10px;
    overflow-y: auto;

    &__loading {
      height: 100%;
    }
  }

  @include tablet {
    display: none;
    top: 0;
    left: 0;
    z-index: 10;

    transform: translateX(-100%);
    visibility: hidden;
    transition:
      transform 0.3s,
      visibility 0.3s;

    &--open {
      display: flex;
      transform: none;
      visibility: visible;
    }
  }

  @include desktop {
    transform: none;
    visibility: visible;
    padding-bottom: 15px;

    :deep(.add-chat-btn) {
      margin-top: 15px;
    }

    &:not(.sidebar--open) {
      align-items: center;
      width: 68px;
      padding-inline: 10px;

      .sidebar__title,
      .sidebar__close,
      .sidebar__user-name,
      .chats {
        display: none;
      }

      .sidebar__user {
        margin-top: auto;
      }

      :deep(.add-chat-btn) {
        width: 48px;
        margin-top: 20px;
        padding-inline: 0;

        span {
          display: none;
        }
      }
    }
  }
}
</style>
