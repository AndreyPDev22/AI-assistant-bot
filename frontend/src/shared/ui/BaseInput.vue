<template>
  <div :class="['base-input', { 'base-input--optional': optional }]">
    <label
      v-if="placeholder"
      class="base-input__label"
      :for="id"
    >
      {{ placeholder }}
    </label>
    <input
      :id
      v-model="value"
      class="base-input__input"
      :class="`base-input__input--${size}`"
      :name
      :type
      :placeholder
      :required
      :aria-describedby="description ? descriptionId : undefined"
    />
    <p
      v-if="description"
      :id="descriptionId"
      class="base-input__description"
    >
      {{ description }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { InputTypeHTMLAttribute } from 'vue';

import { InputSize } from './types';

const {
  id,
  type = 'text',
  placeholder = '',
  description = '',
  size = InputSize.MD,
} = defineProps<{
  id: string;
  name: string;
  type?: InputTypeHTMLAttribute;
  placeholder?: string;
  description?: string;
  required?: boolean;
  optional?: boolean;
  size?: InputSize;
}>();

const value = defineModel<string>({ default: '' });

const descriptionId = computed(() => `${id}-description`);
</script>

<style lang="scss" scoped>
.base-input {
  position: relative;

  &__label {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip-path: inset(50%);
    white-space: nowrap;
  }

  &__input {
    display: block;
    width: 100%;
    padding-inline: 20px;

    border: 1px solid var(--color-pink-900);
    border-radius: 46px;

    background-color: transparent;

    &--md {
      height: 40px;
    }

    &--lg {
      height: 50px;
    }

    &::placeholder {
      color: var(--color-pink-600);
    }
  }

  &--optional::before {
    position: absolute;
    top: 0;
    left: -6px;
    content: '*';
    color: var(--color-pink-600);
  }

  &__description {
    margin-top: 5px;
    font-size: 1rem;
    line-height: 1.2;
    color: var(--color-pink-600);
  }
}
</style>
