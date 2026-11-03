import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().trim().email('Некорректный адрес почты'),
  password: z.string().min(8, 'Введите пароль'),
});
