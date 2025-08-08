import React from 'react';
import { useChat } from '../context/ChatContext';

function InputBar() {
  const { query, setQuery, sendMessage, isLoading } = useChat();

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') sendMessage();
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow-md flex items-center">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyPress}
        placeholder="Ask something..."
        className="flex-grow p-2 border rounded mr-2"
      />
      <button
        onClick={sendMessage}
        disabled={isLoading}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        {isLoading ? 'Sending...' : 'Send'}
      </button>
    </div>
  );
}

export default InputBar;