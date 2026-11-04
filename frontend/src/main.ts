import { createApp } from 'vue';
import { createPinia } from 'pinia';

import { router } from './router';
import { setupMocks } from './mocks';
import App from './App.vue';
import 'vue3-toastify/dist/index.css';
import './styles/style.scss';

async function mountApp() {
  if (import.meta.env.VITE_USE_API_MOCK === 'true') {
    await setupMocks();
  }

  createApp(App).use(createPinia()).use(router).mount('#app');
}

mountApp();
