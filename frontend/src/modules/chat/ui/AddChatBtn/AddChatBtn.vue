<template>
  <BaseBtn
    :as="RouterLink"
    class="add-chat-btn"
    :size="BtnSize.SM"
    :to="{ name: RouteNames.CHAT }"
    @click="$emit('select')"
  >
    <div class="add-chat-btn__info">
      <img
        src="./assets/icon.svg"
        alt=""
      />
      <span>Новый чат</span>
    </div>
  </BaseBtn>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router';
import { BaseBtn, BtnSize } from '@/shared/ui';
import { RouteNames } from '../../routes';

defineEmits<{
  select: [];
}>();
</script>

<style lang="scss" scoped>
.add-chat-btn {
  margin-top: 20px;
  --base-btn-primary: var(--color-pink-100);

  &__info {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 11px;
  }

  img {
    width: 18px;
    height: 18px;
  }
}
</style>
