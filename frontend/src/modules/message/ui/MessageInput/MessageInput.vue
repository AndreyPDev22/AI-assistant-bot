<template>
  <div
    :class="[
      'message-input',
      {
        'message-input--expanded': isExpanded,
        'message-input--recording': isRecording,
        'message-input--disabled': isDisabled,
        'message-input--has-text': text.length,
      },
    ]"
  >
    <div
      v-if="filesList.length"
      class="message-input__files"
    >
      <FilePreview
        v-for="file in filesList"
        :key="file.id"
        :file
      />
    </div>
    <div class="message-input__field">
      <template v-if="!isRecording">
        <input
          ref="fileInput"
          type="file"
          hidden
          multiple
          @change="onFileChange"
        />
        <button
          class="message-input__upload-file"
          aria-label="Добавить файл"
          @click="openFileDialog"
        >
          <img
            src="./assets/plus.svg"
            alt=""
          />
        </button>
        <textarea
          ref="textarea"
          v-model="text"
          class="message-input__input"
          rows="1"
          placeholder="Введите запрос..."
        />
      </template>
      <div class="message-input__voice">
        <div
          v-if="isRecording"
          ref="volumesContainer"
          class="message-input__voice-volumes"
        >
          <span
            v-for="(volume, index) in volumeLevelsHistory"
            :key="index"
            :class="`message-input__voice-volume message-input__voice-volume--${volume}`"
          >
          </span>
        </div>
        <button
          class="message-input__microphone"
          aria-label="Ввести голосовое сообщение"
          @click="toggleRecording"
        ></button>
      </div>
      <button
        class="message-input__send-message"
        aria-label="Отправить сообщение"
      >
        <img
          src="./assets/send.svg"
          alt=""
        />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, useTemplateRef } from 'vue';
import type { MessageFile } from '../../model';
import { useVoiceRecorder } from '../../lib/useVoiceRecorder';
import FilePreview from '../FilePreview/FilePreview.vue';

defineProps<{
  isDisabled?: boolean;
}>();

const fileInput = useTemplateRef('fileInput');
const textarea = useTemplateRef('textarea');
const volumesContainer = useTemplateRef('volumesContainer');

const text = ref('');
const filesList = ref<MessageFile[]>([]);

const { isRecording, volumeLevelsHistory, toggleRecording } = useVoiceRecorder(
  volumesContainer,
  (file) => filesList.value.push(file),
);

const isExpanded = computed(() => text.value.length || filesList.value.length);

watch(
  [text, isExpanded],
  () => {
    const el = textarea.value;

    if (!el) {
      return;
    }

    el.style.height = 'auto';
    el.style.height = `${el.scrollHeight}px`;
  },
  { flush: 'post' },
);

function openFileDialog() {
  fileInput.value?.click();
}

function onFileChange(event: Event) {
  const files = (event.target as HTMLInputElement).files;

  if (!files) {
    return;
  }

  for (const file of files) {
    filesList.value.push({
      id: crypto.randomUUID(),
      name: file.name,
      url: URL.createObjectURL(file),
    });
  }

  (event.target as HTMLInputElement).value = '';
}
</script>

<style lang="scss" scoped>
.message-input {
  width: 100%;
  padding: 10px 11px 9px 19px;

  flex-direction: column;

  border-radius: 24px;
  background-color: #eecfd2;
  box-shadow: inset 0 1px 4px 0 rgba(0, 0, 0, 0.25);

  &,
  &__files,
  &__field,
  &__voice,
  &__voice-volumes {
    display: flex;
  }

  &,
  &__files {
    gap: 10px;
  }

  &__files,
  &__field {
    flex-wrap: wrap;
  }

  &__field,
  &__voice,
  &__voice-volumes {
    align-items: center;
  }

  &__field {
    row-gap: 3px;
  }

  &__upload-file,
  &__input,
  &__microphone,
  &__send-message {
    background: none;
    border: none;
    outline: none;

    &:focus-visible {
      outline: 2px solid var(--color-pink-600);
      outline-offset: 2px;
    }
  }

  &__upload-file,
  &__microphone,
  &__send-message {
    cursor: pointer;
  }

  &__microphone,
  &__send-message {
    width: 31px;
    height: 31px;

    border-radius: 50%;
  }

  &__input,
  &__voice-volumes,
  &--recording .message-input__voice {
    flex: 1;
    min-width: 0;
  }

  &__input {
    --input-line-height: 1.7rem;

    max-height: calc(var(--input-line-height) * 5);
    margin-left: 13px;
    padding: 0;

    font: inherit;
    line-height: var(--input-line-height);

    resize: none;
    scrollbar-width: none;

    &::-webkit-scrollbar {
      width: 0;
    }

    &:focus-visible {
      outline-offset: 4px;
      border-radius: 8px;
    }

    &::placeholder {
      color: var(--color-pink-600);
    }
  }

  &__voice {
    margin-left: 12px;

    gap: 5px;
  }

  &--recording {
    padding-left: 10px;

    .message-input__voice {
      height: 33px;

      margin-left: 0;
      padding: 4px 8px 4px 12px;

      border-radius: 80px;
      background-color: #f4e2e4;
    }

    .message-input__microphone {
      background-color: #e0b9bd;
      background-image: url('./assets/microphone-play.svg');
    }
  }

  &__microphone {
    background-image: url('./assets/microphone.svg');
    background-repeat: no-repeat;
    background-position: center;
  }

  &__voice-volumes {
    justify-content: flex-end;
    gap: 2px;

    overflow: hidden;
  }

  &__voice-volume {
    width: 3px;
    flex-shrink: 0;

    border-radius: 25px;
    background-color: var(--color-pink-700);

    &--1 {
      height: 3px;
    }

    &--2 {
      height: 5px;
    }

    &--3 {
      height: 9px;
    }

    &--4 {
      height: 13px;
    }

    &--5 {
      height: 19px;
    }
  }

  &__send-message {
    margin-left: 5px;

    padding: 7px 10px;

    background-color: var(--color-pink-300);
  }

  &--has-text {
    .message-input__field {
      row-gap: 8px;
    }
  }

  &--disabled {
    pointer-events: none;
    background-color: #f6e7e8;

    .message-input__send-message {
      background-color: #ebcfd2;
    }

    .message-input__upload-file img,
    .message-input__send-message img,
    .message-input__microphone {
      filter: brightness(0) invert(30%);
    }
  }

  &--expanded {
    padding-top: 20px;

    .message-input__files,
    .message-input__input {
      margin-right: 9px;
    }

    .message-input__field {
      .message-input__input {
        order: -1;
        flex-basis: 100%;
        margin-left: 0;
      }

      .message-input__voice {
        margin-left: auto;
      }
    }
  }
}
</style>
