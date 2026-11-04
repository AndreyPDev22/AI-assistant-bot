import { computed, ref } from 'vue';
import { defineStore } from 'pinia';

import type { User } from './user';
import { userApi, type LoginPayload, type RegisterPayload } from '../api/user';

import DEFAULT_USER_IMAGE from '@/shared/assets/user.svg';

export const useUserStore = defineStore('auth', () => {
  const user = ref<User | null>(null);
  const isAuthenticated = ref(false);

  const profilePhoto = computed(() => user.value?.photoUrl ?? DEFAULT_USER_IMAGE);
  const fullName = computed(() => {
    const nameParts = [];

    if (user.value?.lastName) {
      nameParts.push(user.value.lastName);
    }
    if (user.value?.firstName) {
      nameParts.push(user.value.firstName);
    }

    const fullName = nameParts.join(' ');
    return fullName || 'Гость';
  });

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

  async function logout() {
    await userApi.logout();

    user.value = null;
    isAuthenticated.value = false;
  }

  return {
    user,
    fullName,
    profilePhoto,
    isAuthenticated,
    login,
    register,
    logout,
  };
});
