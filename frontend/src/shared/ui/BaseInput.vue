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
      :class="[
        'base-input__input',
        `base-input__input--${size}`,
        { 'base-input__input--error': errorText },
      ]"
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
    <p
      v-if="errorText"
      class="base-input__error-text"
    >
      {{ errorText }}
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
  errorText = '',
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
  errorText?: string;
}>();

const value = defineModel<string>({ default: '' });

const descriptionId = computed(() => `${id}-description`);
</script>

<style lang="scss" scoped>
:root[data-theme='dark'] {
  .base-input {
    --error-input-border-color: #d64c59;
    --error-message-color: #d64c59;
    --error-message-background: black;
  }
}

.base-input {
  --error-input-border-color: #c21122;
  --error-message-color: #a51a27;
  --error-message-background: white;

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

    &--error {
      border-color: var(--error-input-border-color);
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

  &__error-text {
    position: absolute;
    bottom: -33px;
    left: 0;
    right: 0;

    padding-block: 7px;

    text-align: center;
    color: var(--error-message-color);

    border: 1px solid var(--error-message-color);
    background-color: var(--error-message-background);

    z-index: 100;
  }
}
</style>
