<template>
  <div class="container">
    <Suspense>
      <Chat />
      <template #fallback>
        <p>Загрузка...</p>
      </template>
    </Suspense>
  </div>
</template>

<script setup lang="ts">
import { Chat } from './modules/chat';
</script>
