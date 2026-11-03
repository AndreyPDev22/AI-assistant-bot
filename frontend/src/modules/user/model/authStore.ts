import { ref } from 'vue';
import { defineStore } from 'pinia';

import type { User } from './user';
import { userApi, type LoginPayload, type RegisterPayload } from '../api/user';

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null);
  const isAuthenticated = ref(false);

  async function login(payload: LoginPayload) {
    const response = await userApi.login(payload);
    if (response) {
      user.value = response;
      isAuthenticated.value = true;
    }
  }

  async function register(payload: RegisterPayload) {
    const response = await userApi.register(payload);
    if (response) {
      user.value = response;
      isAuthenticated.value = true;
    }
  }

  return {
    user,
    isAuthenticated,
    login,
    register,
  };
});
