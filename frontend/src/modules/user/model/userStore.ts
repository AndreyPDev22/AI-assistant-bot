import { computed, ref } from 'vue';
import { defineStore } from 'pinia';

import { applyTheme } from '@/shared/lib/theme';

import DEFAULT_USER_IMAGE from '@/shared/assets/user.svg';

import type { User, UserSettings } from './user';
import {
  userApi,
  type LoginPayload,
  type RegisterPayload,
  type UpdateSettingsPayload,
} from '../api/user';

export const useUserStore = defineStore('auth', () => {
  const user = ref<User | null>(null);
  const isAuthenticated = ref(false);
  const isAuthRestoring = ref(false);

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

  async function restoreAuth() {
    if (isAuthRestoring.value) return;

    isAuthRestoring.value = true;

    let response: User | undefined;

    try {
      response = await userApi.me();
    } catch {
      user.value = null;
      isAuthenticated.value = false;
    } finally {
      isAuthRestoring.value = false;
    }

    if (response) {
      user.value = response;
      isAuthenticated.value = true;
      applyTheme(response.settings.theme);
    }
  }

  async function login(payload: LoginPayload) {
    const response = await userApi.login(payload);
    if (response) {
      user.value = response;
      isAuthenticated.value = true;
      applyTheme(response.settings.theme);
    }
  }

  async function register(payload: RegisterPayload) {
    const response = await userApi.register(payload);
    if (response) {
      user.value = response;
      isAuthenticated.value = true;
      applyTheme(response.settings.theme);
    }
  }

  async function logout() {
    await userApi.logout();

    user.value = null;
    isAuthenticated.value = false;
  }

  async function updateSettings(payload: UpdateSettingsPayload) {
    if (!user.value) {
      throw new Error('Пользователь не авторизован');
    }

    let response: UserSettings;

    try {
      response = await userApi.updateSettings(payload);
    } catch {
      throw new Error('Не удалось обновить настройки аккаунта');
    }

    if (response && user.value) {
      user.value.settings = response;

      if (payload.theme) {
        applyTheme(payload.theme);
      }
    }
  }

  async function updatePhoto(photo: File) {
    if (!user.value) {
      throw new Error('Пользователь не авторизован');
    }

    let response: User;

    try {
      response = await userApi.updatePhoto(photo);
    } catch {
      throw new Error('Не удалось обновить фотографию профиля');
    }

    if (response) {
      user.value.photoUrl = response.photoUrl;
    }
  }

  return {
    user,
    fullName,
    profilePhoto,
    isAuthenticated,
    login,
    register,
    logout,
    restoreAuth,
    updateSettings,
    updatePhoto,
  };
});
