import { MessageDTO, MessageRole, toMessageDTO } from '../dto/MessageDTO'
import { STATUS_CODE } from './http';

export const sendMessage = async (
  request: {
    api: string,
    conversationId: string,
    userMessage: MessageDTO,
  }
): Promise<MessageDTO> => {
  console.log(`User message: ${request.userMessage}`);
  const response = await fetch(`${request.api}/chatbot/conversation/${request.conversationId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request.userMessage),
  })
  if (response.ok) {
    // TODO: validate response body
    const responseJSON = await response.json()
    return toMessageDTO(responseJSON)
  }
  if (response.status === STATUS_CODE.TooManyRequests) {
    throw new Error('Too many requests, please try again later.');
  }
  throw new Error('Something went wrong...');
}
