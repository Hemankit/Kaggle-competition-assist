import React, { useRef, useEffect } from 'react';
import { useChat } from '../context/ChatContext';
import ChatBox from './Chatbox';
import InputBar from './InputBar';
import Header from './Header';
import SideBar from './SideBar';
import UserInfoPanel from './UserInfoPanel';

function ChatInterface() {
  const { messages } = useChat();
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  return (
    <div className="flex flex-col h-full w-full">
      <Header />
      <div className="flex flex-row flex-1 h-full">
        <SideBar />
        <UserInfoPanel />
        <div className="flex flex-col gap-4 p-4 flex-1">
          <ChatBox />
          <div ref={chatEndRef} />
          <InputBar />
        </div>
      </div>
    </div>
  );
}

export default ChatInterface;