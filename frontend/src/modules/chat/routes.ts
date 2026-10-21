import type { RouteRecordRaw } from 'vue-router';

export enum RouteNames {
  CHAT = 'chat',
}

export const routes: RouteRecordRaw[] = [
  {
    path: '/:chatId?',
    name: RouteNames.CHAT,
    component: () => import('./ui/Chat.vue'),
    props: true,
  },
];
