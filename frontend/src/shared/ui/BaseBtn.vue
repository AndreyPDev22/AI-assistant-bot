<template>
  <component
    :is="as"
    :type="as === 'button' ? 'button' : undefined"
    :class="['base-btn', `base-btn--${size}`, `base-btn--${variant}`]"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
import type { Component } from 'vue';

import { BtnSize, BtnVariant } from './types';

const {
  as = 'button',
  variant = BtnVariant.PRIMARY,
  size = BtnSize.LG,
} = defineProps<{
  as?: string | Component;
  variant?: BtnVariant;
  size?: BtnSize;
}>();
</script>

<style lang="scss" scoped>
@use '@/styles/breakpoints' as *;

$primary: var(--base-btn-primary, var(--color-pink-150));
$disabled: #eee4e5;

.base-btn {
  display: flex;
  justify-content: center;
  align-items: center;

  width: 100%;

  text-decoration: none;

  border: 1px solid transparent;
  border-radius: 46px;

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

  &--primary {
    border-color: $primary;
    background-color: $primary;
  }

  &--outline {
    border-color: #ba9b9d;
    background-color: transparent;
  }

  &:disabled {
    color: #4d4d4d;
    border-color: $disabled;
    background-color: $disabled;
    cursor: default;
  }
}
</style>
