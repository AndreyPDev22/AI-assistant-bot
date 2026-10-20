<template>
  <div class="container container--chat">
    <Chat />
  </div>
</template>

<script setup lang="ts">
import { Chat } from './modules/chat';
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
