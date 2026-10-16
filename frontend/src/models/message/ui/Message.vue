<template>
  <div :class="['message', { 'message--assistant': message.senderRole === SenderRole.ASSISTANT }]">
    <div
      v-if="message.files"
      class="message__files"
    >
      <a
        v-for="file in message.files"
        :key="file.id"
        :href="file.url"
        download
        :class="[
          'file',
          { 'file--image': isImage(file.extension), 'file--is-pdf': isPdf(file.extension) },
        ]"
        :style="{ backgroundImage: pdfPreviews[file.id] ? `url(${pdfPreviews[file.id]})` : '' }"
      >
        <img
          v-if="isImage(file.extension)"
          class="file__preview"
          :src="file.url"
          alt=""
        />
        <div class="file__info">
          <p class="file__name">{{ file.name }}</p>
          <span class="file__extension">{{ file.extension }}</span>
        </div>
      </a>
    </div>
    <div
      class="message__content"
      v-html="html"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
import { marked } from 'marked';

import { SenderRole, type Message } from '../model';
import { getPdfPreview } from '../lib/pdfPreview';

const PDF_EXTENSION = 'pdf';

const IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp', 'avif'];

const { message } = defineProps<{
  message: Message;
}>();

const html = computed(() => marked.parse(message.text, { async: false, breaks: true }));

const pdfPreviews = ref<Record<string, string>>({});

onMounted(() => {
  message.files?.forEach(async (file) => {
    if (!isPdf(file.extension)) return;

    let src: string | undefined;
    try {
      src = await getPdfPreview(file.url);
    } catch {
      src = undefined;
    }

    if (src) {
      pdfPreviews.value[file.id] = src;
    }
  });
});

function isPdf(extension: string): boolean {
  return extension === PDF_EXTENSION;
}

function isImage(extension: string): boolean {
  return IMAGE_EXTENSIONS.includes(extension.toLowerCase());
}
</script>

<style lang="scss" scoped>
.message {
  display: flex;
  flex-direction: column;
  gap: 10px;

  margin-left: auto;

  width: max-content;
  max-width: calc(100% - 10px);

  &__content {
    padding: 10px 20px;
    border-radius: 6px;

    line-height: 1.5;
    overflow-wrap: anywhere;

    > :deep(:first-child) {
      margin-top: 0;
    }

    > :deep(:last-child) {
      margin-bottom: 0;
    }

    :deep(p),
    :deep(ul),
    :deep(ol),
    :deep(blockquote),
    :deep(pre),
    :deep(table),
    :deep(hr) {
      margin: 0 0 0.75em;
    }

    :deep(h1),
    :deep(h2),
    :deep(h3),
    :deep(h4),
    :deep(h5),
    :deep(h6) {
      margin: 1em 0 0.5em;
      font-weight: 600;
      line-height: 1.25;
    }

    :deep(h1) {
      font-size: 1.5em;
    }
    :deep(h2) {
      font-size: 1.3em;
    }
    :deep(h3) {
      font-size: 1.15em;
    }
    :deep(h4),
    :deep(h5),
    :deep(h6) {
      font-size: 1em;
    }

    :deep(strong),
    :deep(b) {
      font-weight: 600;
    }

    :deep(em),
    :deep(i) {
      font-style: italic;
    }

    :deep(del),
    :deep(s) {
      text-decoration: line-through;
    }

    :deep(a) {
      color: #2563eb;
      text-decoration: underline;
      text-underline-offset: 2px;
    }

    :deep(ul),
    :deep(ol) {
      padding-left: 1.5em;
    }

    :deep(ul) {
      list-style: disc;
    }

    :deep(ol) {
      list-style: decimal;
    }

    :deep(li) {
      margin: 0.25em 0;
    }

    :deep(li > ul),
    :deep(li > ol) {
      margin: 0.25em 0 0;
    }

    :deep(ul ul) {
      list-style: circle;
    }

    :deep(blockquote) {
      padding: 0.25em 1em;
      border-left: 4px solid #d1d5db;
      color: #4b5563;
    }

    :deep(code) {
      padding: 0.15em 0.4em;
      border-radius: 4px;
      background-color: #f3f4f6;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 0.9em;
    }

    :deep(pre) {
      padding: 12px 16px;
      border-radius: 6px;
      background-color: #f3f4f6;
      overflow-x: auto;
    }

    :deep(pre code) {
      padding: 0;
      background: none;
      font-size: 0.875em;
    }

    :deep(hr) {
      border: 0;
      border-top: 1px solid #d1d5db;
    }

    :deep(table) {
      display: block;
      max-width: 100%;
      overflow-x: auto;
      border-collapse: collapse;
    }

    :deep(th),
    :deep(td) {
      padding: 6px 12px;
      border: 1px solid #d1d5db;
      text-align: left;
    }

    :deep(th) {
      background-color: #f3f4f6;
      font-weight: 600;
    }

    :deep(img) {
      max-width: 100%;
      height: auto;
    }
  }

  &__files {
    display: flex;
    justify-content: flex-end;
    gap: 10px;

    width: calc(100% - 10px);
  }

  .file {
    position: relative;

    display: grid;
    place-items: center;

    width: 120px;
    height: 120px;

    border: 1px solid gray;
    border-radius: 6px;

    text-decoration: none;

    &__extension {
      position: absolute;
      left: 20px;
      bottom: 10px;
      padding: 4px 8px;

      background-color: gray;
      border-radius: 2px;
    }

    &__preview {
      width: 100%;
      height: auto;
    }

    &--is-pdf {
      background-size: cover;
      background-position: top;
      background-repeat: no-repeat;
    }

    &--image {
      width: 100%;
      height: auto;

      .file__info {
        display: none;
      }
    }
  }

  &--assistant {
    margin-left: 0;
    margin-right: auto;

    .message__files {
      justify-content: flex-start;
    }
  }
}
</style>
