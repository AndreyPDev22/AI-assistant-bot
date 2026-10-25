<template>
  <div class="base-select">
    <select
      :id
      v-model="selected"
      class="base-select__select"
      :name
      :aria-label="label"
    >
      <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
      >
        {{ option.label }}
      </option>
    </select>
    <img
      class="base-select__chevron"
      src="./assets/chevron.svg"
      alt=""
    />
  </div>
</template>

<script setup lang="ts">
import type { SelectOption } from './types';

defineProps<{
  options: SelectOption[];
  id?: string;
  name?: string;
  label?: string;
}>();

const selected = defineModel<string>();
</script>

<style lang="scss" scoped>
.base-select {
  position: relative;
  width: 102px;
  height: 27px;

  &__select {
    width: 100%;
    height: 100%;
    padding-inline: 10px 27px;

    border: none;
    border-radius: 6px;

    background-color: var(--color-pink-150);
    cursor: pointer;
    appearance: none;

    &:focus-visible {
      outline: 2px solid var(--color-pink-600);
      outline-offset: 2px;
    }
  }

  &__chevron {
    position: absolute;
    top: 12px;
    right: 15px;

    pointer-events: none;
  }
}
</style>
