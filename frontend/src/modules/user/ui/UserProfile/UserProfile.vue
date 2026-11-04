<template>
  <section class="user-profile">
    <PhotoSelect
      v-model="photo"
      class="user-profile__photo"
    />
    <h3 class="user-profile__name">{{ fullName }}</h3>
    <dl class="user-profile__settings">
      <div class="user-profile__setting">
        <dt>Язык</dt>
        <dd>
          <BaseSelect
            v-model="settings.language"
            :options="LANGUAGE_OPTIONS"
          />
        </dd>
      </div>
      <div class="user-profile__setting">
        <dt>Уведомления</dt>
        <dd>
          <BaseSwitch
            v-model="settings.notifications"
            :on-value="AppNotifications.ON"
            :off-value="AppNotifications.OFF"
          />
        </dd>
      </div>
      <div class="user-profile__setting">
        <dt>Тема</dt>
        <dd>
          <BaseSwitch
            v-model="settings.theme"
            :on-value="AppTheme.LIGHT"
            :off-value="AppTheme.DARK"
            :thumb-icon="LIGHT_THEME_ICON"
            :track-icon="DARK_THEME_ICON"
          />
        </dd>
      </div>
    </dl>
    <BaseBtn
      class="user-profile__logout"
      :variant="BtnVariant.OUTLINE"
      :size="BtnSize.MD"
      @click="
        () => {
          logout();
          $emit('close');
        }
      "
    >
      Выйти из аккаунта
    </BaseBtn>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

import {
  BaseBtn,
  BaseSelect,
  BaseSwitch,
  BtnSize,
  BtnVariant,
  PhotoSelect,
  type SelectOption,
} from '@/shared/ui';

import { useUserStore } from '../../model/userStore';
import { AppLanguage, AppNotifications, AppTheme } from '../../model/user';
import type { UserSettings } from '../../model/user';

import DARK_THEME_ICON from './assets/dark-theme.svg';
import LIGHT_THEME_ICON from './assets/light-theme.svg';

const LANGUAGE_OPTIONS: SelectOption[] = [
  { value: AppLanguage.RU, label: 'Русский' },
  { value: AppLanguage.EN, label: 'Английский' },
  { value: AppLanguage.CH, label: 'Китайский' },
];

defineEmits<{
  close: [];
}>();

const { user, profilePhoto, fullName, logout } = useUserStore();

if (!user) {
  throw new Error('Пользователь не авторизован');
}

const photo = ref<File | null>(null);
const settings = ref<UserSettings>({
  language: user.settings.language,
  notifications: user.settings.notifications,
  theme: user.settings.theme,
});

onMounted(async () => {
  if (!profilePhoto) {
    return;
  }

  try {
    photo.value = await urlToFile(profilePhoto, 'profile-photo');
  } catch (e) {
    console.error('Ошибка преобразования ссылки в файл:', e);
  }
});

async function urlToFile(url: string, fileName = 'photo'): Promise<File> {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Не удалось загрузить файл: ${response.status}`);
  }

  const blob = await response.blob();

  const mime = blob.type || 'image/jpeg';
  const ext = mime.split('/')[1]?.split('+')[0] || 'jpg';

  return new File([blob], `${fileName}.${ext}`, { type: mime });
}
</script>

<style lang="scss" scoped>
.user-profile {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;

  &__name {
    margin-top: 20px;

    font-size: var(--font-size-lg);
  }

  &__settings {
    width: 100%;
    margin-top: 40px;

    display: flex;
    flex-direction: column;
    gap: 25px;
  }

  &__setting {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  &__logout {
    margin-top: 35px;
  }
}
</style>
