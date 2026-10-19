import { setupWorker } from 'msw/browser';
import { chatApiHandlers } from './handlers/chat';

export const worker = setupWorker(...chatApiHandlers);
