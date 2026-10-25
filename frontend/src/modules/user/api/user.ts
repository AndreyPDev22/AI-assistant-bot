import { apiRequest } from '@/shared/api/client';

import type { User } from '../model/user';

export type RegisterPayload = {
  lastName: string;
  firstName: string;
  middleName: string;
  group: string;
  email: string;
  password: string;
  photo: File | null;
};

export const userApi = {
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

    return apiRequest<User>('/api/users/register', { method: 'POST', body });
  },
};
