export enum AppLanguage {
  RU = 'ru',
  EN = 'en',
  CH = 'ch',
}

export enum AppNotifications {
  ON = 'on',
  OFF = 'off',
}

export enum AppTheme {
  LIGHT = 'light',
  DARK = 'dark',
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
