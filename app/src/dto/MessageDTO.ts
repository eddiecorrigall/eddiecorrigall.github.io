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
    role: unsafeObject.role === 'user' ? MessageRole.USER : MessageRole.ASSISTANT,
    text: unsafeObject.text.trim(),
  }
}
