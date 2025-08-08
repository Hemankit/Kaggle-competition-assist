import React from 'react';
import { useChat } from '../context/ChatContext';
import MessageBubble from './MessageBubble';

function ChatBox() {
  const { messages } = useChat();

  return (
    <div className="p-4 bg-white rounded-lg shadow-md h-[400px] overflow-y-scroll">
      <h2 className="text-lg font-semibold mb-2">Chat History</h2>
      {messages.map((msg, index) => (
        <MessageBubble key={index} {...msg} />
      ))}
    </div>
  );
}

export default ChatBox;