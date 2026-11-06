import type { AppTheme } from '@/shared/config/appTheme';

export enum AppLanguage {
  RU = 'ru',
  EN = 'en',
  ZH = 'zh',
}

export enum AppNotifications {
  ON = 'on',
  OFF = 'off',
}

export type UserSettings = {
  language: AppLanguage;
  theme: AppTheme;
  notifications: AppNotifications;
};

export interface User {
  id: string;
  lastName: string;
  firstName: string;
  middleName: string;
  group: string;
  email: string;
  photoUrl: string | null;
  settings: UserSettings;
}
