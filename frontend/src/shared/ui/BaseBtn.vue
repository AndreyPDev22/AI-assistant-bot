<template>
  <component
    :is="as"
    :type="as === 'button' ? type : undefined"
    :class="['base-btn', `base-btn--${size}`, `base-btn--${variant}`]"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
import type { Component } from 'vue';

import { BtnSize, BtnType, BtnVariant } from './types';

const {
  as = 'button',
  variant = BtnVariant.PRIMARY,
  size = BtnSize.LG,
  type = BtnType.BUTTON,
} = defineProps<{
  as?: string | Component;
  variant?: BtnVariant;
  size?: BtnSize;
  type?: BtnType;
}>();
</script>

<style lang="scss" scoped>
@use '@/styles/breakpoints' as *;

:root[data-theme='dark'] {
  .base-btn {
    --disabled-background: #6a5154;
    --disabled-color: white;
  }
}

.base-btn {
  $primary: var(--base-btn-primary, var(--color-pink-150));
  --disabled-background: #eee4e5;
  --disabled-color: #4d4d4d;

  display: flex;
  justify-content: center;
  align-items: center;

  width: 100%;

  text-decoration: none;

  border: 1px solid $primary;
  border-radius: 46px;

  background-color: $primary;
  cursor: pointer;

  &--sm {
    height: 40px;
    border-radius: 36px;

    @include tablet {
      height: 48px;
    }
  }

  &--md {
    height: 40px;
  }

  &--lg {
    height: 50px;
  }

  &--outline {
    background-color: transparent;
  }

  &:disabled {
    color: var(--disabled-color);
    border-color: var(--disabled-background);
    background-color: var(--disabled-background);
    cursor: default;
  }
}
</style>
