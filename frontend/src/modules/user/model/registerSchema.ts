import { z } from 'zod';

const GROUP_PATTERN = /^\d{3}-\d{3}$/;
const MIN_PASSWORD_LENGTH = 8;

export const registerSchema = z.object({
  lastName: z.string().trim().min(1, 'Укажите фамилию'),
  firstName: z.string().trim().min(1, 'Укажите имя'),
  middleName: z.string().trim(),
  group: z.string().trim().regex(GROUP_PATTERN, 'Номер группы в формате 261-321'),
  email: z.string().trim().email('Некорректный адрес почты'),
  password: z.string().min(MIN_PASSWORD_LENGTH, `Не короче ${MIN_PASSWORD_LENGTH} символов`),
});
