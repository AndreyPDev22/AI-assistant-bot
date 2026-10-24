<template>
  <RouterLink
    class="add-chat-btn"
    :to="{ name: RouteNames.CHAT }"
    @click="$emit('select')"
  >
    <img
      src="./assets/icon.svg"
      alt=""
    />
    <span>Новый чат</span>
  </RouterLink>
</template>

<script setup lang="ts">
import { RouteNames } from '../../routes';

defineEmits<{
  select: [];
}>();
</script>

<style lang="scss" scoped>
@use '@/styles/breakpoints' as *;

.add-chat-btn {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 11px;

  width: 100%;
  margin-top: 20px;
  padding-block: 11px;

  text-decoration: none;

  border: none;
  border-radius: 36px;
  background-color: var(--color-pink-100);

  img {
    width: 18px;
    height: 18px;
  }

  span {
    text-decoration: none;
  }

  @include tablet {
    padding-block: 15px;
  }
}
</style>
