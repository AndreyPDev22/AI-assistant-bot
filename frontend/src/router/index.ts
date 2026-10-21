import { createRouter, createWebHistory } from 'vue-router';

import { routes, RouteNames } from '@/modules/chat';

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    ...routes,
    {
      path: '/:pathMatch(.*)*',
      redirect: { name: RouteNames.CHAT },
    },
  ],
});
