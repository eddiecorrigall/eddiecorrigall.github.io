import React, { useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import ChatBot from './components/ChatBot';

const ChatBotApp = () => {
  useEffect(() => {
    console.log('ChatBot rendered');
  });

  return <ChatBot
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
      <div style={{ 'width': '500px' }}>
        <ChatBotApp />
      </div>
    )
  },
};

export default APPS;
