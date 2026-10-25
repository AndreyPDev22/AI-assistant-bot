import { delay, http, HttpResponse } from 'msw';
import snakecaseKeys from 'snakecase-keys';

import type { User } from '@/modules/user';

import { APIResponseStatus, type Envelope } from '@/shared/api/client';

const GROUP_PATTERN = /^\d{3}-\d{3}$/;
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const MIN_PASSWORD_LENGTH = 8;

const MOCK_USERS: User[] = [];

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

    const isRegistered = MOCK_USERS.some((user) => user.email === email);

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

    MOCK_USERS.push(user);

    const response: Envelope<unknown> = {
      data: snakecaseKeys({ ...user }, { deep: true }),
      error: null,
    };

    return HttpResponse.json(response, { status: APIResponseStatus.CREATED });
  }),
];
