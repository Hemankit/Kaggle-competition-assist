import React, { useEffect, useRef } from 'react';
import { useChat } from '../context/ChatContext';

export default function ChatPage() {
  const {
    messages,
    input,
    setInput,
    isLoading,
    error,
    submitQuery,
  } = useChat();

  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    await submitQuery(input);
    setInput('');
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-white shadow px-6 py-4 text-xl font-semibold text-gray-800">
        🧠 Kaggle Copilot
      </div>

      {/* Chat Window */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-md px-4 py-2 rounded-xl text-white text-sm ${
                msg.role === 'user'
                  ? 'bg-blue-600 rounded-br-none'
                  : 'bg-gray-700 rounded-bl-none'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-400 text-white px-4 py-2 rounded-xl text-sm animate-pulse">
              Thinking...
            </div>
          </div>
        )}

        {error && (
          <div className="text-red-500 text-sm text-center">{error}</div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <form
        onSubmit={handleSubmit}
        className="bg-white px-6 py-4 shadow flex gap-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:border-blue-400"
          placeholder="Ask me how to improve your Kaggle notebook..."
        />
        <button
          type="submit"
          disabled={isLoading}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}