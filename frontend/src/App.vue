<template>
  <div class="container">
    <Suspense>
      <ChatsList />
      <template #fallback>
        <p>Загрузка чатов...</p>
      </template>
    </Suspense>
  </div>
  <div class="container container--chat">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { ChatsList } from '@/modules/chat';
</script>

<style lang="scss" scoped>
.container {
  &--chat {
    height: 100dvh;

    padding-top: 40px;
    padding-bottom: 25px;
  }
}
</style>
