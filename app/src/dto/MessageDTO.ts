export interface DocumentDTO {
}

export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
}

export interface MessageDTO {
  conversation_id: string,
  created_at: Date,
  text: string;
  role: MessageRole,
  documents?: DocumentDTO[],
}

export const toMessageDTO = (unsafeObject: any): MessageDTO => {
  // TODO: validate
  return {
    conversation_id: unsafeObject.conversation_id,
    created_at: new Date(unsafeObject.created_at),
    documents: unsafeObject.documents,
    role: MessageRole[unsafeObject.role as keyof typeof MessageRole],
    text: unsafeObject.text.trim(),
  }
}
