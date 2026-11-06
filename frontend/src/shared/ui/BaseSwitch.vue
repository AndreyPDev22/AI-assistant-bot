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
      <img
        v-if="trackIcon"
        class="base-switch__icon base-switch__icon--track"
        :src="trackIcon"
        alt=""
      />
      <slot name="track" />
    </span>
    <span class="base-switch__thumb">
      <img
        v-if="thumbIcon"
        class="base-switch__icon base-switch__icon--thumb"
        :src="thumbIcon"
        alt=""
      />
      <slot name="thumb" />
    </span>
  </label>
</template>

<script setup lang="ts" generic="T extends boolean | string">
import { computed } from 'vue';

const {
  id = 'switch',
  name = 'switch',
  label = 'switch',
  onValue = undefined,
  offValue = undefined,
  trackIcon = undefined,
  thumbIcon = undefined,
} = defineProps<{
  id?: string;
  name?: string;
  label?: string;
  onValue?: T;
  offValue?: T;
  trackIcon?: string;
  thumbIcon?: string;
}>();

const model = defineModel<T>({ required: true });

const checked = computed({
  get: () => {
    if (onValue === undefined) {
      return Boolean(model.value);
    }
    return model.value === onValue;
  },
  set: (value: boolean) => {
    if (onValue === undefined) {
      model.value = value as T;
      return;
    }
    model.value = (value ? onValue : offValue) as T;
  },
});
</script>

<style lang="scss" scoped>
:root[data-theme='dark'] {
  .base-switch {
    --box-shadow: #754848;
  }
}
.base-switch {
  --box-shadow: #c09296;

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
    gap: 4px;

    width: 100%;
    height: 100%;
    padding-inline: 6px;

    border-radius: 200px;
    background-color: var(--color-pink-150);
    box-shadow: inset 0 2px 4px var(--box-shadow);
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

  &__icon {
    display: block;
    flex-shrink: 0;

    width: 16px;
    height: 16px;

    object-fit: contain;
    pointer-events: none;

    &--thumb {
      width: 14px;
      height: 14px;
    }
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

  img.base-switch__icon {
    filter: brightness(0) saturate(100%) invert(39%) sepia(12%) saturate(600%) hue-rotate(314deg)
      brightness(88%) contrast(85%);
  }
}
</style>
