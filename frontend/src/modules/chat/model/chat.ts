import type { Message } from '@/modules/message';

export interface Chat {
  id: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
  isFavorite: boolean;
}
