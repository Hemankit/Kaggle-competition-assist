import React, { createContext, useContext, useState } from 'react';
import axios from 'axios';

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const submitQuery = async (userQuery, debug = false) => {
    setIsLoading(true);
    setError(null);

    try {
      // Append user message
      setMessages((prev) => [...prev, { role: 'user', content: userQuery }]);

      const response = await axios.post('http://localhost:5000/component-orchestrator/', {
        query: userQuery,
        query_type: 'reasoning', // you can make this dynamic if needed
        debug,
      });

      const result = response.data;

      if (result.error) {
        setError(result.error);
      } else {
        const reply = result.final_response || 'No response.';
        setMessages((prev) => [...prev, { role: 'assistant', content: reply }]);

        if (debug && result.execution_trace) {
          console.log('Trace (dev only):', result.execution_trace);
        }
      }
    } catch (err) {
      console.error('Query submission error:', err);
      setError('Something went wrong while processing your query.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ChatContext.Provider
      value={{
        messages,
        input,
        setInput,
        isLoading,
        error,
        submitQuery,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => useContext(ChatContext);