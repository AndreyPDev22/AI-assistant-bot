import { delay, http, HttpResponse } from 'msw';
import snakecaseKeys from 'snakecase-keys';

import { SenderRole, type Message, type MessagePayload } from '@/modules/message';
import type { Chat } from '@/modules/chat';

import { MILLISECONDS_IN_DAY } from '@/shared/constants';
import { APIResponseStatus, type Envelope } from '@/shared/api/client';

const IS_RANDOM_EMPTY_CHATS_ENABLED = false;

const MOCK_CHAT_MESSAGES = new Map<string, Message[]>([
  [
    '1',
    [
      { id: '1', senderRole: SenderRole.USER, text: 'Привет!' },
      {
        id: '2',
        senderRole: SenderRole.ASSISTANT,
        text: 'Здравствуйте! **Чем могу помочь?**',
      },
      {
        id: '3',
        senderRole: SenderRole.USER,
        text: 'Расскажи, что ты умеешь. Вот *пример* задания:',
        files: [{ id: 'f1', name: 'document-1.pdf', url: '/MessagesTestFiles/document-1.pdf' }],
      },
      {
        id: '4',
        senderRole: SenderRole.ASSISTANT,
        text: 'Я умею:\n\n- отвечать на вопросы\n- писать тексты\n- разбирать файлы',
      },
      {
        id: '5',
        senderRole: SenderRole.USER,
        text: 'Какая сегодня погода?',
      },
      {
        id: '6',
        senderRole: SenderRole.ASSISTANT,
        text: 'У меня нет доступа к данным о погоде.',
      },
      {
        id: '7',
        senderRole: SenderRole.USER,
        text: 'Ладно. Помоги написать письмо.',
      },
      {
        id: '8',
        senderRole: SenderRole.ASSISTANT,
        text: 'Конечно! Кому и о чём нужно письмо?',
      },
      {
        id: '9',
        senderRole: SenderRole.USER,
        text: 'Преподавателю, про **перенос дедлайна**. Прикладываю скриншоты.',
        files: [
          { id: 'f2', name: 'image.png', url: '/MessagesTestFiles/image.png' },
          { id: 'f3', name: 'photo.jpg', url: '/MessagesTestFiles/photo.jpg' },
        ],
      },
      {
        id: '10',
        senderRole: SenderRole.ASSISTANT,
        text: 'Хорошо, вот [черновик письма](https://example.com):\n\n> Уважаемый преподаватель, прошу перенести срок сдачи…',
        files: [{ id: 'f4', name: 'notes.txt', url: '/MessagesTestFiles/notes.txt' }],
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
      },
      {
        id: '12',
        senderRole: SenderRole.ASSISTANT,
        text: 'MSW (Mock Service Worker) перехватывает HTTP-запросы и отвечает на них моками.',
      },
    ],
  ],
  [
    '3',
    [
      {
        id: '13',
        senderRole: SenderRole.USER,
        text: 'Объясни разницу между процессом и потоком',
      },
      {
        id: '14',
        senderRole: SenderRole.ASSISTANT,
        text: 'Процесс — изолированная программа со своей памятью, поток — единица выполнения внутри процесса, потоки делят память.',
      },
      {
        id: '15',
        senderRole: SenderRole.USER,
        text: 'А что быстрее создаётся?',
      },
      {
        id: '16',
        senderRole: SenderRole.ASSISTANT,
        text: '**Поток** — он не требует выделения отдельного адресного пространства.',
      },
    ],
  ],
  [
    '4',
    [
      {
        id: '17',
        senderRole: SenderRole.USER,
        text: 'Напиши письмо преподавателю о переносе дедлайна',
      },
      {
        id: '18',
        senderRole: SenderRole.ASSISTANT,
        text: 'Уважаемый преподаватель, прошу перенести срок сдачи лабораторной работы на неделю в связи с болезнью.',
      },
      {
        id: '19',
        senderRole: SenderRole.USER,
        text: 'Сделай тон более формальным',
      },
      {
        id: '20',
        senderRole: SenderRole.ASSISTANT,
        text: 'Уважаемый Иван Петрович! Прошу рассмотреть возможность переноса срока сдачи лабораторной работы на одну неделю по причине болезни. Справку прилагаю.',
      },
    ],
  ],
  [
    '5',
    [
      {
        id: '21',
        senderRole: SenderRole.USER,
        text: 'Что такое MSW и зачем он нужен?',
      },
      {
        id: '22',
        senderRole: SenderRole.ASSISTANT,
        text: 'MSW перехватывает HTTP-запросы в браузере и отвечает на них моками, чтобы разрабатывать фронтенд без бэкенда.',
      },
      {
        id: '23',
        senderRole: SenderRole.USER,
        text: 'Он работает и в тестах?',
      },
      {
        id: '24',
        senderRole: SenderRole.ASSISTANT,
        text: 'Да, MSW можно подключать в Node.js через `setupServer` и использовать в unit-тестах.',
      },
    ],
  ],
  [
    '6',
    [
      {
        id: '25',
        senderRole: SenderRole.USER,
        text: 'Подскажи, как подготовиться к собеседованию',
      },
      {
        id: '26',
        senderRole: SenderRole.ASSISTANT,
        text: 'Повторите основы языка, разберите свои проекты и подготовьте 2–3 вопроса к интервьюеру.',
      },
      {
        id: '27',
        senderRole: SenderRole.USER,
        text: 'Какие вопросы задать интервьюеру?',
      },
      {
        id: '28',
        senderRole: SenderRole.ASSISTANT,
        text: 'Например: как устроен процесс код-ревью, какой стек используется, как выглядит адаптация новых сотрудников.',
      },
    ],
  ],
  [
    '7',
    [
      {
        id: '29',
        senderRole: SenderRole.USER,
        text: 'Составь план проекта по базам данных',
      },
      {
        id: '30',
        senderRole: SenderRole.ASSISTANT,
        text: '1. Анализ предметной области. 2. ER-диаграмма. 3. Схема таблиц. 4. SQL-запросы. 5. Отчёт.',
      },
      {
        id: '31',
        senderRole: SenderRole.USER,
        text: 'Какую СУБД лучше выбрать?',
      },
      {
        id: '32',
        senderRole: SenderRole.ASSISTANT,
        text: 'Для учебного проекта подойдёт **PostgreSQL** — бесплатная, мощная и хорошо документирована.',
      },
    ],
  ],
  [
    '8',
    [
      {
        id: '33',
        senderRole: SenderRole.USER,
        text: 'Как найти производную сложной функции?',
      },
      {
        id: '34',
        senderRole: SenderRole.ASSISTANT,
        text: 'Используйте цепное правило: (f(g(x)))′ = f′(g(x)) · g′(x). Например, (sin x²)′ = 2x · cos x².',
      },
      {
        id: '35',
        senderRole: SenderRole.USER,
        text: 'Разбери ещё один пример',
      },
      {
        id: '36',
        senderRole: SenderRole.ASSISTANT,
        text: 'Для y = e^(3x) получаем y′ = e^(3x) · 3 = 3e^(3x).',
      },
    ],
  ],
  [
    '9',
    [
      {
        id: '37',
        senderRole: SenderRole.USER,
        text: 'Чем отличается let от const в JavaScript?',
      },
      {
        id: '38',
        senderRole: SenderRole.ASSISTANT,
        text: 'let позволяет переприсваивать значение, const — нет. Оба имеют блочную область видимости.',
      },
      {
        id: '39',
        senderRole: SenderRole.USER,
        text: 'А var?',
      },
      {
        id: '40',
        senderRole: SenderRole.ASSISTANT,
        text: '**var** имеет функциональную область видимости и поднимается (hoisting), поэтому в современном коде его не используют.',
      },
    ],
  ],
  [
    '10',
    [
      {
        id: '41',
        senderRole: SenderRole.USER,
        text: 'Как правильно оформить список литературы?',
      },
      {
        id: '42',
        senderRole: SenderRole.ASSISTANT,
        text: 'Источники указывают в порядке упоминания: автор, название, город, издательство, год, число страниц.',
      },
      {
        id: '43',
        senderRole: SenderRole.USER,
        text: 'Как оформить электронный ресурс?',
      },
      {
        id: '44',
        senderRole: SenderRole.ASSISTANT,
        text: 'Укажите автора, название, режим доступа (URL) и дату обращения: *URL: https://example.com (дата обращения: 01.10.2026)*.',
      },
    ],
  ],
  [
    '11',
    [
      {
        id: '45',
        senderRole: SenderRole.USER,
        text: 'Расскажи про принципы SOLID',
      },
      {
        id: '46',
        senderRole: SenderRole.ASSISTANT,
        text: 'SOLID — пять принципов ООП: единственная ответственность, открытость/закрытость, подстановка Лисков, разделение интерфейсов, инверсия зависимостей.',
      },
      {
        id: '47',
        senderRole: SenderRole.USER,
        text: 'Приведи пример для первого принципа',
      },
      {
        id: '48',
        senderRole: SenderRole.ASSISTANT,
        text: 'Класс `Report` не должен и формировать отчёт, и сохранять его в файл — это две разные ответственности.',
      },
    ],
  ],
  [
    '12',
    [
      {
        id: '49',
        senderRole: SenderRole.USER,
        text: 'Как подготовиться к защите диплома?',
      },
      {
        id: '50',
        senderRole: SenderRole.ASSISTANT,
        text: 'Сделайте презентацию на 10–12 слайдов, отрепетируйте доклад на 7 минут и продумайте ответы на вопросы комиссии.',
      },
      {
        id: '51',
        senderRole: SenderRole.USER,
        text: 'Что должно быть на первом слайде?',
      },
      {
        id: '52',
        senderRole: SenderRole.ASSISTANT,
        text: 'Тема работы, ФИО автора и руководителя, название университета и кафедры.',
      },
    ],
  ],
  [
    '13',
    [
      {
        id: '53',
        senderRole: SenderRole.USER,
        text: 'Объясни, что такое нормализация базы данных',
      },
      {
        id: '54',
        senderRole: SenderRole.ASSISTANT,
        text: 'Нормализация — разбиение таблиц для устранения дублирования данных. Обычно достаточно третьей нормальной формы.',
      },
      {
        id: '55',
        senderRole: SenderRole.USER,
        text: 'Что требует 3НФ?',
      },
      {
        id: '56',
        senderRole: SenderRole.ASSISTANT,
        text: 'Чтобы все неключевые атрибуты зависели **только от ключа** и не зависели друг от друга.',
      },
    ],
  ],
  [
    '14',
    [
      {
        id: '57',
        senderRole: SenderRole.USER,
        text: 'Как работает Git rebase?',
      },
      {
        id: '58',
        senderRole: SenderRole.ASSISTANT,
        text: 'rebase переносит ваши коммиты поверх другой ветки, делая историю линейной. Не используйте его для уже опубликованных веток.',
      },
      {
        id: '59',
        senderRole: SenderRole.USER,
        text: 'Чем он отличается от merge?',
      },
      {
        id: '60',
        senderRole: SenderRole.ASSISTANT,
        text: 'merge создаёт отдельный коммит слияния и сохраняет историю как есть, rebase переписывает историю.',
      },
    ],
  ],
  [
    '15',
    [
      {
        id: '61',
        senderRole: SenderRole.USER,
        text: 'Помоги выбрать тему для реферата по информатике',
      },
      {
        id: '62',
        senderRole: SenderRole.ASSISTANT,
        text: 'Подойдут темы: «Нейронные сети в образовании», «Основы кибербезопасности», «История развития интернета».',
      },
      {
        id: '63',
        senderRole: SenderRole.USER,
        text: 'Расскажи подробнее про кибербезопасность',
      },
      {
        id: '64',
        senderRole: SenderRole.ASSISTANT,
        text: 'Можно раскрыть виды угроз, основы шифрования, двухфакторную аутентификацию и правила безопасного поведения в сети.',
      },
    ],
  ],
  [
    '16',
    [
      {
        id: '65',
        senderRole: SenderRole.USER,
        text: 'Как рассчитать стипендию и надбавки?',
      },
      {
        id: '66',
        senderRole: SenderRole.ASSISTANT,
        text: 'Размер зависит от результатов сессии. Точные суммы уточняйте в положении о стипендиях вашего университета.',
      },
      {
        id: '67',
        senderRole: SenderRole.USER,
        text: 'Когда её начисляют?',
      },
      {
        id: '68',
        senderRole: SenderRole.ASSISTANT,
        text: 'Обычно выплаты начинаются со следующего месяца после окончания сессии.',
      },
    ],
  ],
  [
    '17',
    [
      {
        id: '69',
        senderRole: SenderRole.USER,
        text: 'Переведи на английский: «Прошу продлить срок сдачи»',
      },
      {
        id: '70',
        senderRole: SenderRole.ASSISTANT,
        text: 'I kindly ask you to extend the submission deadline.',
      },
      {
        id: '71',
        senderRole: SenderRole.USER,
        text: 'А более формально?',
      },
      {
        id: '72',
        senderRole: SenderRole.ASSISTANT,
        text: 'I would be grateful if you could grant an extension of the submission deadline.',
      },
    ],
  ],
]);

