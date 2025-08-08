import React from 'react';

// MessageBubble component for a single chat message
function MessageBubble({ sender, content, timestamp }) {
  const isUser = sender === 'User';
  const bubbleStyle = {
    background: isUser ? '#d0eaff' : '#f0f0f0',
    color: '#222',
    borderRadius: '18px',
    padding: '12px 18px',
    margin: '8px 0',
    alignSelf: isUser ? 'flex-end' : 'flex-start',
    maxWidth: '70%',
    boxShadow: '0 1px 3px rgba(0,0,0,0.07)',
    position: 'relative',
    wordBreak: 'break-word',
  };
  const timeStyle = {
    fontSize: '0.8em',
    color: '#888',
    marginTop: '6px',
    textAlign: isUser ? 'right' : 'left',
  };
  return (
    <div style={bubbleStyle}>
      <div>{content}</div>
      <div style={timeStyle}>{new Date(timestamp).toLocaleTimeString()}</div>
    </div>
  );
}

export default MessageBubble;