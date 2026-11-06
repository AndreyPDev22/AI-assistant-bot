import { z } from 'zod';

import { i18n } from '@/shared/i18n';

const GROUP_PATTERN = /^(\d{3}|\d{2}[АA])-\d{3,4}$/;

export const registerSchema = z.object({
  lastName: z.string().trim().min(1, i18n.global.t('auth.registrationForm.fields.lastName.error')),
  firstName: z
    .string()
    .trim()
    .min(1, i18n.global.t('auth.registrationForm.fields.firstName.error')),
  middleName: z.string().trim(),
  group: z
    .string()
    .trim()
    .regex(GROUP_PATTERN, i18n.global.t('auth.registrationForm.fields.group.error')),
  email: z.string().trim().email(i18n.global.t('auth.registrationForm.fields.email.error')),
  password: z.string().min(8, i18n.global.t('auth.registrationForm.fields.password.error')),
});