function daysAgo(days: number) {
  return new Date(Date.now() - days * MILLISECONDS_IN_DAY).toISOString();
}

function createMockChat(
  id: string,
  createdAt: string,
  updatedAt: string,
  isFavorite = false,
): Chat {
  const messages = MOCK_CHAT_MESSAGES.get(id) ?? [];

  return { id, messages, createdAt, updatedAt, isFavorite };
}

const MOCK_CHATS: Chat[] = [
  createMockChat('1', daysAgo(0.1), daysAgo(0.1), true),
  createMockChat('2', daysAgo(0.2), daysAgo(0.2)),
  createMockChat('3', daysAgo(1.2), daysAgo(1.2)),
  createMockChat('4', daysAgo(3), daysAgo(3)),
  createMockChat('5', daysAgo(15), daysAgo(0.3)),
  createMockChat('6', daysAgo(120), daysAgo(120)),
  createMockChat('7', daysAgo(500), daysAgo(500)),
  createMockChat('8', daysAgo(0.5), daysAgo(0.5), true),
  createMockChat('9', daysAgo(0.7), daysAgo(0.7)),
  createMockChat('10', daysAgo(1.5), daysAgo(1.5)),
  createMockChat('11', daysAgo(2.3), daysAgo(2.3)),
  createMockChat('12', daysAgo(5), daysAgo(5), true),
  createMockChat('13', daysAgo(9), daysAgo(9)),
  createMockChat('14', daysAgo(22), daysAgo(1.8)),
  createMockChat('15', daysAgo(45), daysAgo(45)),
  createMockChat('16', daysAgo(200), daysAgo(200)),
  createMockChat('17', daysAgo(400), daysAgo(400)),
];

