import { useLocalStorage } from '@vueuse/core';
import { AppTheme } from './../config/appTheme';

const savedTheme = useLocalStorage<AppTheme>('theme', AppTheme.LIGHT);

export function applyTheme(theme: AppTheme) {
  savedTheme.value = theme;
  document.documentElement.dataset.theme = theme;
}

export function initTheme() {
  document.documentElement.dataset.theme = savedTheme.value;
}
