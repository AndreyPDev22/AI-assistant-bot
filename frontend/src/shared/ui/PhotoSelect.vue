<template>
  <label class="photo-select">
    <span class="photo-select__preview">
      <img
        v-if="previewUrl"
        class="photo-select__image"
        :src="previewUrl"
        alt=""
      />
      <img
        v-else
        class="photo-select__placeholder"
        src="@/shared/assets/user.svg"
        alt=""
      />
    </span>
    <span class="photo-select__edit">
      <img
        src="./assets/pencil.svg"
        alt=""
      />
    </span>
    <input
      class="photo-select__input"
      type="file"
      accept="image/*"
      aria-label="Изменить фото профиля"
      @change="onChange"
    />
  </label>
</template>

<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue';

const photo = defineModel<File | null>({ default: null });

const previewUrl = ref('');

watch(
  photo,
  (file) => {
    revokePreview();
    previewUrl.value = file ? URL.createObjectURL(file) : '';
  },
  { immediate: true },
);

onBeforeUnmount(revokePreview);

function revokePreview() {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }
}

function onChange(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0];

  if (file) {
    photo.value = file;
  }
}
</script>

<style lang="scss" scoped>
.photo-select {
  position: relative;
  display: block;

  width: 110px;
  height: 110px;

  cursor: pointer;

  &__preview {
    display: flex;
    justify-content: center;
    align-items: center;

    width: 100%;
    height: 100%;
    overflow: hidden;

    border-radius: 50%;
    background-color: var(--color-pink-150);
  }

  &__image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  &__placeholder {
    width: 56px;
    height: 72px;
  }

  &__edit {
    position: absolute;
    right: 4px;
    bottom: 4px;

    display: flex;
    justify-content: center;
    align-items: center;

    width: 18px;
    height: 18px;

    border-radius: 50%;
    background-color: var(--color-pink-300);
  }

  &__input {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip-path: inset(50%);
  }

  &:focus-within {
    outline: 2px solid var(--color-pink-600);
    outline-offset: 2px;
    border-radius: 50%;
  }
}
</style>
