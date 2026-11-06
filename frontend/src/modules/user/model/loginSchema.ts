import { z } from 'zod';

import { i18n } from '@/shared/i18n';

export const loginSchema = z.object({
  email: z.string().trim().email(i18n.global.t('auth.authForm.fields.email.error')),
  password: z.string().min(8, i18n.global.t('auth.authForm.fields.password.error')),
});
