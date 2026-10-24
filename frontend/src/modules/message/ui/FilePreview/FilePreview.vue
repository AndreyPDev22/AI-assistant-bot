<template>
  <div class="file">
    <a
      :href="file.url"
      class="file__link"
      download
    >
      <div class="file__info">
        <img
          :src="previewSrc"
          :class="[
            'file__preview',
            { 'file__preview--placeholder': previewSrc === BASE_FILE_IMAGE },
          ]"
          alt=""
        />
        <p class="file__name">
          <img
            :src="BASE_FILE_IMAGE"
            alt=""
          />
          <span>
            {{ file.name }}
          </span>
        </p>
      </div>
    </a>
    <button
      v-if="deletable"
      type="button"
      class="file__delete"
      aria-label="Удалить файл"
      @click="$emit('delete', file.id)"
    >
      <img
        src="./assets/close.svg"
        alt=""
      />
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';

import type { MessageFile } from '../../model/message';
import { getPdfPreview } from '../../lib/pdfPreview';

import BASE_FILE_IMAGE from './assets/file.svg';

const PDF_EXTENSION = 'pdf';
const IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp', 'avif'];

const { file, deletable = false } = defineProps<{
  file: MessageFile;
  deletable?: boolean;
}>();

defineEmits<{
  delete: [id: string];
}>();

const pdfPreview = ref<string>();

const extension = computed(() => {
  const dotIndex = file.name.lastIndexOf('.');
  return dotIndex === -1 ? '' : file.name.slice(dotIndex + 1).toLowerCase();
});
const isPdf = computed(() => extension.value === PDF_EXTENSION);
const isImage = computed(() => IMAGE_EXTENSIONS.includes(extension.value));
const previewSrc = computed(() => (isImage.value ? file.url : pdfPreview.value) || BASE_FILE_IMAGE);

onMounted(async () => {
  if (!isPdf.value) return;

  try {
    pdfPreview.value = await getPdfPreview(file.url);
  } catch {
    // Превью недоступно — остаётся иконка по умолчанию
  }
});
</script>

<style lang="scss" scoped>
.file {
  position: relative;

  place-self: center;

  width: 100px;
  height: 75px;

  &__link {
    display: flex;

    width: 100%;
    height: 100%;

    text-decoration: none;

    border: 1px solid #d3a0a5;
    border-radius: 6px;

    overflow: hidden;
  }

  &__delete {
    position: absolute;
    top: 6px;
    right: 6px;

    display: flex;
    padding: 0;

    border: none;
    background: none;

    cursor: pointer;
  }

  &__info {
    width: 100%;
    min-width: 0;

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    background-color: white;
  }

  &__name {
    width: 100%;
    height: 20px;
    padding: 4px 6px;

    display: flex;
    align-items: center;
    gap: 10px;

    font-size: 1rem;
    background-color: #d3a0a5;

    img {
      width: 7px;
      height: 9px;

      flex-shrink: 0;
    }

    span {
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;

      line-height: 1.3;
    }
  }

  &__preview {
    width: 100%;
    height: 55px;

    &--placeholder {
      object-fit: none;
    }
  }
}
</style>
