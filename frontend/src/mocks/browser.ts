import { setupWorker } from 'msw/browser';
import { chatApiHandlers } from './handlers/chat';
import { userApiHandlers } from './handlers/user';

export const worker = setupWorker(...chatApiHandlers, ...userApiHandlers);
