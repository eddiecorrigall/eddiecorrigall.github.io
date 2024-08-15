import React, { useState, FormEvent, ChangeEvent } from 'react'
import SubmitText from './SubmitText'
import * as styles from './Chat.module.css'

interface DocumentDTO {
}

interface MessageDTO {
  conversation_id: string,
  created_at: Date,
  text: string;
  role: 'user' | 'assistant',
  documents?: DocumentDTO[],
}

const Chat = (props: {
  messagePlaceholder: string,
  submitLabel: string,
}) => {
  const conversation_id = 'abc123'; // TODO: get this from cookie
  const [messages, setMessages] = useState<MessageDTO[]>([
    { conversation_id, created_at: new Date(), role: 'user', text: 'Its Eddie' },
    { conversation_id, created_at: new Date(), role: 'assistant', text: 'New phone, who dis?' },
    { conversation_id, created_at: new Date(), role: 'user', text: 'Hello?' },
    { conversation_id, created_at: new Date(), role: 'user', text: 'Hello!' },
  ])
  const [userMessage, setUserMessage] = useState<string>('')

  const handleUserMessageChange = (event: ChangeEvent<HTMLInputElement>) => {
    const text = event.target.value
    setUserMessage(text)
  }

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    const sanitizedUserMessage = userMessage.trim()
    if (sanitizedUserMessage === '') return
    const newMessage: MessageDTO = {
      conversation_id,
      created_at: new Date(),
      text: sanitizedUserMessage,
      role: 'user',
    }
    setMessages([newMessage, ...messages]) // append to front
    // TODO: http request to API
    setUserMessage('')
  }

  const classNames = (styles as any);
  const messageClassName = classNames.message
  const getRoleClassName = (message: MessageDTO) => {
    return message.role === 'user'
      ? classNames.user
      : classNames.assistant
  }
  return <div className={(styles as any).container}>
    <SubmitText
      onSubmit={handleSubmit}
      onChange={handleUserMessageChange}
      value={userMessage}
      placeholder={props.messagePlaceholder}
      buttonLabel={props.submitLabel}
    />
    <div className={(styles as any).messages}>
      {messages.map((message, index) => (
        <p
          key={index}
          data-time={message.created_at.toLocaleTimeString()}
          className={`${messageClassName} ${getRoleClassName(message)}`}>
          {message.text}
        </p>
      ))}
    </div>
  </div>
};

export default Chat
