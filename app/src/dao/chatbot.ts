import { MessageDTO, toMessageDTO } from '../dto/MessageDTO'
import { STATUS_CODE } from './http';

export const sendMessage = async (
  request: {
    api: string,
    conversationId: string,
    userMessage: MessageDTO,
  }
): Promise<MessageDTO> => {
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
    const assistantMessage = toMessageDTO(responseJSON)
    return assistantMessage
  }
  if (response.status === STATUS_CODE.TooManyRequests) {
    throw new Error('Too many requests, please try again later.')
  }
  throw new Error('Something went wrong...')
}

export const listMessages = async (
  request: {
    api: string,
    conversationId: string,
  },
): Promise<MessageDTO[]> => {
  const response = await fetch(`${request.api}/chatbot/conversation/${request.conversationId}`, {
    method: 'GET',
  })
  if (response.ok) {
    const responseJSON = await response.json()
    return responseJSON.map(toMessageDTO)
  }
  if (response.status === STATUS_CODE.TooManyRequests) {
    throw new Error('Too many requests, please try again later.')
  }
  throw new Error('Something went wrong...')
}
