<template>
  <label class="base-switch">
    <input
      :id
      v-model="checked"
      class="base-switch__input"
      type="checkbox"
      role="switch"
      :name
      :aria-label="label"
    />
    <span class="base-switch__track">
      <slot name="track" />
    </span>
    <span class="base-switch__thumb">
      <slot name="thumb" />
    </span>
  </label>
</template>

<script setup lang="ts">
defineProps<{
  id?: string;
  name?: string;
  label?: string;
}>();

const checked = defineModel<boolean>({ default: false });
</script>

<style lang="scss" scoped>
.base-switch {
  position: relative;
  display: block;
  width: 55px;
  height: 27px;

  cursor: pointer;

  &__input {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip-path: inset(50%);
  }

  &__track {
    display: flex;
    justify-content: flex-end;
    align-items: center;

    width: 100%;
    height: 100%;
    padding-inline: 6px;

    border-radius: 200px;
    background-color: var(--color-pink-150);
    box-shadow: inset 0 2px 4px #c09296;
  }

  &__thumb {
    position: absolute;
    top: 1px;
    left: 1px;

    display: flex;
    justify-content: center;
    align-items: center;

    width: 25px;
    height: 25px;

    border-radius: 50%;
    background-color: var(--color-white);

    transition: transform 0.2s;
  }

  &__input:checked {
    & ~ .base-switch__track {
      justify-content: flex-start;
    }

    & ~ .base-switch__thumb {
      transform: translateX(28px);
    }
  }

  &__input:focus-visible ~ .base-switch__track {
    outline: 2px solid var(--color-pink-600);
    outline-offset: 2px;
  }
}
</style>
