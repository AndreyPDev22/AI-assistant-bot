import { delay, http, HttpResponse } from 'msw';
import snakecaseKeys from 'snakecase-keys';

import type { User } from '@/modules/user';

import { APIResponseStatus, type Envelope } from '@/shared/api/client';

const GROUP_PATTERN = /^\d{3}-\d{3}$/;
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const MIN_PASSWORD_LENGTH = 8;

type MockAccount = { user: User; password: string };

const MOCK_ACCOUNTS: MockAccount[] = [
  {
    user: {
      id: 'demo-user',
      lastName: 'Иванов',
      firstName: 'Иван',
      middleName: '',
      group: '261-321',
      email: 'demo@example.com',
      photoUrl:
        'https://img.magnific.com/free-photo/cropped-portrait-young-handsome-boy-looking-camera-posing-isolated-green-background_155003-45249.jpg',
    },
    password: 'password123',
  },
];

function response<T>(data: T, status = APIResponseStatus.SUCCESS) {
  const body: Envelope<unknown> = {
    data: data === null ? null : snakecaseKeys(data as Record<string, unknown>, { deep: true }),
    error: null,
  };
  return HttpResponse.json(body, { status });
}

function getField(formData: FormData, name: string) {
  const value = formData.get(name);
  return typeof value === 'string' ? value.trim() : '';
}

function errorResponse(status: APIResponseStatus, message: string) {
  const response: Envelope<null> = { data: null, error: { code: status, message } };

  return HttpResponse.json(response, { status });
}

export const userApiHandlers = [
  http.post('/api/users/register', async ({ request }) => {
    await delay(500);

    const formData = await request.formData().catch(() => null);

    if (!formData) {
      return errorResponse(APIResponseStatus.UNPROCESSABLE_ENTITY, 'Некорректный формат запроса');
    }

    const lastName = getField(formData, 'last_name');
    const firstName = getField(formData, 'first_name');
    const middleName = getField(formData, 'middle_name');
    const group = getField(formData, 'group');
    const email = getField(formData, 'email').toLowerCase();
    const password = String(formData.get('password') ?? '');
    const photo = formData.get('photo');

    if (!lastName || !firstName || !group || !email || !password) {
      return errorResponse(
        APIResponseStatus.UNPROCESSABLE_ENTITY,
        'Заполните фамилию, имя, номер группы, почту и пароль',
      );
    }

    if (!GROUP_PATTERN.test(group)) {
      return errorResponse(
        APIResponseStatus.UNPROCESSABLE_ENTITY,
        'Номер группы должен быть в формате 261-321',
      );
    }

    if (!EMAIL_PATTERN.test(email)) {
      return errorResponse(APIResponseStatus.UNPROCESSABLE_ENTITY, 'Некорректный адрес почты');
    }

    if (password.length < MIN_PASSWORD_LENGTH) {
      return errorResponse(
        APIResponseStatus.UNPROCESSABLE_ENTITY,
        `Пароль должен быть не короче ${MIN_PASSWORD_LENGTH} символов`,
      );
    }

    const isRegistered = MOCK_ACCOUNTS.some((account) => account.user.email === email);

    if (isRegistered) {
      return errorResponse(
        APIResponseStatus.CONFLICT,
        'Пользователь с такой почтой уже зарегистрирован',
      );
    }

    const user: User = {
      id: crypto.randomUUID(),
      lastName,
      firstName,
      middleName,
      group,
      email,
      photoUrl: photo instanceof File ? URL.createObjectURL(photo) : null,
    };

    MOCK_ACCOUNTS.push({ user, password });
    return response(user, APIResponseStatus.CREATED);
  }),

  http.post('/api/auth/login', async ({ request }) => {
    await delay(350);
    const payload = (await request.json().catch(() => null)) as {
      email?: string;
      password?: string;
    } | null;
    const email = payload?.email?.trim().toLowerCase();
    const account = MOCK_ACCOUNTS.find(
      ({ user, password }) => user.email === email && password === payload?.password,
    );

    if (!account) {
      return errorResponse(APIResponseStatus.NOT_AUTHORIZED, 'Неверная почта или пароль');
    }

    return response(account.user);
  }),
];
