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
      @click="$emit('openProfile')"
    >
      <span class="sidebar__user-avatar">
        <img
          src="../AppHeader/assets/user.svg"
          alt=""
        />
      </span>
      <span class="sidebar__user-name">Пользователь</span>
    </button>
  </aside>
</template>

<script setup lang="ts">
import { AddChatBtn, ChatsList } from '@/modules/chat';

defineProps<{
  isOpen: boolean;
}>();

defineEmits<{
  open: [];
  close: [];
  navigate: [];
  openProfile: [];
}>();
</script>

<style lang="scss" scoped>
@use '@/styles/breakpoints' as *;

.sidebar {
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

    img {
      width: 14px;
      height: 19px;
    }
  }

  &__user-name {
    font-size: var(--font-size-lg);
    font-weight: 500;
  }

  .chats {
    flex: 1;
    min-height: 0;
    margin-top: 30px;
    overflow-y: auto;

    &__loading {
      height: 100%;
    }
  }

  @include tablet {
    display: flex;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 10;

    transform: translateX(-100%);
    visibility: hidden;
    transition:
      transform 0.3s,
      visibility 0.3s;

    &--open {
      transform: none;
      visibility: visible;
    }
  }

  @include desktop {
    position: static;
    transform: none;
    visibility: visible;

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
        padding-inline: 0;

        span {
          display: none;
        }
      }
    }
  }
}
</style>
