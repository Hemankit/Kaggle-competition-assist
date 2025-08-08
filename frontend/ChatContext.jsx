import React, { createContext, useContext, useState } from 'react';
import axios from 'axios';

// Create the context
const ChatContext = createContext();

// Custom hook for easier access
export const useChat = () => useContext(ChatContext);

// Provider component
export const ChatProvider = ({ children }) => {
  const [username, setUsername] = useState('');
  const [competitionName, setCompetitionName] = useState('');
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Placeholder for saved chats (can later be fetched from backend/localStorage)
  const [savedChats, setSavedChats] = useState([]);

  const sendMessage = async () => {
    if (!query.trim()) return;

    const userMessage = {
      sender: 'User',
      content: query,
      timestamp: Date.now(),
    };

    setMessages(prev => [...prev, userMessage]);
    setQuery('');
    setIsLoading(true);

    try {
      const res = await axios.post('http://localhost:5000/multi-agent/', {
        query,
        query_type: 'reasoning', // or 'expert' depending on routing logic
      });

      const assistantMessage = {
        sender: 'Assistant',
        content: res.data?.response?.text || 'No response',
        timestamp: Date.now(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = {
        sender: 'Assistant',
        content: 'Error: Unable to fetch response.',
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Placeholder methods for future logic (sidebar integration)
  const selectChat = (chatId) => {
    console.log("Selected chat:", chatId);
    // Load selected chat messages into `messages`
    // For now, mock behavior:
    const chat = savedChats.find(chat => chat.id === chatId);
    if (chat) {
      setMessages(chat.messages || []);
    }
  };

  const newChat = () => {
    const newChatObj = {
      id: Date.now(),
      title: `Chat ${savedChats.length + 1}`,
      messages: [],
    };
    setSavedChats(prev => [...prev, newChatObj]);
    setMessages([]); // Start with empty chat
  };

  return (
    <ChatContext.Provider
      value={{
        username,
        setUsername,
        competitionName,
        setCompetitionName,
        query,
        setQuery,
        messages,
        setMessages,
        isLoading,
        sendMessage,
        savedChats,
        selectChat,
        newChat,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};