function sortMockChats() {
  MOCK_CHATS.sort((a, b) => {
    return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
  });
}

sortMockChats();

export const chatApiHandlers = [
  http.get('/api/chats', async () => {
    await delay(500);

    const response: Envelope<unknown> = {
      data: IS_RANDOM_EMPTY_CHATS_ENABLED
        ? []
        : MOCK_CHATS.filter((chat) => chat.messages.length).map((chat) => {
            return snakecaseKeys({ ...chat }, { deep: true });
          }),
      error: null,
    };
    return HttpResponse.json(response);
  }),

  http.post('/api/chats', async () => {
    await delay(500);

    const now = new Date().toISOString();
    const chat = createMockChat(crypto.randomUUID(), now, now);

    MOCK_CHAT_MESSAGES.set(chat.id, chat.messages);
    MOCK_CHATS.unshift(chat);

    const response: Envelope<unknown> = {
      data: snakecaseKeys({ ...chat }, { deep: true }),
      error: null,
    };

    return HttpResponse.json(response, { status: APIResponseStatus.CREATED });
  }),

  http.get('/api/chats/:chatId/messages', async ({ params }) => {
    const chatId = String(params.chatId);
    const messages = MOCK_CHAT_MESSAGES.get(chatId);

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

    const response: Envelope<unknown> = {
      data: messages.map((message) => {
        return snakecaseKeys({ ...message }, { deep: true });
      }),
      error: null,
    };
    return HttpResponse.json(response);
  }),

  http.post('/api/chats/:chatId/messages', async ({ params, request }) => {
    const chatId = String(params.chatId);
    const messages = MOCK_CHAT_MESSAGES.get(chatId);

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

    const body = (await request.json().catch(() => {
      return null;
    })) as MessagePayload | null;
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
    };

    messages.push(message);

    const chat = MOCK_CHATS.find((mockChat) => {
      return mockChat.id === chatId;
    });
    if (chat) {
      chat.updatedAt = new Date().toISOString();
      sortMockChats();
    }

    const response: Envelope<unknown> = {
      data: snakecaseKeys({ ...message }, { deep: true }),
      error: null,
    };

    return HttpResponse.json(response, { status: APIResponseStatus.CREATED });
  }),
];
