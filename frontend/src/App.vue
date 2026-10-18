<template>
  <div class="messages container">
    <MessageItem
      v-for="message in MESSAGES"
      :key="message.id"
      :message="message"
    />
  </div>
  <div class="message-input-container container">
    <MessageInput />
  </div>
</template>

<script setup lang="ts">
import { MessageItem, MessageInput, SenderRole, type Message } from '@/modules/message';

const MESSAGES: Message[] = [
  { id: '1', senderRole: SenderRole.USER, text: 'Привет!', createdAt: '2026-10-16T10:00:00Z' },
  {
    id: '2',
    senderRole: SenderRole.ASSISTANT,
    text: 'Здравствуйте! **Чем могу помочь?**',
    createdAt: '2026-10-16T10:00:05Z',
  },
  {
    id: '3',
    senderRole: SenderRole.USER,
    text: 'Расскажи, что ты умеешь. Вот *пример* задания:',
    files: [{ id: 'f1', name: 'document-1.pdf', url: '/MessagesTestFiles/document-1.pdf' }],
    createdAt: '2026-10-16T10:00:20Z',
  },
  {
    id: '4',
    senderRole: SenderRole.ASSISTANT,
    text: 'Я умею:\n\n- отвечать на вопросы\n- писать тексты\n- разбирать файлы',
    createdAt: '2026-10-16T10:00:25Z',
  },
  {
    id: '5',
    senderRole: SenderRole.USER,
    text: 'Какая сегодня погода?',
    createdAt: '2026-10-16T10:01:00Z',
  },
  {
    id: '6',
    senderRole: SenderRole.ASSISTANT,
    text: 'У меня нет доступа к данным о погоде.',
    createdAt: '2026-10-16T10:01:05Z',
  },
  {
    id: '7',
    senderRole: SenderRole.USER,
    text: 'Ладно. Помоги написать письмо.',
    createdAt: '2026-10-16T10:02:00Z',
  },
  {
    id: '8',
    senderRole: SenderRole.ASSISTANT,
    text: 'Конечно! Кому и о чём нужно письмо?',
    createdAt: '2026-10-16T10:02:05Z',
  },
  {
    id: '9',
    senderRole: SenderRole.USER,
    text: 'Преподавателю, про **перенос дедлайна**. Прикладываю скриншоты.',
    files: [
      { id: 'f2', name: 'image.png', url: '/MessagesTestFiles/image.png' },
      { id: 'f3', name: 'photo.jpg', url: '/MessagesTestFiles/photo.jpg' },
    ],
    createdAt: '2026-10-16T10:02:30Z',
  },
  {
    id: '10',
    senderRole: SenderRole.ASSISTANT,
    text: 'Хорошо, вот [черновик письма](https://example.com):\n\n> Уважаемый преподаватель, прошу перенести срок сдачи…',
    files: [{ id: 'f4', name: 'notes.txt', url: '/MessagesTestFiles/notes.txt' }],
    createdAt: '2026-10-16T10:02:40Z',
  },
];
</script>

<style lang="scss" scoped>
.message-input-container {
  margin-top: 30px;
}
</style>
