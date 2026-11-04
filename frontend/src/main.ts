import { createApp } from 'vue';
import { createPinia } from 'pinia';

import { useAuthStore } from '@/modules/user';

import { router } from './router';
import { setupMocks } from './mocks';
import App from './App.vue';
import 'vue3-toastify/dist/index.css';
import './styles/style.scss';

async function mountApp() {
  if (import.meta.env.VITE_USE_API_MOCK === 'true') {
    await setupMocks();
  }

  const pinia = createPinia();
  const app = createApp(App).use(pinia).use(router);
  if (import.meta.env.VITE_USE_API_MOCK !== 'true') {
    try {
      await useAuthStore(pinia).restoreSession();
    } catch (error) {
      console.error('Не удалось восстановить сессию', error);
    }
  }
  app.mount('#app');
}

mountApp();
