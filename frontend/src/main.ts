import { createApp } from 'vue';
import { createPinia } from 'pinia';

import 'vue3-toastify/dist/index.css';

import { useUserStore } from '@/modules/user';

import { i18n } from '@/shared/i18n';
import { initTheme } from '@/shared/lib/theme';

import './styles/style.scss';

import App from './App.vue';

import { router } from './router';
import { setupMocks } from './mocks';

async function mountApp() {
  if (import.meta.env.VITE_USE_API_MOCK === 'true') {
    await setupMocks();
  }

  const app = createApp(App);
  const pinia = createPinia();

  app.use(pinia);

  const userStore = useUserStore(pinia);

  await userStore.restoreAuth();

  app.use(router);
  app.use(i18n);

  await router.isReady();

  initTheme();

  app.mount('#app');
}

mountApp();
