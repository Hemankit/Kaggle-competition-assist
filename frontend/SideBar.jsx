import React, { useContext } from 'react';
import { ChatContext } from '../context/ChatContext'; // update path if different

function Sidebar() {
  const {
    username,
    setUsername,
    competitionName,
    setCompetitionName,
    savedChats,
    selectChat,
    newChat
  } = useContext(ChatContext);

  return (
    <div className="w-64 bg-gray-100 h-full flex flex-col p-4 border-r">
      {/* User Info */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-2">User Info</h2>
        <label className="block text-sm mb-1">Kaggle Username</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full p-2 rounded border text-sm"
          placeholder="Your Kaggle name"
        />
        <label className="block text-sm mt-4 mb-1">Competition</label>
        <input
          type="text"
          value={competitionName}
          onChange={(e) => setCompetitionName(e.target.value)}
          className="w-full p-2 rounded border text-sm"
          placeholder="Competition name"
        />
      </div>

      {/* Saved Chats */}
      <div className="flex-1 overflow-y-auto">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-md font-medium">Saved Chats</h3>
          <button
            onClick={newChat}
            className="text-sm text-blue-600 hover:underline"
          >
            + New
          </button>
        </div>
        {savedChats.length === 0 ? (
          <p className="text-sm text-gray-500">No saved chats.</p>
        ) : (
          <ul className="space-y-2">
            {savedChats.map((chat, index) => (
              <li
                key={index}
                className="cursor-pointer p-2 bg-white rounded hover:bg-blue-100 text-sm"
                onClick={() => selectChat(chat.id)}
              >
                {chat.title || `Chat ${index + 1}`}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default Sidebar;