<template>
  <section class="user-profile">
    <PhotoSelect
      v-model="photo"
      :preview="profilePhoto"
      class="user-profile__photo"
    />
    <h3 class="user-profile__name">{{ fullName }}</h3>
    <dl class="user-profile__settings">
      <div class="user-profile__setting">
        <dt>{{ $t('profile.language') }}</dt>
        <dd>
          <BaseSelect
            v-model="settings.language"
            :options="LANGUAGE_OPTIONS"
          />
        </dd>
      </div>
      <div class="user-profile__setting">
        <dt>{{ $t('profile.notifications') }}</dt>
        <dd>
          <BaseSwitch
            v-model="settings.notifications"
            :on-value="AppNotifications.ON"
            :off-value="AppNotifications.OFF"
          />
        </dd>
      </div>
      <div class="user-profile__setting">
        <dt>{{ $t('profile.theme') }}</dt>
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
      {{ $t('auth.logout') }}
    </BaseBtn>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { toast } from 'vue3-toastify';

import {
  BaseBtn,
  BaseSelect,
  BaseSwitch,
  BtnSize,
  BtnVariant,
  PhotoSelect,
  type SelectOption,
} from '@/shared/ui';
import { i18n } from '@/shared/i18n';
import { AppTheme } from '@/shared/config/appTheme';

import { useUserStore } from '../../model/userStore';
import { AppLanguage, AppNotifications } from '../../model/user';
import type { UserSettings } from '../../model/user';

import DARK_THEME_ICON from './assets/dark-theme.svg';
import LIGHT_THEME_ICON from './assets/light-theme.svg';

defineEmits<{
  close: [];
}>();

const { t } = useI18n();
const { user, profilePhoto, fullName, logout, updateSettings, updatePhoto } = useUserStore();

if (!user) {
  throw new Error('Пользователь не авторизован');
}

const photo = ref<File | null>(null);
const settings = ref<UserSettings>({
  language: user.settings.language,
  notifications: user.settings.notifications,
  theme: user.settings.theme,
});

const LANGUAGE_OPTIONS = computed<SelectOption[]>(() => [
  { value: AppLanguage.RU, label: t('profile.languages.ru') },
  { value: AppLanguage.EN, label: t('profile.languages.en') },
  { value: AppLanguage.ZH, label: t('profile.languages.zh') },
]);

watch(
  () => settings.value.theme,
  async () => {
    try {
      await updateSettings(settings.value);
    } catch {
      toast.error('Не удалось обновить настройки');
    }
  },
);

watch(
  () => settings.value.language,
  async (newLang, oldLang) => {
    try {
      await updateSettings(settings.value);
    } catch {
      toast.error('Не удалось обновить настройки');
    }

    if (newLang !== oldLang) {
      i18n.global.locale.value = settings.value.language;
    }
  },
);

watch(
  () => settings.value.notifications,
  async (newVal, oldVal) => {
    try {
      await updateSettings(settings.value);
    } catch {
      toast.error('Не удалось обновить настройки');
      return;
    }
    if (newVal !== oldVal && newVal === AppNotifications.ON) {
      await requestNotificationPermission();
    }
  },
);

watch(photo, async (file) => {
  if (!file) return;

  try {
    await updatePhoto(file);
  } catch {
    toast.error('Не удалось обновить фотографию');
  }
});

const requestNotificationPermission = async () => {
  if (!('Notification' in window)) {
    toast.error('Ваш браузер не поддерживает уведомления');
    return false;
  }

  if (Notification.permission === 'granted') {
    return true;
  }

  if (Notification.permission === 'denied') {
    toast.error('Разрешите уведомления в настройках браузера');
    return false;
  }

  const permission = await Notification.requestPermission();
  return permission === 'granted';
};
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
