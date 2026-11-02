<template>
  <Transition name="app-loader">
    <AppLoader v-if="!isFontsLoaded" />
  </Transition>
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
        <div
          v-else-if="view === AppView.PROFILE"
          class="app__profile"
        >
          <RegistrationForm @registered="view = AppView.CHAT" />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { promiseTimeout, useMediaQuery } from '@vueuse/core';

import { AppHeader, AppLoader, AppSidebar, AppView, RegistrationForm } from '@/widgets';
import { ChatsList, AddChatBtn } from '@/modules/chat';

const TABLET_MIN_WIDTH = 744;
const DESKTOP_MIN_WIDTH = 1440;
const MIN_LOADER_DURATION = 1000;

const isTablet = useMediaQuery(`(min-width: ${TABLET_MIN_WIDTH}px)`);
const isDesktop = useMediaQuery(`(min-width: ${DESKTOP_MIN_WIDTH}px)`);

const isFontsLoaded = ref(false);

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

onMounted(async () => {
  await Promise.all([document.fonts.ready, promiseTimeout(MIN_LOADER_DURATION)]);
  isFontsLoaded.value = true;
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

.app-loader-leave-active {
  transition: opacity 0.3s;
}

.app-loader-leave-to {
  opacity: 0;
}

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

    position: relative;
    isolation: isolate;
    overflow: hidden;

    height: 100dvh;
    min-width: 0;
    padding: 30px 30px 25px;

    &::before {
      --spot-size: 597px;

      position: absolute;
      content: '';
      top: 50%;
      left: 50%;

      width: var(--spot-size);
      height: var(--spot-size);
      transform: translate(-50%, -50%);

      background: radial-gradient(
        closest-side,
        color-mix(in srgb, var(--color-pink-200) 75%, transparent) 0%,
        color-mix(in srgb, var(--color-pink-200) 68%, transparent) 25%,
        color-mix(in srgb, var(--color-pink-200) 50%, transparent) 45%,
        color-mix(in srgb, var(--color-pink-200) 25%, transparent) 65%,
        color-mix(in srgb, var(--color-pink-200) 6%, transparent) 85%,
        transparent 100%
      );

      pointer-events: none;
      z-index: -1;
    }
  }

  &__content {
    width: 100%;
    min-height: 0;
    margin-top: 43px;

    flex: 1;
    display: flex;
    flex-direction: column;
  }

  &__loading {
    height: 100%;
  }

  &__profile {
    width: 100%;
    max-width: 260px;
    margin-inline: auto;
    overflow-y: auto;
  }

  @include tablet {
    &__backdrop {
      display: block;
    }

    &__main {
      padding-bottom: 40px;

      &::before {
        --spot-size: 1048px;
      }
    }

    &__profile {
      max-width: 236px;
    }
  }

  @include desktop {
    &__backdrop {
      display: none;
    }

    &__main {
      padding-top: 40px;

      &::before {
        --spot-size: 1444px;
      }
    }

    &__content {
      margin-top: 0;
    }
  }
}
</style>
