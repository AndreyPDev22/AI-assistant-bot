import { delay, http, HttpResponse } from 'msw';
import snakecaseKeys from 'snakecase-keys';

import { APIResponseStatus, type Envelope } from '@/shared/api/client';
import { SenderRole, type Message, type MessagePayload } from '@/modules/message';

const mockChatMessages = new Map<string, Message[]>([
  [
    '1',
    [
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
    ],
  ],
  [
    '2',
    [
      {
        id: '11',
        senderRole: SenderRole.USER,
        text: 'Объясни, что такое **MSW**.',
        createdAt: '2026-10-17T09:00:00Z',
      },
      {
        id: '12',
        senderRole: SenderRole.ASSISTANT,
        text: 'MSW (Mock Service Worker) перехватывает HTTP-запросы и отвечает на них моками.',
        createdAt: '2026-10-17T09:00:05Z',
      },
    ],
  ],
]);

export const chatApiHandlers = [
  http.get('/api/chats/:chatId/messages', async ({ params }) => {
    const chatId = String(params.chatId);
    const messages = mockChatMessages.get(chatId);

    await delay(500);

    if (!messages) {
      const errorResponse: Envelope<null> = {
        data: null,
        error: {
          code: APIResponseStatus.NOT_FOUND,
          message: `Чат ${chatId} не найден`,
        },
      };
      return HttpResponse.json(errorResponse, { status: APIResponseStatus.NOT_FOUND });
    }

    const isEmptyResponse = Math.random() < 0.5;
    const response: Envelope<unknown> = {
      data: isEmptyResponse
        ? []
        : messages.map((message) => snakecaseKeys({ ...message }, { deep: true })),
      error: null,
    };
    return HttpResponse.json(response);
  }),

  http.post('/api/chats/:chatId/messages', async ({ params, request }) => {
    const chatId = String(params.chatId);
    const messages = mockChatMessages.get(chatId);

    await delay(500);

    if (!messages) {
      const errorResponse: Envelope<null> = {
        data: null,
        error: {
          code: APIResponseStatus.NOT_FOUND,
          message: `Чат ${chatId} не найден`,
        },
      };
      return HttpResponse.json(errorResponse, { status: APIResponseStatus.NOT_FOUND });
    }

    const body = (await request.json().catch(() => null)) as MessagePayload | null;
    const text = typeof body?.text === 'string' ? body.text : '';

    if (!text.trim() && !body?.files?.length) {
      const errorResponse: Envelope<null> = {
        data: null,
        error: {
          code: APIResponseStatus.UNPROCESSABLE_ENTITY,
          message: 'Сообщение не может быть пустым',
        },
      };
      return HttpResponse.json(errorResponse, { status: APIResponseStatus.UNPROCESSABLE_ENTITY });
    }

    const message: Message = {
      id: crypto.randomUUID(),
      senderRole: SenderRole.USER,
      text,
      ...(body?.files?.length ? { files: body.files } : {}),
      createdAt: new Date().toISOString(),
    };

    messages.push(message);

    const response: Envelope<unknown> = {
      data: snakecaseKeys({ ...message }, { deep: true }),
      error: null,
    };

    return HttpResponse.json(response, { status: APIResponseStatus.CREATED });
  }),
];
