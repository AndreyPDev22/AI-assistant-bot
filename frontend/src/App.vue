<template>
  <div class="app">
    <template v-if="isTablet">
      <AppSidebar
        :is-open="isSidebarOpen"
        @open="isSidebarOpen = true"
        @close="isSidebarOpen = false"
        @navigate="onSidebarNavigate(AppView.CHAT)"
        @open-profile="onSidebarNavigate(AppView.PROFILE)"
      />
      <div
        v-if="isSidebarOpen"
        class="app__backdrop"
        @click="isSidebarOpen = false"
      />
    </template>

    <div class="app__main">
      <AppHeader
        v-model="view"
        :is-menu-open
        @menu-click="onMenuClick"
      />

      <main class="app__content">
        <KeepAlive>
          <RouterView v-if="view === AppView.CHAT" />
        </KeepAlive>
        <template v-if="view === AppView.LIST">
          <Suspense>
            <ChatsList @close-list="view = AppView.CHAT" />
            <template #fallback>
              <p class="app__loading">Загрузка чатов...</p>
            </template>
          </Suspense>
          <AddChatBtn @select="view = AppView.CHAT" />
        </template>
        <div v-else-if="view === AppView.PROFILE">Профиль</div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useMediaQuery } from '@vueuse/core';

import { AppHeader, AppSidebar, AppView } from '@/widgets';
import { ChatsList, AddChatBtn } from '@/modules/chat';

const TABLET_MIN_WIDTH = 744;
const DESKTOP_MIN_WIDTH = 1440;

const isTablet = useMediaQuery(`(min-width: ${TABLET_MIN_WIDTH}px)`);
const isDesktop = useMediaQuery(`(min-width: ${DESKTOP_MIN_WIDTH}px)`);

const view = ref(AppView.CHAT);
const isSidebarOpen = ref(isDesktop.value);

const isMenuOpen = computed(() =>
  isTablet.value ? isSidebarOpen.value : view.value === AppView.LIST,
);

watch(isDesktop, (value) => {
  isSidebarOpen.value = value;
});

watch(isTablet, (value) => {
  if (value && view.value === AppView.LIST) {
    view.value = AppView.CHAT;
  }
});

function onMenuClick() {
  if (isTablet.value) {
    isSidebarOpen.value = !isSidebarOpen.value;
  } else {
    view.value = view.value === AppView.LIST ? AppView.CHAT : AppView.LIST;
  }
}

function onSidebarNavigate(target: AppView) {
  view.value = target;

  if (!isDesktop.value) {
    isSidebarOpen.value = false;
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/breakpoints' as *;

.app {
  display: flex;
  height: 100dvh;

  &__backdrop {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 9;

    background-color: var(--color-white-50);
  }

  &__main {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    flex: 1;

    height: 100dvh;
    min-width: 0;
    padding: 30px 30px 25px;
  }

  &__content {
    width: 100%;
    min-height: 0;
    margin-top: 43px;

    flex: 1;
    display: flex;
    flex-direction: column;

    position: relative;
    isolation: isolate;

    &::before {
      position: absolute;
      content: '';
      top: 50%;
      left: 50%;

      width: 273px;
      height: 273px;
      transform: translate(-50%, -50%);

      filter: blur(81px);
      background: var(--color-pink-200);
      border-radius: 50%;

      pointer-events: none;
      z-index: -1;
    }
  }

  &__loading {
    height: 100%;
  }

  @include tablet {
    &__backdrop {
      display: block;
    }

    &__main {
      padding-bottom: 40px;
    }

    &__content::before {
      width: 488px;
      height: 488px;
    }
  }

  @include desktop {
    &__backdrop {
      display: none;
    }

    &__main {
      padding-top: 40px;
    }

    &__content {
      margin-top: 0;

      &::before {
        width: 645px;
        height: 645px;
      }
    }
  }
}
</style>
