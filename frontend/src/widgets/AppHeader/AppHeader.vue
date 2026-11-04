<template>
  <header class="header">
    <button
      class="header__burger-button"
      :aria-label="burgerMenuAriaLabel"
      @click="$emit('menuClick')"
    >
      <img
        src="./assets/burger-menu.svg"
        alt=""
      />
    </button>
    <RouterLink
      to="/"
      class="header__logo"
      @click="view = AppView.CHAT"
    >
      <img
        src="@/shared/assets/star.svg"
        alt=""
      />
    </RouterLink>
    <button
      :class="['header__account', { 'header__account--default': userPhoto === DEFAULT_USER_PHOTO }]"
      :aria-label="accountAriaLabel"
      @click="toggleView(AppView.PROFILE)"
    >
      <img
        :src="userPhoto"
        alt=""
      />
    </button>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';

import { useUserStore } from '@/modules/user';

import DEFAULT_USER_PHOTO from '@/shared/assets/user.svg';

import { AppView } from './types';

const view = defineModel<AppView>({ default: AppView.CHAT });

const { isMenuOpen } = defineProps<{
  isMenuOpen: boolean;
}>();

defineEmits<{
  menuClick: [];
}>();

const { user } = storeToRefs(useUserStore());

const userPhoto = computed(() => user.value?.photoUrl ?? DEFAULT_USER_PHOTO);
const burgerMenuAriaLabel = computed(() => (isMenuOpen ? 'Скрыть меню' : 'Открыть меню'));
const accountAriaLabel = computed(() =>
  view.value === AppView.PROFILE ? 'Закрыть профиль' : 'Открыть профиль',
);

function toggleView(target: AppView.PROFILE) {
  view.value = view.value === target ? AppView.CHAT : target;
}
</script>

<style lang="scss" scoped>
@use '@/styles/breakpoints' as *;

.header {
  width: 100%;

  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;

  &__burger-button,
  &__account {
    background: none;
    border: none;

    cursor: pointer;
  }

  &__logo {
    position: relative;
    display: block;
    width: 25px;
    height: 25px;

    img {
      width: 100%;
      height: 100%;
    }

    &::before,
    &::after {
      position: absolute;
      content: '';
      top: 50%;

      width: 20px;
      border-bottom: 1px solid var(--color-accent);
    }

    &::before {
      right: calc(100% + 8px);
    }

    &::after {
      left: calc(100% + 8px);
    }
  }

  &__burger-button {
    justify-self: start;
  }

  &__account {
    justify-self: end;

    img {
      width: 32px;
      height: 32px;

      border-radius: 50%;
    }

    &--default {
      img {
        width: 14px;
        height: 32px;

        filter: brightness(0);
      }
    }
  }

  @include tablet {
    &__account {
      display: none;
    }
  }

  @include desktop {
    display: none;
  }
}
</style>
