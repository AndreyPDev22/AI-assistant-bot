import { apiRequest } from '@/shared/api/client';

import type { User, UserSettings } from '../model/user';

export type UpdateSettingsPayload = Partial<UserSettings>;

export type RegisterPayload = {
  lastName: string;
  firstName: string;
  middleName: string;
  group: string;
  email: string;
  password: string;
  photo: File | null;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export const userApi = {
  me: () =>
    apiRequest<User>('/api/auth/me', {
      method: 'GET',
      credentials: 'include',
    }),

  register: (payload: RegisterPayload) => {
    const body = new FormData();

    body.append('last_name', payload.lastName);
    body.append('first_name', payload.firstName);
    body.append('middle_name', payload.middleName);
    body.append('group', payload.group);
    body.append('email', payload.email);
    body.append('password', payload.password);

    if (payload.photo) {
      body.append('photo', payload.photo);
    }

    return apiRequest<User>('/api/users/register', {
      method: 'POST',
      body,
      credentials: 'include',
    });
  },

  login: (payload: LoginPayload) =>
    apiRequest<User>('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      credentials: 'include',
    }),

  logout: () =>
    apiRequest<null>('/api/auth/logout', {
      method: 'POST',
      credentials: 'include',
    }),

  updateSettings: (payload: UpdateSettingsPayload) =>
    apiRequest<UserSettings>('/api/users/me/settings', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      credentials: 'include',
    }),

  updatePhoto: (photo: File) => {
    const body = new FormData();
    body.append('photo', photo);

    return apiRequest<User>('/api/users/me/photo', {
      method: 'PATCH',
      body,
      credentials: 'include',
    });
  },
};
