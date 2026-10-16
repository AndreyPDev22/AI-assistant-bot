export enum SenderRole {
  USER = 'user',
  ASSISTANT = 'assistant',
}

type MessageFile = {
  id: string;
  name: string;
  extension: string;
  url: string;
};

export interface Message {
  id: string;
  senderRole: SenderRole;
  text: string;
  files?: MessageFile[];
  createdAt: string;
}
