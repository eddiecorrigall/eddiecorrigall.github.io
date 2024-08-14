import React, { useEffect } from 'react';
import { createRoot } from 'react-dom/client';

const ChatBotApp: React.FC = () => {
  useEffect(() => {
    console.log('rendered');
  });

  return <p>Hello world!</p>
}

const APPS = {
  chatbot: (options: { id: string, api: string }) => {
    const { id, api } = options;
    const container = document.getElementById(id);
    const root = createRoot(container!);
    root.render(<ChatBotApp />);
  },
};

export default APPS;
