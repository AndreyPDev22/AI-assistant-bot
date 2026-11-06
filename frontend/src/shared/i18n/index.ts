import { createI18n } from 'vue-i18n';

import ru from './locales/ru';
import en from './locales/en';
import zh from './locales/zh';

export const i18n = createI18n({
  legacy: false,
  locale: 'ru',
  fallbackLocale: 'ru',
  messages: {
    ru,
    en,
    zh,
  },
});
