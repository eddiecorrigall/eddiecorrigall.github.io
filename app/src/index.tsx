import React, { ChangeEvent, useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import Chat from './components/Chat';
import { MessageDTO, MessageRole } from './dto/MessageDTO';
import { getCookie, setCookie } from './cookies';
import { listMessages, sendMessage } from './dao/chatbot';

const getConversationID = () => {
  const name = 'conversationId';
  let id = getCookie(name);
  if (id === undefined) {
      id = crypto.randomUUID();
      setCookie(name, id);
  }
  return id;
}

const ChatBotApp = (props: { api: string }) => {
  const conversationId = getConversationID();
  const [userMessageText, setUserMessageText] = useState<string>('')
  const [messages, setMessages] = useState<MessageDTO[]>([])

  useEffect(() => {
    listMessages({
      api: props.api,
      conversationId,
    })
      .then(setMessages)
      .catch((e) => alert(e))
  }, [])

  const appendMessage = (message: MessageDTO) => {
    setMessages((previousMessages) => {
      return [message, ...previousMessages]
    })
  }

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    const sanitizedUserMessageText = userMessageText.trim()
    const isUserMessageTextEmpty = sanitizedUserMessageText.length === 0
    if (isUserMessageTextEmpty) return
    const userMessage: MessageDTO = {
      conversation_id: conversationId,
      created_at: new Date(),
      text: sanitizedUserMessageText,
      role: MessageRole.USER,
    }
    appendMessage(userMessage)
    sendMessage({ api: props.api, conversationId, userMessage })
      .then((assistantMessage: MessageDTO) => {
        appendMessage(assistantMessage)
      })
      .catch((error) => {
        alert(error.message)
      })
    setUserMessageText('')
  }

  const handleUserMessageChange = (event: ChangeEvent<HTMLInputElement>) => {
    const text = event.target.value
    setUserMessageText(text)
  }

  return <Chat
    onSubmit={handleSubmit}
    onUserMessageTextChange={handleUserMessageChange}
    userMessageText={userMessageText}
    messages={messages}
    messagePlaceholder='Write a message to the assistant'
    submitLabel='Submit'
  />
}

const APPS = {
  chatbot: (options: { id: string, api: string }) => {
    const { id, api } = options;
    const container = document.getElementById(id);
    const root = createRoot(container!);
    root.render(
      <div style={{ 'width': '100%' }}>
        <ChatBotApp api={api} />
      </div>
    )
  },
};

export default APPS;
